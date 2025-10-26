"""
Script de seed pour initialiser la base de données avec les données existantes
Usage: python seed_data.py
"""
import os
import sys
from app import app, db, Photo, Activity, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_photos():
    """Ajoute les photos existantes dans le dossier static/uploads/images/"""
    print("[PHOTOS] Synchronisation des photos...")
    
    upload_dir = 'static/uploads/images'
    
    if not os.path.exists(upload_dir):
        print(f"[ERREUR] Dossier {upload_dir} non trouvé")
        return
    
    images = [f for f in os.listdir(upload_dir) 
              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    
    if not images:
        print("[INFO] Aucune image à synchroniser")
        return
    
    print(f"[INFO] Trouvé {len(images)} image(s)")
    
    added_count = 0
    for i, img in enumerate(images):
        # Vérifier si l'image existe déjà
        existing = Photo.query.filter_by(filename=img).first()
        if existing:
            print(f"[EXISTE] {img}")
            continue
        
        # Ajouter l'image
        photo = Photo(
            filename=img,
            caption=f"Image {i+1}",
            display_order=i
        )
        db.session.add(photo)
        added_count += 1
        print(f"[AJOUTE] {img}")
    
    if added_count > 0:
        db.session.commit()
        print(f"[OK] {added_count} nouvelle(s) photo(s) ajoutée(s)")
    else:
        print("[OK] Toutes les photos sont déjà en base")

def seed_admin():
    """Crée l'utilisateur admin si nécessaire"""
    print("\n[ADMIN] Synchronisation de l'admin...")
    
    admin_password = os.environ.get('ADMIN_MDP')
    if not admin_password:
        print("[ERREUR] ADMIN_MDP non défini dans les variables d'environnement")
        print("[INFO] Utilisez 'python update_admin_password.py' pour créer l'admin")
        return
    
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@chez-meme.com',
            password_hash=generate_password_hash(admin_password),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("[OK] Utilisateur admin créé")
    else:
        # Mettre à jour le mot de passe si l'admin existe déjà
        admin_user.password_hash = generate_password_hash(admin_password)
        db.session.commit()
        print("[OK] Mot de passe admin mis à jour")

def seed_activities():
    """Ajoute les activités par défaut si nécessaire"""
    print("\n[ACTIVITES] Synchronisation des activités...")
    
    if Activity.query.count() > 0:
        print("[EXISTE] Activités déjà présentes")
        return
    
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
    print("[OK] Activités par défaut ajoutées")

def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("SEED DATA - Initialisation de la base de données")
    print("=" * 80)
    
    with app.app_context():
        try:
            # Créer les tables
            db.create_all()
            print("\n[OK] Tables créées/vérifiées")
            
            # Séed des données
            seed_admin()
            seed_activities()
            seed_photos()
            
            print("\n" + "=" * 80)
            print("[TERMINE] Données initialisées avec succès!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n[ERREUR] {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()
