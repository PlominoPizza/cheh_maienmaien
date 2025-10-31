from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
from functools import wraps
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
import logging
from io import BytesIO

# Configuration du logging - AFFICHAGE COMPLET DANS LE TERMINAL
logging.basicConfig(
    level=logging.DEBUG,  # Affiche tous les niveaux (DEBUG, INFO, WARNING, ERROR)
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()  # Affiche dans la console/terminal
    ]
)

# Réduire le bruit des dépendances
logging.getLogger('werkzeug').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Charger les variables d'environnement depuis .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Fichier .env charge")
except ImportError:
    logger.warning("python-dotenv non installe, utilisation des variables d'environnement systeme")
    pass

# Charger la version de l'application
VERSION_FILE = os.path.join(os.path.dirname(__file__), 'VERSION')
if os.path.exists(VERSION_FILE):
    with open(VERSION_FILE, 'r') as f:
        APP_VERSION = f.read().strip()
else:
    APP_VERSION = 'unknown'

logger.info(f"Application version: {APP_VERSION}")

app = Flask(__name__)
app.config['APP_VERSION'] = APP_VERSION

# Configuration de sécurité
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chez-meme-super-secret-key-2024-development-only')
# Le mot de passe admin doit être défini dans les variables d'environnement
# En développement local, voir .env ou utiliser update_admin_password.py
app.config['ADMIN_MDP'] = os.environ.get('ADMIN_MDP')
if not app.config['ADMIN_MDP']:
    logger.warning("ADMIN_MDP n'est pas défini. Utilisez update_admin_password.py pour configurer l'admin.")

# Configuration de la base de données
# Supporte SQLite en local et PostgreSQL en production
database_url = os.environ.get('DATABASE_URL', 'sqlite:///chez_meme.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Optimisations pour la production
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 0,
    'pool_size': 10
}

# Configuration pour le téléversement d'images
UPLOAD_FOLDER = 'static/uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Configuration hCaptcha
app.config['HCAPTCHA_SITE_KEY'] = os.environ.get('HCAPTCHA_SITE_KEY', '')
app.config['HCAPTCHA_SECRET_KEY'] = os.environ.get('HCAPTCHA_SECRET_KEY', '')

# Créer le dossier de téléversement s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# Modèles de base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
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
    filename = db.Column(db.String(200), nullable=False)  # Gardé pour compatibilité
    image_token = db.Column(db.String(64), unique=True, index=True)  # Token aléatoire sécurisé
    image_data = db.Column(db.LargeBinary)  # Données binaires de l'image
    mime_type = db.Column(db.String(50))  # Type MIME (image/jpeg, image/png, etc.)
    caption = db.Column(db.String(200))
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WallOfShame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String(100), nullable=False)
    image_token = db.Column(db.String(64), unique=True, index=True)  # Token aléatoire sécurisé
    image_data = db.Column(db.LargeBinary)  # Données binaires de l'image
    mime_type = db.Column(db.String(50))  # Type MIME
    image_url = db.Column(db.String(200))  # Gardé pour rétrocompatibilité
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    display_order = db.Column(db.Integer, default=0)

class ReservationPending(db.Model):
    """Réservations en attente de validation par l'admin"""
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    guest_name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, approved, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String(100), nullable=False)
    visit_count = db.Column(db.Integer, default=0)
    rank_position = db.Column(db.Integer, default=0)
    last_visit = db.Column(db.Date)
    image_token = db.Column(db.String(64), unique=True, index=True)  # Token aléatoire sécurisé
    image_data = db.Column(db.LargeBinary)  # Données binaires de l'image
    mime_type = db.Column(db.String(50))  # Type MIME
    image_url = db.Column(db.String(200))  # Gardé pour rétrocompatibilité
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Fonctions utilitaires pour les images
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_url(image_filename=None, image_token=None, image_type=None):
    """
    Retourne l'URL de l'image.
    Priorité : token DB > fichier local
    """
    if image_token and image_type:
        return f"/image/{image_token}/{image_type}"
    elif image_filename:
        return f"/static/uploads/images/{image_filename}"
    return None

def resize_image_in_memory(image_bytes, fixed_width=800):
    """Redimensionne une image en mémoire à une largeur fixe de 800px en gardant les proportions"""
    try:
        img = Image.open(BytesIO(image_bytes))
        # Si l'image est déjà plus petite ou égale à 800px, on la laisse telle quelle
        if img.width <= fixed_width:
            return image_bytes
        
        # Calculer la nouvelle hauteur en gardant les proportions
        ratio = fixed_width / img.width
        new_height = int(img.height * ratio)
        new_size = (fixed_width, new_height)
        
        # Redimensionner
        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Sauvegarder en mémoire
        output = BytesIO()
        format_name = img.format or 'JPEG'
        if format_name == 'PNG':
            resized_img.save(output, format='PNG', optimize=True)
        else:
            resized_img.save(output, format='JPEG', quality=85, optimize=True)
        
        return output.getvalue()
    except Exception as e:
        logger.error(f"Erreur lors du redimensionnement en mémoire: {e}")
        return image_bytes  # Retourner l'image originale en cas d'erreur

def resize_image(image_path, fixed_width=800):
    """Redimensionne une image à une largeur fixe de 800px en gardant les proportions"""
    try:
        with Image.open(image_path) as img:
            # Si l'image est déjà plus petite ou égale à 800px, on la laisse telle quelle
            if img.width <= fixed_width:
                return True
            
            # Calculer la nouvelle hauteur en gardant les proportions
            ratio = fixed_width / img.width
            new_height = int(img.height * ratio)
            new_size = (fixed_width, new_height)
            
            # Redimensionner
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Sauvegarder en écrasant l'original
            resized_img.save(image_path, optimize=True, quality=85)
            return True
    except Exception as e:
        logger.error(f"Erreur lors du redimensionnement: {e}")
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

# Gestionnaire d'erreurs global
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Erreur serveur: {error}")
    flash('Une erreur est survenue. Veuillez réessayer.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"Page non trouvée: {request.path}")
    return "<h1>404 - Page non trouvée</h1><p><a href='/'>Retour à l'accueil</a></p>", 404

# Routes principales
# Initialisation automatique de la base de données au démarrage
_first_request_done = False

@app.after_request
def add_security_headers(response):
    """Ajoute des headers pour empêcher l'indexation des images du wall of shame"""
    # Si c'est une image du wall of shame ou la page elle-même
    if '/wall-of-shame' in request.path:
        response.headers['X-Robots-Tag'] = 'noindex, nofollow, noimageindex, noarchive, nosnippet'
    
    # Pour toutes les images uploadées
    if '/static/uploads/images/' in request.path:
        response.headers['X-Robots-Tag'] = 'noindex, nofollow, noimageindex'
    
    # Pour les pages contenant des images
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    
    return response

@app.before_request
def log_request_info():
    """Logger toutes les requêtes HTTP pour le debugging"""
    # Ne pas logger les requêtes pour les fichiers statiques
    if not request.path.startswith('/static') and not request.path.startswith('/favicon.ico'):
        logger.info(f"[REQUETE] {request.method} {request.path}")
        
        # Logger les données POST pour les formulaires
        if request.method == 'POST' and request.form:
            # Masquer les mots de passe pour la sécurité
            form_data = {k: '***' if 'password' in k.lower() else v 
                        for k, v in request.form.items()}
            logger.debug(f"Form data: {form_data}")

@app.after_request
def log_response_info(response):
    """Logger toutes les réponses HTTP"""
    if not request.path.startswith('/static') and not request.path.startswith('/favicon.ico'):
        logger.info(f"[REPONSE] {response.status_code} pour {request.method} {request.path}")
    return response

@app.before_request
def initialize_db():
    """Crée les tables et initialise les données par défaut au premier démarrage"""
    global _first_request_done
    if not _first_request_done:
        try:
            _first_request_done = True
            db.create_all()
            logger.info("Tables de base de données créées/vérifiées.")
            
            # Migration v2.0.0 - Ajouter les colonnes manquantes si nécessaire
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                # Ajouter image_url à Leaderboard si la table existe
                if 'leaderboard' in existing_tables:
                    columns = [col['name'] for col in inspector.get_columns('leaderboard')]
                    if 'image_url' not in columns:
                        logger.info("Migration v2.0.0: Ajout de la colonne image_url à Leaderboard")
                        if db.engine.dialect.name == 'postgresql':
                            db.session.execute(text("ALTER TABLE leaderboard ADD COLUMN IF NOT EXISTS image_url VARCHAR(200)"))
                        else:  # SQLite
                            logger.info("SQLite ne supporte pas ALTER TABLE ADD COLUMN. Utilisez migrate_db.py pour migrer.")
                        db.session.commit()
                
                # Ajouter display_order à WallOfShame si nécessaire
                if 'wall_of_shame' in existing_tables:
                    columns = [col['name'] for col in inspector.get_columns('wall_of_shame')]
                    if 'display_order' not in columns:
                        logger.info("Migration v2.0.0: Ajout de la colonne display_order à WallOfShame")
                        if db.engine.dialect.name == 'postgresql':
                            db.session.execute(text("ALTER TABLE wall_of_shame ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0"))
                        else:  # SQLite
                            logger.info("SQLite ne supporte pas ALTER TABLE ADD COLUMN. Utilisez migrate_db.py pour migrer.")
                        db.session.commit()
                
                # Migration v2.1.0 - Ajouter les colonnes pour stockage images en DB
                if 'photo' in existing_tables:
                    columns = [col['name'] for col in inspector.get_columns('photo')]
                    if 'image_token' not in columns and db.engine.dialect.name == 'postgresql':
                        logger.info("Migration v2.1.0: Ajout des colonnes image_token, image_data, mime_type à Photo")
                        db.session.execute(text("ALTER TABLE photo ADD COLUMN IF NOT EXISTS image_token VARCHAR(64)"))
                        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_photo_image_token ON photo(image_token)"))
                        db.session.execute(text("ALTER TABLE photo ADD COLUMN IF NOT EXISTS image_data BYTEA"))
                        db.session.execute(text("ALTER TABLE photo ADD COLUMN IF NOT EXISTS mime_type VARCHAR(50)"))
                        db.session.commit()
                
                if 'wall_of_shame' in existing_tables:
                    columns = [col['name'] for col in inspector.get_columns('wall_of_shame')]
                    if 'image_token' not in columns and db.engine.dialect.name == 'postgresql':
                        logger.info("Migration v2.1.0: Ajout des colonnes image_token, image_data, mime_type à WallOfShame")
                        db.session.execute(text("ALTER TABLE wall_of_shame ADD COLUMN IF NOT EXISTS image_token VARCHAR(64)"))
                        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_wall_of_shame_image_token ON wall_of_shame(image_token)"))
                        db.session.execute(text("ALTER TABLE wall_of_shame ADD COLUMN IF NOT EXISTS image_data BYTEA"))
                        db.session.execute(text("ALTER TABLE wall_of_shame ADD COLUMN IF NOT EXISTS mime_type VARCHAR(50)"))
                        db.session.commit()
                
                if 'leaderboard' in existing_tables:
                    columns = [col['name'] for col in inspector.get_columns('leaderboard')]
                    if 'image_token' not in columns and db.engine.dialect.name == 'postgresql':
                        logger.info("Migration v2.1.0: Ajout des colonnes image_token, image_data, mime_type à Leaderboard")
                        db.session.execute(text("ALTER TABLE leaderboard ADD COLUMN IF NOT EXISTS image_token VARCHAR(64)"))
                        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_leaderboard_image_token ON leaderboard(image_token)"))
                        db.session.execute(text("ALTER TABLE leaderboard ADD COLUMN IF NOT EXISTS image_data BYTEA"))
                        db.session.execute(text("ALTER TABLE leaderboard ADD COLUMN IF NOT EXISTS mime_type VARCHAR(50)"))
                        db.session.commit()
            except Exception as migration_error:
                logger.warning(f"Migration automatique: {migration_error}")
                logger.info("Si des erreurs persistent, exécutez: python migrate_db.py")
            
            # Migrer la colonne password_hash si nécessaire (pour les anciennes installations)
            try:
                database_url = os.environ.get('DATABASE_URL', 'sqlite:///chez_meme.db')
                if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
                    # Vérifier si on peut obtenir le schéma de la table
                    db.session.execute(db.text("SELECT password_hash FROM \"user\" LIMIT 1"))
                    # Si ça marche, essayer de modifier la colonne
                    try:
                        db.session.execute(db.text("""
                            ALTER TABLE "user" 
                            ALTER COLUMN password_hash TYPE VARCHAR(256);
                        """))
                        db.session.commit()
                        logger.info("Colonne password_hash migrée vers VARCHAR(256)")
                    except Exception as e:
                        if "does not exist" not in str(e) and "already has type" not in str(e):
                            logger.warning(f"Erreur lors de la migration de la colonne: {e}")
                        db.session.rollback()
            except Exception as e:
                logger.info("Migration de colonne non nécessaire")
            
            # S'assurer que l'admin existe avec le bon mot de passe
            admin_user = User.query.filter_by(username='admin').first()
            admin_password = app.config.get('ADMIN_MDP')
            
            if admin_password:
                logger.info(f"ADMIN_MDP détecté - Mise à jour du mot de passe admin")
                
                # Générer le nouveau hash
                new_password_hash = generate_password_hash(admin_password)
                
                if admin_user:
                    logger.info("Utilisateur admin trouvé - Mise à jour du mot de passe")
                    admin_user.password_hash = new_password_hash
                    admin_user.is_admin = True
                    db.session.commit()
                    logger.info("✓ Mot de passe admin mis à jour avec succès")
                else:
                    # Créer l'admin
                    logger.info("Création d'un nouvel utilisateur admin")
                    admin_user = User(
                        username='admin',
                        email='admin@chez-meme.com',
                        password_hash=new_password_hash,
                        is_admin=True
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    logger.info("✓ Utilisateur admin créé avec succès")
            else:
                if admin_user:
                    logger.info("Utilisateur admin trouvé (mot de passe inchangé)")
                else:
                    logger.warning("ADMIN_MDP non défini - l'admin ne peut pas être créé")
            
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
                logger.info("Activités par défaut ajoutées.")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            raise

@app.route('/robots.txt')
def robots_txt():
    """Sert le fichier robots.txt pour empêcher l'indexation des images du wall of shame"""
    return app.send_static_file('robots.txt')

@app.route('/image/<token>/<image_type>')
def get_image_from_db(token, image_type):
    """
    Route sécurisée pour servir les images depuis la base de données.
    Utilise des tokens aléatoires de 64 caractères pour éviter l'indexation.
    """
    try:
        # Vérification de base du token (protection contre brute force)
        if len(token) != 64:
            logger.warning(f"Tentative d'accès avec token de longueur invalide: {len(token)}")
            return '', 404
        
        # Vérification optionnelle du Referer (log pour sécurité, mais pas de blocage strict)
        referer = request.headers.get('Referer', '')
        host = request.headers.get('Host', '')
        if referer and host and not referer.startswith(f'https://{host}') and not referer.startswith(f'http://{host}'):
            logger.warning(f"Tentative d'accès image depuis un domaine externe: {referer} (token: {token[:10]}...)")
            # On ne bloque pas complètement pour compatibilité navigateurs/mode développement
            # mais on log pour monitoring
        
        # Récupération depuis la base de données
        image_data = None
        mime_type = None
        
        if image_type == 'photo':
            photo = Photo.query.filter_by(image_token=token).first()
            if photo and photo.image_data:
                image_data = photo.image_data
                mime_type = photo.mime_type or 'image/jpeg'
        
        elif image_type == 'wall':
            entry = WallOfShame.query.filter_by(image_token=token).first()
            if entry and entry.image_data:
                image_data = entry.image_data
                mime_type = entry.mime_type or 'image/jpeg'
        
        elif image_type == 'leader':
            leader = Leaderboard.query.filter_by(image_token=token).first()
            if leader and leader.image_data:
                image_data = leader.image_data
                mime_type = leader.mime_type or 'image/jpeg'
        
        else:
            logger.warning(f"Type d'image invalide: {image_type}")
            return '', 404
        
        if not image_data:
            return '', 404
        
        # Headers de sécurité pour empêcher l'indexation
        response = Response(image_data, mimetype=mime_type)
        response.headers['X-Robots-Tag'] = 'noindex, nofollow, noimageindex, noarchive, nosnippet'
        response.headers['Cache-Control'] = 'private, max-age=3600'  # Cache privé seulement
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'image: {e}")
        return '', 404

@app.route('/')
def index():
    photos = Photo.query.order_by(Photo.display_order, Photo.created_at).all()
    return render_template('index.html', photos=photos, get_image_url=get_image_url)

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
    # Coordonnées de chez mémé : 7 avenue du Lac Marion, 64200 Biarritz
    chez_meme_coords = {'lat': 43.47007441987446, 'lng': -1.5502231105144162}
    
    # Données des spots de surf à proximité (ordre de proximité)
    # Descriptions officielles depuis Surf Forecast : https://fr.surf-forecast.com/
    # Calcul des coûts (prix_round_trip) pour l'aller-retour depuis 7 avenue du Lac Marion, 64200 Biarritz
    # Hypothèses : Renault Clio IV (6.5 L/100km), essence 1.75€/L
    # Formule carburant : (distance_km * 2 / 100) * 6.5 * 1.75
    # Péages A63 (classe 1) - Référence : https://public-content.vinci-autoroutes.com/PDF/Tarifs-peage-asf/C1-TARIFS-WEB-2025-maille.pdf
    # Chez mémé : sortie 4 Biarritz (demi-échangeur sud) -> 1,2€/passage
    # Hendaye : péage n°2 (St Jean de Luz Sud) -> 1,9€/passage = 3,8€ A/R
    # Capbreton/Hossegor/Seignosse : péage n°8 (Capbreton) -> 2€/passage = 4€ A/R
    # Distances calculées via l'API OSRM (Open Source Routing Machine) - distances routières réelles
    # Point de départ : 7 avenue du Lac Marion, 64200 Biarritz (43.47007441987446, -1.5502231105144162)
    # Coordonnées GPS mises à jour selon les points d'arrivée fournis
    surf_spots = [
        {
            'name': 'Côte des Basques',
            'location': 'Biarritz',
            'lat': 43.47564359716611,
            'lng': -1.5664002921277527,
            'distance_km': 2.1,  # Distance calculée via OSRM
            'temps_minutes': 5,
            'prix_round_trip': 0.48,  # Pas de péage : (2.1*2/100)*6.5*1.75 = 0.48€
            'rating': 4,
            'description': 'Côte des Basques dans la Côte Basque est un spot de plage et de récif exposé qui offre un surf assez régulier et peut fonctionner à tout moment de l\'année. Fonctionne mieux avec des vents offshore de l\'est avec un certain abri ici des vents du nord-ouest. Houles de vent et de fond en parts égales et l\'angle idéal de houle est de l\'ouest. Le spot de plage offre à la fois des vagues gauches et droites. Meilleur autour de la marée basse. Quand le surf est bon, la foule est probable. Attention aux rochers dans le lineup.'
        },
        {
            'name': 'Grande Plage',
            'location': 'Biarritz',
            'lat': 43.48505622591267,
            'lng': -1.5574765227972476,
            'distance_km': 2.5,  # Distance calculée via OSRM
            'temps_minutes': 5,
            'prix_round_trip': 0.57,  # Pas de péage : (2.5*2/100)*6.5*1.75 = 0.57€
            'rating': 3,
            'description': 'Grande Plage dans la Côte Basque est un spot de plage exposé qui offre un surf assez régulier et peut fonctionner à tout moment de l\'année. Les vents offshore soufflent de l\'est avec un certain abri ici des vents du sud. Houles de vent et de fond en parts égales et la meilleure direction de houle est de l\'ouest. Le spot de plage offre à la fois des vagues gauches et droites. Susceptible d\'être bondé si ça fonctionne. Les dangers incluent la foule et la pollution.'
        },
        {
            'name': 'Chambre d\'Amour',
            'location': 'Anglet',
            'lat': 43.49427252956886,
            'lng': -1.5456154571455343,
            'distance_km': 5.2,  # Distance calculée via OSRM
            'temps_minutes': 11,
            'prix_round_trip': 1.18,  # Pas de péage : (5.2*2/100)*6.5*1.75 = 1.18€
            'rating': 3,
            'description': 'Anglet - Chambre d\'Amour dans la Côte Basque est un spot de plage exposé qui offre un surf assez régulier et peut fonctionner à tout moment de l\'année. La meilleure direction de vent est du sud-est. Tendance à recevoir un mélange de houles de fond et de vent et l\'angle idéal de houle est du nord-ouest. Le spot de plage offre à la fois des vagues gauches et droites. Surfeable à tous les stades de la marée. C\'est souvent bondé ici. Les dangers incluent les dangers créés par l\'homme (bouées etc.) et le localisme.'
        },
        {
            'name': 'Uhabia',
            'location': 'Bidart',
            'lat': 43.43108738144451,
            'lng': -1.5989006378043706,
            'distance_km': 7.9,  # Distance calculée via OSRM
            'temps_minutes': 11,
            'prix_round_trip': 1.80,  # Pas de péage : (7.9*2/100)*6.5*1.75 = 1.80€
            'rating': 3,
            'description': 'Bidart dans la Côte Basque est un spot de plage exposé qui offre un surf assez fiable et peut fonctionner à tout moment de l\'année. La meilleure direction de vent est du sud-est. Tendance à recevoir un mélange de houles de fond et de vent et la meilleure direction de houle est de l\'ouest. Le spot de plage offre des vagues gauches et droites. Bon surf à tous les stades de la marée. Parfois bondé. Attention aux courants, rochers et pollution.'
        },
        {
            'name': 'Parlementia',
            'location': 'Guéthary',
            'lat': 43.427723562362054,
            'lng': -1.6068852440572812,
            'distance_km': 8.7,  # Distance calculée via OSRM
            'temps_minutes': 13,
            'prix_round_trip': 1.98,  # Pas de péage : (8.7*2/100)*6.5*1.75 = 1.98€
            'rating': 3,
            'description': 'Parlementia dans la Côte Basque est un spot de récif exposé qui offre un surf fiable et peut fonctionner à tout moment de l\'année. La meilleure direction de vent est de l\'est-sud-est. Houles de vent et de fond en parts égales et la meilleure direction de houle est de l\'ouest. Il n\'y a pas de spot de plage, seulement un récif droite. La qualité du surf n\'est pas affectée par la marée. Quand ça fonctionne ici, ça peut être bondé. Attention aux rochers.'
        },
        {
            'name': 'Hendaye Plage',
            'location': 'Hendaye',
            'lat': 43.3735961088257,
            'lng': -1.7742203280832838,
            'distance_km': 31.4,  # Distance calculée via OSRM
            'temps_minutes': 29,
            'prix_round_trip': 10.94,  # Carburant : (31.4*2/100)*6.5*1.75 = 7.14€ + Péage A63 péage 2 (3.8€ A/R) = 10.94€
            'rating': 3,
            'description': 'Hendaye Plage dans la Côte Basque est un spot de plage et de récif assez exposé qui offre un surf assez régulier et peut fonctionner à tout moment de l\'année. Les vents offshore viennent du sud avec un certain abri ici des vents d\'ouest. La plupart du surf ici provient de houles de fond et la direction idéale de houle est de l\'ouest-nord-ouest. Le spot de plage offre des vagues gauches et droites et il y a aussi un récif droite. La qualité du surf n\'est pas affectée par la marée. Susceptible d\'être bondé si ça fonctionne. Attention aux rochers.'
        },
        {
            'name': 'Santocha',
            'location': 'Capbreton',
            'lat': 43.64702883230817,
            'lng': -1.4426945771349413,
            'distance_km': 37.3,  # Distance calculée via OSRM
            'temps_minutes': 33,
            'prix_round_trip': 12.48,  # Carburant : (37.3*2/100)*6.5*1.75 = 8.48€ + Péage A63 péage 8 (4€ A/R) = 12.48€
            'rating': 3,
            'description': 'Capbreton - Le Santocha dans les Landes est un spot de plage assez exposé qui offre un surf assez régulier et peut fonctionner à tout moment de l\'année. La meilleure direction de vent est de l\'est. Houles de vent et de fond en parts égales et la meilleure direction de houle est de l\'ouest. Le spot de plage offre des vagues gauches et droites. Même quand il y a des vagues, il n\'est probablement pas bondé. Attention au localisme.'
        },
        {
            'name': 'La Gravière',
            'location': 'Hossegor',
            'lat': 43.6737751398771,
            'lng': -1.4391911691273902,
            'distance_km': 40.1,  # Distance calculée via OSRM
            'temps_minutes': 37,
            'prix_round_trip': 13.11,  # Carburant : (40.1*2/100)*6.5*1.75 = 9.11€ + Péage A63 péage 8 (4€ A/R) = 13.11€
            'rating': 4,
            'description': 'Hossegor - La Gravière dans les Landes est un spot de barre de sable exposé qui offre un surf assez régulier. La meilleure période de l\'année pour les vagues est l\'automne. Les vents offshore soufflent de l\'est. Tendance à recevoir un mélange de houles de fond et de vent et la direction idéale de houle est de l\'ouest. Le spot de barre de sable offre à la fois des vagues gauches et droites. C\'est parfois bondé ici. Prenez des précautions particulières ici si ça devient très bondé.'
        },
        {
            'name': 'Le Penon',
            'location': 'Seignosse',
            'lat': 43.709888795671304,
            'lng': -1.4339030135463402,
            'distance_km': 46.2,  # Distance calculée via OSRM
            'temps_minutes': 44,
            'prix_round_trip': 14.51,  # Carburant : (46.2*2/100)*6.5*1.75 = 10.51€ + Péage A63 péage 8 (4€ A/R) = 14.51€
            'rating': 3,
            'description': 'Le Penon en Aquitaine est un spot de plage/jetée exposé qui offre un surf irrégulier sans modèle saisonnier particulier. La meilleure direction de vent est de l\'est. Houles de vent et de fond en parts égales et l\'angle idéal de houle est de l\'ouest. Le spot de plage offre des vagues gauches et droites. Bon surf à tous les stades de la marée. Quand le surf est bon, ça peut devenir assez chargé dans l\'eau. Attention aux courants dangereux.'
        },
        {
            'name': 'Roca Puta',
            'location': 'Zumaia (Espagne)',
            'lat': 43.30547054811386,
            'lng': -2.240322543271815,
            'distance_km': 72.8,  # Distance calculée via OSRM
            'temps_minutes': 53,
            'prix_round_trip': 20.36,  # Carburant : (72.8*2/100)*6.5*1.75 = 16.56€ + Péage A63 péage 2 (3.8€ A/R) = 20.36€ (péage Espagne non inclus - frontière libre)
            'rating': 4,
            'description': 'Roca Puta dans le Pays Basque est un spot de récif exposé qui offre un surf assez régulier. L\'automne et l\'hiver sont les meilleures périodes de l\'année pour les vagues. Fonctionne mieux avec des vents offshore du sud-est. Les houles de fond et de vent sont également probables et la direction idéale de houle est du nord-ouest. Il n\'y a pas de spot de plage, seulement un récif droite. Meilleur autour de la marée basse. Il est très rarement bondé ici. Les dangers incluent des rochers, des courants et la pollution.'
        }
    ]
    
    return render_template('activites.html', surf_spots=surf_spots, chez_meme=chez_meme_coords)

@app.route('/api/surf-forecast')
def api_surf_forecast():
    """API pour récupérer les prévisions de surf pour Biarritz"""
    try:
        # Scraper Surf-Forecast.com pour Grand Plage Biarritz
        return scrape_surf_forecast()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des prévisions: {e}")
        import traceback
        traceback.print_exc()
        return api_surf_forecast_mock()

def scrape_surf_forecast():
    """Récupérer les prévisions pour Côte des Basques"""
    try:
        import requests
        from datetime import datetime, timedelta
        
        # Coordonnées de Côte des Basques, Biarritz
        latitude = 43.475206303831754
        longitude = -1.5686086721152588
        
        # API Open-Meteo pour les prévisions météorologiques marines
        url = "https://marine-api.open-meteo.com/v1/marine"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "wave_height,wave_period,wave_direction,wind_speed_10m,wind_direction_10m",
            "timezone": "Europe/Paris",
            "forecast_days": 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            hourly = data.get('hourly', {})
            
            # Organiser les données par jour et par période (matin, après-midi, nuit)
            forecasts = {}
            
            for i, timestamp in enumerate(hourly.get('time', [])):
                date = datetime.fromisoformat(timestamp.replace('+01:00', '+00:00') if '+01:00' in timestamp else timestamp)
                hour = date.hour
                
                # Déterminer la période
                if 4 <= hour < 12:
                    period = 'morning'
                elif 12 <= hour < 20:
                    period = 'afternoon'
                else:
                    period = 'night'
                
                date_key = date.date().isoformat()
                
                if date_key not in forecasts:
                    forecasts[date_key] = {
                        'morning': {'wave_height': [], 'wave_period': [], 'wind_speed': [], 'wind_direction': []},
                        'afternoon': {'wave_height': [], 'wave_period': [], 'wind_speed': [], 'wind_direction': []},
                        'night': {'wave_height': [], 'wave_period': [], 'wind_speed': [], 'wind_direction': []}
                    }
                
                # Ajouter les données à la période correspondante
                wave_height = hourly.get('wave_height', [])[i] if i < len(hourly.get('wave_height', [])) else 0
                wave_period = hourly.get('wave_period', [])[i] if i < len(hourly.get('wave_period', [])) else 0
                wind_speed = hourly.get('wind_speed_10m', [])[i] if i < len(hourly.get('wind_speed_10m', [])) else 0
                wind_direction = hourly.get('wind_direction_10m', [])[i] if i < len(hourly.get('wind_direction_10m', [])) else 0
                
                forecasts[date_key][period]['wave_height'].append(wave_height)
                forecasts[date_key][period]['wave_period'].append(wave_period)
                forecasts[date_key][period]['wind_speed'].append(wind_speed)
                forecasts[date_key][period]['wind_direction'].append(wind_direction)
            
            # Calculer les moyennes pour chaque période
            result = []
            for date_key in sorted(forecasts.keys())[:10]:
                day_data = forecasts[date_key]
                
                def avg(lst):
                    return round(sum(lst) / len(lst), 1) if lst else 0
                
                def avg_int(lst):
                    return int(sum(lst) / len(lst)) if lst else 0
                
                result.append({
                    'date': date_key,
                    'periods': {
                        'morning': {
                            'wave_height': avg(day_data['morning']['wave_height']),
                            'wave_period': avg_int(day_data['morning']['wave_period']),
                            'wind_speed': avg_int([s * 3.6 for s in day_data['morning']['wind_speed']]),  # m/s to km/h
                            'wind_direction': avg_int(day_data['morning']['wind_direction'])
                        },
                        'afternoon': {
                            'wave_height': avg(day_data['afternoon']['wave_height']),
                            'wave_period': avg_int(day_data['afternoon']['wave_period']),
                            'wind_speed': avg_int([s * 3.6 for s in day_data['afternoon']['wind_speed']]),
                            'wind_direction': avg_int(day_data['afternoon']['wind_direction'])
                        },
                        'night': {
                            'wave_height': avg(day_data['night']['wave_height']),
                            'wave_period': avg_int(day_data['night']['wave_period']),
                            'wind_speed': avg_int([s * 3.6 for s in day_data['night']['wind_speed']]),
                            'wind_direction': avg_int(day_data['night']['wind_direction'])
                        }
                    }
                })
            
            # Ajouter les marées pour chaque jour
            for forecast in result:
                forecast['tides'] = get_tides_for_date(forecast['date'])
            
            return jsonify({
                'success': True,
                'forecasts': result
            })
        else:
            logger.error(f"Erreur API Open-Meteo: {response.status_code} - {response.text}")
            return api_surf_forecast_mock()
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des prévisions: {e}")
        import traceback
        traceback.print_exc()
        return api_surf_forecast_mock()

def api_surf_forecast_mock():
    """Version mockée de l'API de prévisions de surf"""
    from datetime import datetime, timedelta
    import random
    
    forecasts = []
    base_date = datetime.now()
    
    for i in range(10):
        date = base_date + timedelta(days=i)
        date_str = date.date().isoformat()
        
        # Générer des données réalistes pour Biarritz
        forecasts.append({
            'date': date_str,
            'periods': {
                'morning': {
                    'wave_height': round(random.uniform(0.8, 2.5), 1),
                    'wave_period': random.randint(8, 15),
                    'wind_speed': random.randint(5, 25),
                    'wind_direction': random.randint(0, 360)
                },
                'afternoon': {
                    'wave_height': round(random.uniform(1.0, 3.0), 1),
                    'wave_period': random.randint(10, 18),
                    'wind_speed': random.randint(10, 30),
                    'wind_direction': random.randint(0, 360)
                },
                'night': {
                    'wave_height': round(random.uniform(0.9, 2.2), 1),
                    'wave_period': random.randint(8, 14),
                    'wind_speed': random.randint(5, 20),
                    'wind_direction': random.randint(0, 360)
                }
            },
            'tides': {
                'high_1': {
                    'time': f"{(8 + i) % 24}:00",
                    'height': round(3.0 + random.uniform(0, 1.5), 2)
                },
                'low_1': {
                    'time': f"{(14 + i) % 24}:00",
                    'height': round(1.0 + random.uniform(0, 0.8), 2)
                }
            }
        })
    
    return jsonify({
        'success': True,
        'forecasts': forecasts,
        'mock': True  # Flag pour indiquer que ce sont des données mockées
    })

def get_tides_for_date(date_str):
    """Récupérer les marées pour une date donnée"""
    try:
        import requests
        from datetime import datetime
        
        # Coordonnées de Biarritz
        latitude = 43.487
        longitude = -1.560
        
        # API Tide API pour les marées
        # On utilise une approximation simple basée sur l'heure
        date = datetime.fromisoformat(date_str)
        
        # Pour l'instant, on va simuler des marées (haute et basse)
        # Dans un vrai cas, on utiliserait une API de marées comme tides.mobilegeographics.com
        
        # Simulation simple : haute marée autour de 8h et 20h, basse marée autour de 14h et 2h
        high_tide_1 = f"{(8 + (date.day % 4)) % 24}:00"
        low_tide_1 = f"{(14 + (date.day % 4)) % 24}:00"
        
        return {
            'high_1': {'time': high_tide_1, 'height': round(3.5 + (date.day % 5) * 0.2, 2)},
            'low_1': {'time': low_tide_1, 'height': round(1.2 + (date.day % 5) * 0.1, 2)}
        }
    except Exception as e:
        logger.error(f"Erreur marées: {e}")
        return {
            'high_1': {'time': 'N/A', 'height': 0},
            'low_1': {'time': 'N/A', 'height': 0}
        }

@app.route('/wall-of-shame')
def wall_of_shame():
    wall_entries = WallOfShame.query.order_by(WallOfShame.display_order, WallOfShame.created_at.desc()).all()
    return render_template('wall_of_shame.html', wall_entries=wall_entries, get_image_url=get_image_url)

@app.route('/leaderboard')
def leaderboard():
    leaders = Leaderboard.query.order_by(Leaderboard.rank_position, Leaderboard.visit_count.desc()).all()
    return render_template('leaderboard.html', leaders=leaders, get_image_url=get_image_url)

def verify_hcaptcha(token):
    """Vérifier le token hCaptcha"""
    # En mode développement, si aucune clé n'est configurée, accepter toujours
    if not app.config['HCAPTCHA_SECRET_KEY']:
        logger.info("hCaptcha désactivé (mode développement)")
        return True
    
    if not token:
        logger.warning("Token hCaptcha manquant")
        return False
    
    try:
        import requests
        response = requests.post(
            'https://hcaptcha.com/siteverify',
            data={
                'secret': app.config['HCAPTCHA_SECRET_KEY'],
                'response': token
            },
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            logger.info(f"Vérification hCaptcha: {'succès' if success else 'échec'}")
            return success
    except Exception as e:
        logger.error(f"Erreur lors de la vérification hCaptcha: {e}")
        return False
    
    return False

@app.route('/reserver', methods=['GET', 'POST'])
def reserver():
    if request.method == 'POST':
        try:
            # Créer une nouvelle réservation en attente
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            
            # Vérifier que les dates sont valides
            if start_date >= end_date:
                return jsonify({'success': False, 'message': 'Le jour de départ doit être après le jour d\'arrivée !'})
            
            if start_date < date.today():
                return jsonify({'success': False, 'message': 'Impossible de réserver dans le passé !'})
            
            # Vérifier les conflits avec les réservations approuvées
            conflicting = Reservation.query.filter(
                Reservation.status == 'approved',
                Reservation.start_date < end_date,
                Reservation.end_date > start_date
            ).first()
            
            if conflicting:
                return jsonify({'success': False, 'message': f'Ces dates sont déjà réservées par {conflicting.guest_name} !'})
            
            # Récupérer l'IP et le user agent pour la sécurité
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            # Créer la réservation en attente
            pending_reservation = ReservationPending(
                start_date=start_date,
                end_date=end_date,
                guest_name=request.form['guest_name'],
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.add(pending_reservation)
            db.session.commit()
            
            logger.info(f"Nouvelle réservation en attente créée par {request.form['guest_name']} (IP: {ip_address})")
            return jsonify({'success': True, 'message': 'Votre demande a bien été envoyée pour approbation.'})
                
        except Exception as e:
            logger.error(f"Erreur lors de la réservation: {e}")
            return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})
    
    # Récupérer les paramètres pour pré-remplir le formulaire
    prefilled_data = {
        'guest_name': request.args.get('guest_name', ''),
        'start_date': request.args.get('start_date', ''),
        'end_date': request.args.get('end_date', '')
    }
    
    return render_template('reserver.html', prefilled_data=prefilled_data)

@app.route('/admin')
@admin_required
def admin():
    all_reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    # Compter les réservations en attente
    pending_count = ReservationPending.query.filter_by(status='pending').count()
    return render_template('admin_dashboard.html', reservations=all_reservations, pending_count=pending_count)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vérification normale du mot de passe
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password) and user.is_admin:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = True
            flash('Connexion réussie !', 'success')
            logger.info(f"Connexion admin: {username}")
            return redirect(url_for('admin'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
            logger.warning(f"Tentative de connexion échouée pour: {username}")
    
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
            
            logger.info(f"Réservation admin créée pour {request.form['guest_name']}")
            return jsonify({'success': True, 'message': 'Réservation créée avec succès !'})
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de réservation admin: {e}")
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
        
        logger.info(f"Réservation {reservation_id} modifiée")
        return jsonify({'success': True, 'message': 'Réservation modifiée avec succès !'})
        
    except Exception as e:
        logger.error(f"Erreur lors de la modification de réservation: {e}")
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/admin/delete/<int:reservation_id>', methods=['DELETE'])
@admin_required
def admin_delete_reservation(reservation_id):
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        guest_name = reservation.guest_name
        
        db.session.delete(reservation)
        db.session.commit()
        
        logger.info(f"Réservation supprimée: {guest_name}")
        return jsonify({'success': True, 'message': f'Réservation de {guest_name} supprimée avec succès !'})
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de réservation: {e}")
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

# Routes pour la gestion des photos
@app.route('/admin/photos')
@admin_required
def admin_photos():
    photos = Photo.query.order_by(Photo.display_order, Photo.created_at).all()
    return render_template('admin_photos.html', photos=photos, get_image_url=get_image_url)

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
                # Récupérer la légende correspondante
                caption = captions[i] if i < len(captions) else ""
                
                # Lire le fichier en mémoire
                file.seek(0)
                image_bytes = file.read()
                
                # Déterminer le type MIME
                mime_type = file.content_type or 'image/jpeg'
                if not mime_type.startswith('image/'):
                    # Détecter depuis l'extension
                    ext = os.path.splitext(file.filename)[1].lower()
                    mime_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', 
                                  '.gif': 'image/gif', '.webp': 'image/webp'}
                    mime_type = mime_types.get(ext, 'image/jpeg')
                
                # Redimensionner l'image en mémoire
                resized_image_bytes = resize_image_in_memory(image_bytes, fixed_width=800)
                
                # Générer un token sécurisé unique (64 caractères)
                image_token = secrets.token_urlsafe(48)  # Génère ~64 caractères
                # Vérifier l'unicité (très improbable mais on vérifie)
                while Photo.query.filter_by(image_token=image_token).first():
                    image_token = secrets.token_urlsafe(48)
                
                # Générer un nom de fichier unique pour compatibilité
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                
                # Créer l'entrée en base de données avec données binaires
                photo = Photo(
                    filename=unique_filename,
                    image_token=image_token,
                    image_data=resized_image_bytes,
                    mime_type=mime_type,
                    caption=caption,
                    display_order=Photo.query.count() + uploaded_count
                )
                
                db.session.add(photo)
                uploaded_count += 1
        
        db.session.commit()
        
        logger.info(f"{uploaded_count} photo(s) téléversée(s)")
        return jsonify({
            'success': True, 
            'message': f'{uploaded_count} photo(s) téléversée(s) avec succès !'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du téléversement de photos: {e}")
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/admin/photos/delete/<int:photo_id>', methods=['DELETE'])
@admin_required
def admin_delete_photo(photo_id):
    try:
        photo = Photo.query.get_or_404(photo_id)
        
        # Supprimer le fichier physique (local)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Supprimer de la base de données
        db.session.delete(photo)
        db.session.commit()
        
        logger.info(f"Photo {photo_id} supprimée")
        return jsonify({'success': True, 'message': 'Photo supprimée avec succès !'})
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de photo: {e}")
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
        logger.error(f"Erreur lors de la mise à jour de légende: {e}")
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/admin/photos/update-all', methods=['POST'])
@admin_required
def admin_update_all_photos():
    """Met à jour toutes les photos : légendes et ordre"""
    try:
        data = request.get_json()
        updates = data.get('updates', [])
        
        for update in updates:
            photo = db.session.get(Photo, update['id'])
            if photo:
                photo.caption = update.get('caption', '')
                photo.display_order = update.get('display_order', 0)
        
        db.session.commit()
        
        logger.info(f"Photos mises à jour : {len(updates)} modification(s)")
        return jsonify({'success': True, 'message': f'{len(updates)} photo(s) mise(s) à jour avec succès !'})
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour globale: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

# Routes admin pour Wall of Shame
@app.route('/admin/wall-of-shame')
@admin_required
def admin_wall_of_shame():
    wall_entries = WallOfShame.query.order_by(WallOfShame.display_order, WallOfShame.created_at.desc()).all()
    return render_template('admin_wall_of_shame.html', wall_entries=wall_entries, get_image_url=get_image_url)

@app.route('/admin/wall-of-shame/upload', methods=['POST'])
@admin_required
def admin_upload_wall_entry():
    try:
        person_name = request.form.get('person_name', '')
        if not person_name:
            return jsonify({'success': False, 'message': 'Le nom de la personne est requis'})
        
        if 'photo' not in request.files:
            return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
        
        file = request.files['photo']
        if file and file.filename and allowed_file(file.filename):
            existing_count = WallOfShame.query.count()
            
            # Lire le fichier en mémoire
            file.seek(0)
            image_bytes = file.read()
            
            # Déterminer le type MIME
            mime_type = file.content_type or 'image/jpeg'
            if not mime_type.startswith('image/'):
                ext = os.path.splitext(file.filename)[1].lower()
                mime_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', 
                              '.gif': 'image/gif', '.webp': 'image/webp'}
                mime_type = mime_types.get(ext, 'image/jpeg')
            
            # Redimensionner l'image en mémoire
            resized_image_bytes = resize_image_in_memory(image_bytes, fixed_width=800)
            
            # Générer un token sécurisé unique (64 caractères)
            image_token = secrets.token_urlsafe(48)
            while WallOfShame.query.filter_by(image_token=image_token).first():
                image_token = secrets.token_urlsafe(48)
            
            # Générer un nom de fichier pour compatibilité
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            simple_filename = f"img{existing_count + 1}{ext}"
            
            # Créer l'entrée en base de données avec données binaires
            wall_entry = WallOfShame(
                person_name=person_name,
                image_token=image_token,
                image_data=resized_image_bytes,
                mime_type=mime_type,
                image_url=simple_filename,  # Gardé pour rétrocompatibilité
                display_order=existing_count
            )
            
            db.session.add(wall_entry)
            db.session.commit()
            
            logger.info(f"Entrée Wall of Shame ajoutée pour {person_name} avec l'image token {image_token[:10]}...")
            return jsonify({'success': True, 'message': f'Entrée ajoutée pour {person_name} !'})
        else:
            return jsonify({'success': False, 'message': 'Format de fichier non autorisé'})
            
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout d'entrée Wall of Shame: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/admin/wall-of-shame/delete/<int:entry_id>', methods=['DELETE'])
@admin_required
def admin_delete_wall_entry(entry_id):
    try:
        entry = WallOfShame.query.get_or_404(entry_id)
        
        # Supprimer le fichier physique (local)
        if entry.image_url:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], entry.image_url)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(entry)
        db.session.commit()
        
        logger.info(f"Entrée Wall of Shame {entry_id} supprimée")
        return jsonify({'success': True, 'message': 'Entrée supprimée avec succès !'})
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

# Routes admin pour Leaderboard
@app.route('/admin/leaderboard')
@admin_required
def admin_leaderboard():
    leaders = Leaderboard.query.order_by(Leaderboard.rank_position, Leaderboard.visit_count.desc()).all()
    return render_template('admin_leaderboard.html', leaders=leaders, get_image_url=get_image_url)

@app.route('/admin/leaderboard/add', methods=['POST'])
@admin_required
def admin_add_leader():
    try:
        person_name = request.form.get('person_name', '')
        visit_count = int(request.form.get('visit_count', 0))
        
        if not person_name:
            return jsonify({'success': False, 'message': 'Le nom de la personne est requis'})
        
        # Gérer l'upload de photo (stockage en DB)
        image_token = None
        image_data = None
        mime_type = None
        image_url = None
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                # Lire le fichier en mémoire
                file.seek(0)
                image_bytes = file.read()
                
                # Déterminer le type MIME
                mime_type = file.content_type or 'image/jpeg'
                if not mime_type.startswith('image/'):
                    ext = os.path.splitext(file.filename)[1].lower()
                    mime_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', 
                                  '.gif': 'image/gif', '.webp': 'image/webp'}
                    mime_type = mime_types.get(ext, 'image/jpeg')
                
                # Redimensionner l'image en mémoire
                image_data = resize_image_in_memory(image_bytes, fixed_width=800)
                
                # Générer un token sécurisé unique
                image_token = secrets.token_urlsafe(48)
                while Leaderboard.query.filter_by(image_token=image_token).first():
                    image_token = secrets.token_urlsafe(48)
                
                # Générer un nom de fichier pour compatibilité
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                image_url = unique_filename
        
        leader = Leaderboard(
            person_name=person_name,
            visit_count=visit_count,
            rank_position=Leaderboard.query.count() + 1,
            image_token=image_token,
            image_data=image_data,
            mime_type=mime_type,
            image_url=image_url  # Gardé pour rétrocompatibilité
        )
        
        db.session.add(leader)
        db.session.commit()
        
        logger.info(f"Leader ajouté: {person_name}")
        return jsonify({'success': True, 'message': f'Leader {person_name} ajouté avec succès !'})
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de leader: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/admin/leaderboard/update/<int:leader_id>', methods=['POST'])
@admin_required
def admin_update_leader(leader_id):
    try:
        leader = Leaderboard.query.get_or_404(leader_id)
        leader.person_name = request.form.get('person_name', leader.person_name)
        leader.visit_count = int(request.form.get('visit_count', leader.visit_count))
        
        # Gérer l'upload de photo (stockage en DB)
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                # Lire le fichier en mémoire
                file.seek(0)
                image_bytes = file.read()
                
                # Déterminer le type MIME
                mime_type = file.content_type or 'image/jpeg'
                if not mime_type.startswith('image/'):
                    ext = os.path.splitext(file.filename)[1].lower()
                    mime_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', 
                                  '.gif': 'image/gif', '.webp': 'image/webp'}
                    mime_type = mime_types.get(ext, 'image/jpeg')
                
                # Redimensionner l'image en mémoire
                image_data = resize_image_in_memory(image_bytes, fixed_width=800)
                
                # Générer un nouveau token sécurisé unique
                image_token = secrets.token_urlsafe(48)
                while Leaderboard.query.filter_by(image_token=image_token).first():
                    image_token = secrets.token_urlsafe(48)
                
                # Mettre à jour les champs
                leader.image_token = image_token
                leader.image_data = image_data
                leader.mime_type = mime_type
                
                # Générer un nom de fichier pour compatibilité
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                leader.image_url = unique_filename
        
        db.session.commit()
        
        logger.info(f"Leader {leader_id} mis à jour")
        return jsonify({'success': True, 'message': 'Leader mis à jour avec succès !'})
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/admin/leaderboard/delete/<int:leader_id>', methods=['DELETE'])
@admin_required
def admin_delete_leader(leader_id):
    try:
        leader = Leaderboard.query.get_or_404(leader_id)
        
        # Supprimer l'image si elle existe (local)
        if leader.image_url:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], leader.image_url)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(leader)
        db.session.commit()
        
        logger.info(f"Leader {leader_id} supprimé")
        return jsonify({'success': True, 'message': 'Leader supprimé avec succès !'})
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

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

# === Routes pour les réservations en attente de validation ===

@app.route('/admin/pending')
@admin_required
def admin_pending_reservations():
    """Afficher toutes les réservations (en attente + validées)"""
    # Réservations en attente de validation
    pending = ReservationPending.query.order_by(ReservationPending.created_at.desc()).all()
    # Réservations validées
    approved = Reservation.query.filter_by(status='approved').order_by(Reservation.created_at.desc()).all()
    return render_template('admin_pending.html', pending_reservations=pending, approved_reservations=approved)

@app.route('/admin/pending/approve/<int:pending_id>', methods=['POST'])
@admin_required
def admin_approve_pending(pending_id):
    """Valider une réservation en attente (statut -> Validée)"""
    pending = ReservationPending.query.get_or_404(pending_id)
    
    try:
        # Vérifier les conflits
        conflicting = Reservation.query.filter(
            Reservation.status == 'approved',
            Reservation.start_date < pending.end_date,
            Reservation.end_date > pending.start_date
        ).first()
        
        if conflicting:
            db.session.delete(pending)
            db.session.commit()
            flash(f'Conflit détecté ! Ces dates sont déjà réservées par {conflicting.guest_name}.', 'error')
        else:
            # Changer le statut en 'approved' (Validée)
            pending.status = 'approved'
            
            # Créer la réservation dans la table principale
            token = secrets.token_urlsafe(32)
            reservation = Reservation(
                start_date=pending.start_date,
                end_date=pending.end_date,
                guest_name=pending.guest_name,
                status='approved',
                token=token
            )
            db.session.add(reservation)
            db.session.delete(pending)
            db.session.commit()
            flash(f'Réservation de {pending.guest_name} validée !', 'success')
            logger.info(f"Réservation validée: {pending.guest_name}, {pending.start_date} - {pending.end_date}")
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'approbation: {str(e)}', 'error')
        logger.error(f"Erreur lors de l'approbation: {e}")
    
    return redirect(url_for('admin_pending_reservations'))

@app.route('/admin/pending/reject/<int:pending_id>', methods=['POST'])
@admin_required
def admin_reject_pending(pending_id):
    """Rejeter une réservation en attente"""
    pending = ReservationPending.query.get_or_404(pending_id)
    guest_name = pending.guest_name
    db.session.delete(pending)
    db.session.commit()
    flash(f'Réservation de {guest_name} rejetée et supprimée.', 'info')
    logger.info(f"Réservation rejetée: {guest_name}")
    return redirect(url_for('admin_pending_reservations'))

@app.route('/admin/pending/delete-all', methods=['POST'])
@admin_required
def admin_delete_all_pending():
    """Supprimer toutes les réservations en attente"""
    try:
        count = ReservationPending.query.delete()
        db.session.commit()
        flash(f'Toutes les réservations en attente ont été supprimées ({count}).', 'info')
        logger.info(f"Suppression de toutes les réservations en attente: {count}")
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
        logger.error(f"Erreur lors de la suppression de toutes les réservations: {e}")
    
    return redirect(url_for('admin_pending_reservations'))

@app.route('/admin/pending/search', methods=['POST'])
@admin_required
def admin_search_pending():
    """Rechercher des réservations en attente par nom"""
    search_term = request.form.get('search_term', '').strip()
    
    if not search_term:
        pending = ReservationPending.query.order_by(ReservationPending.created_at.desc()).all()
    else:
        pending = ReservationPending.query.filter(
            (ReservationPending.guest_name.ilike(f'%{search_term}%')) |
            (ReservationPending.nickname.ilike(f'%{search_term}%'))
        ).order_by(ReservationPending.created_at.desc()).all()
    
    return render_template('admin_pending.html', pending_reservations=pending, search_term=search_term)

@app.route('/admin/reservations/delete-range', methods=['POST'])
@admin_required
def admin_delete_reservations_range():
    """Supprimer toutes les réservations entre deux dates"""
    try:
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        
        count = Reservation.query.filter(
            Reservation.start_date >= start_date,
            Reservation.end_date <= end_date
        ).delete()
        
        db.session.commit()
        flash(f'Toutes les réservations entre {start_date} et {end_date} ont été supprimées ({count}).', 'info')
        logger.info(f"Suppression de réservations entre {start_date} et {end_date}: {count}")
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
        logger.error(f"Erreur lors de la suppression des réservations: {e}")
    
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        logger.info(f"Tentative de connexion pour: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            logger.info(f"Utilisateur trouvé: {user.username}, is_admin={user.is_admin}")
            
            if check_password_hash(user.password_hash, password):
                logger.info(f"✓ Mot de passe correct pour {username}")
                session['user_id'] = user.id
                session['username'] = user.username
                session['is_admin'] = user.is_admin
                flash('Connexion réussie !', 'success')
                redirect_url = url_for('admin') if user.is_admin else url_for('index')
                logger.info(f"Redirection vers: {redirect_url}")
                return redirect(redirect_url)
            else:
                logger.warning(f"✗ Mot de passe incorrect pour {username}")
        else:
            logger.warning(f"✗ Utilisateur non trouvé: {username}")
        
        flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie !', 'info')
    return redirect(url_for('index'))

# API pour récupérer les réservations (pour le calendrier JavaScript)
def update_expired_reservations():
    """Passer les réservations passées en statut 'expired' (Passée)"""
    today = date.today()
    
    # Marquer les réservations expirées
    expired_count = ReservationPending.query.filter(
        ReservationPending.end_date < today,
        ReservationPending.status == 'pending'
    ).update({'status': 'expired'})
    
    db.session.commit()
    
    if expired_count > 0:
        logger.info(f"Marcqué {expired_count} réservation(s) comme expirée(s)")
    
    return expired_count

@app.route('/api/reservations')
def api_reservations():
    """Récupérer UNIQUEMENT les réservations validées pour le calendrier"""
    # Passer automatiquement les réservations expirées
    update_expired_reservations()
    
    # Uniquement les réservations approuvées
    approved = Reservation.query.filter_by(status='approved').all()
    
    result = [{
        'id': r.id,
        'start_date': r.start_date.isoformat(),
        'end_date': r.end_date.isoformat(),
        'guest_name': r.guest_name,
        'status': 'validated',
        'type': 'approved'
    } for r in approved]
    
    return jsonify(result)

if __name__ == '__main__':
    # Configuration pour le développement
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'  # Debug activé par défaut en local
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # En production, initialiser les données
    if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('DATABASE_URL', '').startswith('postgres'):
        logger.info("Mode production détecté - Exécution de seed_data.py")
        try:
            import subprocess
            subprocess.run(['python', 'seed_data.py'], check=True)
        except Exception as e:
            logger.warning(f"seed_data.py déjà exécuté ou erreur: {e}")
    
    logger.info(f"Démarrage du serveur Flask - Debug: {debug_mode}")
    
    # Forcer l'affichage des logs Werkzeug dans le terminal
    import sys
    logging.getLogger('werkzeug').handlers = [logging.StreamHandler(sys.stdout)]
    
    app.run(debug=debug_mode, host=host, port=port, use_reloader=True)