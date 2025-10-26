from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
from functools import wraps
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chez-meme-super-secret-key-2024-development-only')

# Configuration de la base de données
# Supporte SQLite en local et PostgreSQL en production
database_url = os.environ.get('DATABASE_URL', 'sqlite:///chez_meme.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration pour le téléversement d'images
UPLOAD_FOLDER = 'static/uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Créer le dossier de téléversement s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200))
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Fonctions utilitaires pour les images
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_width=800, max_height=600):
    """Redimensionne une image en gardant les proportions"""
    try:
        with Image.open(image_path) as img:
            # Calculer les nouvelles dimensions
            ratio = min(max_width/img.width, max_height/img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            
            # Redimensionner
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Sauvegarder en écrasant l'original
            resized_img.save(image_path, optimize=True, quality=85)
            return True
    except Exception as e:
        print(f"Erreur lors du redimensionnement: {e}")
        return False

# Système simplifié - pas d'email

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
# Initialisation automatique de la base de données au démarrage
_first_request_done = False

@app.before_request
def initialize_db():
    """Crée les tables et initialise les données par défaut au premier démarrage"""
    global _first_request_done
    if not _first_request_done:
        _first_request_done = True
        db.create_all()
        print("Tables de base de données créées/vérifiées.")
        
        # Créer un admin par défaut
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@chez-meme.com',
                password_hash=generate_password_hash('On est tous dans la m3rde !'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin par défaut créé: username='admin', password='On est tous dans la m3rde !'")
        
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
            print("Activités par défaut ajoutées.")

@app.route('/')
def index():
    photos = Photo.query.order_by(Photo.display_order, Photo.created_at).all()
    return render_template('index.html', photos=photos)

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
                return jsonify({'success': False, 'message': 'Le jour de départ doit être après le jour d\'arrivée !'})
            
            if start_date < date.today():
                return jsonify({'success': False, 'message': 'Impossible de réserver dans le passé !'})
            
            # Vérifier les conflits avec les réservations approuvées
            # Logique : deux réservations se chevauchent si :
            # - La nouvelle commence avant que l'ancienne se termine ET
            # - La nouvelle se termine après que l'ancienne commence
            conflicting = Reservation.query.filter(
                Reservation.status == 'approved',
                Reservation.start_date < end_date,  # L'ancienne commence avant que la nouvelle se termine
                Reservation.end_date > start_date   # L'ancienne se termine après que la nouvelle commence
            ).first()
            
            if conflicting:
                return jsonify({'success': False, 'message': f'Ces dates sont déjà réservées par {conflicting.guest_name} !'})
            
            # Générer un token unique
            token = secrets.token_urlsafe(32)
            
            # Créer la réservation directement approuvée
            reservation = Reservation(
                start_date=start_date,
                end_date=end_date,
                guest_name=request.form['guest_name'],
                status='approved',  # Directement approuvée
                token=token
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Réservation confirmée ! Elle apparaît maintenant dans le calendrier.'})
                
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})
    
    return render_template('reserver.html')

@app.route('/admin')
@admin_required
def admin():
    all_reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return render_template('admin_dashboard.html', reservations=all_reservations)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password) and user.is_admin:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = True
            flash('Connexion réussie !', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/add', methods=['GET', 'POST'])
@admin_required
def admin_add_reservation():
    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            
            if start_date >= end_date:
                return jsonify({'success': False, 'message': 'Le jour de départ doit être après le jour d\'arrivée !'})
            
            if start_date < date.today():
                return jsonify({'success': False, 'message': 'Impossible de réserver dans le passé !'})
            
            # Vérifier les conflits
            conflicting = Reservation.query.filter(
                Reservation.status == 'approved',
                Reservation.start_date < end_date,
                Reservation.end_date > start_date
            ).first()
            
            if conflicting:
                return jsonify({'success': False, 'message': f'Ces dates sont déjà réservées par {conflicting.guest_name} !'})
            
            token = secrets.token_urlsafe(32)
            
            reservation = Reservation(
                start_date=start_date,
                end_date=end_date,
                guest_name=request.form['guest_name'],
                status=request.form['status'],
                token=token
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Réservation créée avec succès !'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})
    
    return render_template('admin_add.html')

@app.route('/admin/edit/<int:reservation_id>', methods=['POST'])
@admin_required
def admin_edit_reservation(reservation_id):
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        
        if start_date >= end_date:
            return jsonify({'success': False, 'message': 'Le jour de départ doit être après le jour d\'arrivée !'})
        
        # Vérifier les conflits (en excluant la réservation actuelle)
        conflicting = Reservation.query.filter(
            Reservation.id != reservation_id,
            Reservation.status == 'approved',
            Reservation.start_date < end_date,
            Reservation.end_date > start_date
        ).first()
        
        if conflicting:
            return jsonify({'success': False, 'message': f'Ces dates sont déjà réservées par {conflicting.guest_name} !'})
        
        reservation.guest_name = request.form['guest_name']
        reservation.start_date = start_date
        reservation.end_date = end_date
        reservation.status = request.form['status']
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Réservation modifiée avec succès !'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/admin/delete/<int:reservation_id>', methods=['DELETE'])
@admin_required
def admin_delete_reservation(reservation_id):
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        guest_name = reservation.guest_name
        
        db.session.delete(reservation)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Réservation de {guest_name} supprimée avec succès !'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

# Routes pour la gestion des photos
@app.route('/admin/photos')
@admin_required
def admin_photos():
    photos = Photo.query.order_by(Photo.display_order, Photo.created_at).all()
    return render_template('admin_photos.html', photos=photos)

@app.route('/admin/photos/upload', methods=['POST'])
@admin_required
def admin_upload_photos():
    try:
        if 'photos' not in request.files:
            return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
        
        files = request.files.getlist('photos')
        captions = request.form.getlist('captions')
        
        if len(files) > 10:
            return jsonify({'success': False, 'message': 'Maximum 10 photos autorisées'})
        
        uploaded_count = 0
        
        for i, file in enumerate(files):
            if file and file.filename and allowed_file(file.filename):
                # Générer un nom de fichier unique
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                
                # Sauvegarder le fichier
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Redimensionner l'image
                resize_image(file_path)
                
                # Récupérer la légende correspondante
                caption = captions[i] if i < len(captions) else ""
                
                # Créer l'entrée en base de données
                photo = Photo(
                    filename=unique_filename,
                    caption=caption,
                    display_order=Photo.query.count() + uploaded_count
                )
                
                db.session.add(photo)
                uploaded_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'{uploaded_count} photo(s) téléversée(s) avec succès !'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/admin/photos/delete/<int:photo_id>', methods=['DELETE'])
@admin_required
def admin_delete_photo(photo_id):
    try:
        photo = Photo.query.get_or_404(photo_id)
        
        # Supprimer le fichier physique
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Supprimer de la base de données
        db.session.delete(photo)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Photo supprimée avec succès !'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/admin/photos/update-caption/<int:photo_id>', methods=['POST'])
@admin_required
def admin_update_caption(photo_id):
    try:
        photo = Photo.query.get_or_404(photo_id)
        photo.caption = request.form.get('caption', '')
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Légende mise à jour !'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

# Routes de validation supprimées - système simplifié

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

if __name__ == '__main__':
    print("Démarrage du serveur...")
    app.run(debug=True, host='127.0.0.1', port=5000)
