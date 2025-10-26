from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chez-meme-super-secret-key-2024-development-only')

# Configuration de la base de données
# Supporte SQLite en local et PostgreSQL en production
database_url = os.environ.get('DATABASE_URL', 'sqlite:///chez_meme.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèles de base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    guest_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(100), unique=True, nullable=False)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    distance = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))
    activity_type = db.Column(db.String(50))  # surf, vtt, randonnee, escalade
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Configuration email
EMAIL_SMTP_SERVER = os.environ.get('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.environ.get('EMAIL_SMTP_PORT', '587'))
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', 'gabriel.plomion@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'eqom nwek tkuh pvay')
EMAIL_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS', 'gabriel.plomion@gmail.com,miquel.antoine.pro@gmail.com').split(',')

def send_reservation_email(reservation):
    """Envoie un email de réservation aux administrateurs"""
    try:
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = ", ".join(EMAIL_RECIPIENTS)
        msg['Subject'] = f"Nouvelle réservation - {reservation.guest_name}"
        
        # Corps du message
        base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        approve_url = f"{base_url}/approve/{reservation.token}"
        reject_url = f"{base_url}/reject/{reservation.token}"
        
        body = f"""
{reservation.guest_name} veut réserver le canap' de chez mémé du {reservation.start_date} au {reservation.end_date}.

<a href="{approve_url}">[Demande validée]</a>
<a href="{reject_url}">[Demande non validée]</a>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connexion et envoi
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, EMAIL_RECIPIENTS, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False

# Décorateur pour vérifier l'authentification admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Accès refusé. Connexion admin requise.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calendrier')
def calendrier():
    # Récupérer les réservations approuvées pour le calendrier
    approved_reservations = Reservation.query.filter_by(status='approved').all()
    
    # Créer un dictionnaire pour faciliter l'affichage
    reservations_dict = {}
    for res in approved_reservations:
        current_date = res.start_date
        while current_date <= res.end_date:
            reservations_dict[str(current_date)] = {
                'guest_name': res.guest_name
            }
            current_date += timedelta(days=1)
    
    return render_template('calendrier.html', reservations=reservations_dict)

@app.route('/appartement')
def appartement():
    return render_template('appartement.html')

@app.route('/activites')
def activites():
    activities = Activity.query.all()
    return render_template('activites.html', activities=activities)

@app.route('/reserver', methods=['GET', 'POST'])
def reserver():
    if request.method == 'POST':
        try:
            # Créer une nouvelle réservation
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            
            # Vérifier que les dates sont valides
            if start_date >= end_date:
                return jsonify({'success': False, 'message': 'La date de fin doit être après la date de début !'})
            
            if start_date < date.today():
                return jsonify({'success': False, 'message': 'Impossible de réserver dans le passé !'})
            
            # Vérifier les conflits avec les réservations approuvées
            conflicting = Reservation.query.filter(
                Reservation.status == 'approved',
                Reservation.start_date <= end_date,
                Reservation.end_date >= start_date
            ).first()
            
            if conflicting:
                return jsonify({'success': False, 'message': f'Ces dates sont déjà réservées par {conflicting.guest_name} !'})
            
            # Générer un token unique
            token = secrets.token_urlsafe(32)
            
            # Créer la réservation
            reservation = Reservation(
                start_date=start_date,
                end_date=end_date,
                guest_name=request.form['guest_name'],
                status='pending',
                token=token
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            # Envoyer l'email
            if send_reservation_email(reservation):
                return jsonify({'success': True, 'message': 'Demande envoyée ! Vous recevrez un email de confirmation.'})
            else:
                return jsonify({'success': False, 'message': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer.'})
                
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})
    
    return render_template('reserver.html')

@app.route('/admin')
@admin_required
def admin():
    pending_reservations = Reservation.query.filter_by(status='pending').order_by(Reservation.created_at.desc()).all()
    all_reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return render_template('admin.html', 
                         pending_reservations=pending_reservations,
                         all_reservations=all_reservations)

@app.route('/approve/<token>')
def approve_reservation(token):
    reservation = Reservation.query.filter_by(token=token).first()
    if reservation and reservation.status == 'pending':
        reservation.status = 'approved'
        db.session.commit()
        return f"<h1>✅ Réservation approuvée !</h1><p>La réservation de {reservation.guest_name} du {reservation.start_date} au {reservation.end_date} a été validée.</p>"
    else:
        return "<h1>❌ Erreur</h1><p>Réservation introuvable ou déjà traitée.</p>"

@app.route('/reject/<token>')
def reject_reservation(token):
    reservation = Reservation.query.filter_by(token=token).first()
    if reservation and reservation.status == 'pending':
        reservation.status = 'rejected'
        db.session.commit()
        return f"<h1>❌ Réservation rejetée</h1><p>La réservation de {reservation.guest_name} du {reservation.start_date} au {reservation.end_date} a été rejetée.</p>"
    else:
        return "<h1>❌ Erreur</h1><p>Réservation introuvable ou déjà traitée.</p>"

@app.route('/admin/approve/<int:reservation_id>')
@admin_required
def admin_approve_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.status = 'approved'
    db.session.commit()
    flash(f'Réservation de {reservation.guest_name} approuvée !', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/reject/<int:reservation_id>')
@admin_required
def admin_reject_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.status = 'rejected'
    db.session.commit()
    flash(f'Réservation de {reservation.guest_name} rejetée.', 'info')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Connexion réussie !', 'success')
            return redirect(url_for('admin' if user.is_admin else 'index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie !', 'info')
    return redirect(url_for('index'))

# API pour récupérer les réservations (pour le calendrier JavaScript)
@app.route('/api/reservations')
def api_reservations():
    reservations = Reservation.query.filter_by(status='approved').all()
    return jsonify([{
        'id': r.id,
        'start_date': r.start_date.isoformat(),
        'end_date': r.end_date.isoformat(),
        'guest_name': r.guest_name
    } for r in reservations])

# Initialisation de la base de données
def init_db():
    with app.app_context():
        db.create_all()
        
        # Créer un admin par défaut
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@chez-meme.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
        
        # Ajouter des activités par défaut
        if Activity.query.count() == 0:
            activities = [
                Activity(
                    name='Plage de la Côte Sauvage',
                    description='Magnifique plage pour le surf avec des vagues parfaites pour débuter',
                    distance='5 km',
                    difficulty='Facile',
                    activity_type='surf',
                    image_url='/static/images/surf.jpg'
                ),
                Activity(
                    name='Forêt de Fontainebleau',
                    description='Parcours VTT dans les sentiers forestiers avec des dénivelés variés',
                    distance='15 km',
                    difficulty='Intermédiaire',
                    activity_type='vtt',
                    image_url='/static/images/vtt.jpg'
                ),
                Activity(
                    name='Sentier des Crêtes',
                    description='Randonnée panoramique avec vue sur la vallée et les montagnes',
                    distance='8 km',
                    difficulty='Facile',
                    activity_type='randonnee',
                    image_url='/static/images/randonnee.jpg'
                ),
                Activity(
                    name='Rocher de l\'Aigle',
                    description='Site d\'escalade réputé avec des voies de tous niveaux',
                    distance='12 km',
                    difficulty='Difficile',
                    activity_type='escalade',
                    image_url='/static/images/escalade.jpg'
                )
            ]
            
            for activity in activities:
                db.session.add(activity)
        
        db.session.commit()
        print("Base de données initialisée !")
        print("Admin par défaut: username='admin', password='admin123'")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
