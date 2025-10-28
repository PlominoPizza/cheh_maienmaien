#!/usr/bin/env python3
"""
Script à exécuter manuellement pour créer/mettre à jour l'admin sur Render
Usage: Dans Render, ajouter une commande release : python create_admin_render.py
"""

import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash

# Importer app et db seulement si nécessaire
try:
    from app import app, db, User
except ImportError:
    print("ERREUR: Impossible d'importer app")
    sys.exit(1)

def create_or_update_admin():
    """Crée ou met à jour l'admin avec le mot de passe depuis ADMIN_MDP"""
    print("=" * 80)
    print("CRÉATION/MISE À JOUR DE L'ADMIN")
    print("=" * 80)
    
    # Récupérer le mot de passe depuis les variables d'environnement
    admin_password = os.environ.get('ADMIN_MDP')
    
    if not admin_password:
        print("\n[ERREUR] ADMIN_MDP n'est pas défini dans les variables d'environnement")
        print("Définissez ADMIN_MDP sur Render avec le mot de passe voulu")
        return False
    
    print(f"\n[MOT DE PASSE] Longueur: {len(admin_password)} caractères")
    
    with app.app_context():
        try:
            # Créer les tables si nécessaire
            db.create_all()
            print("\n[✓] Tables vérifiées/créées")
            
            # Chercher l'admin existant
            admin_user = User.query.filter_by(username='admin').first()
            
            # Générer le nouveau hash
            new_hash = generate_password_hash(admin_password)
            print(f"\n[INFO] Nouveau hash généré (longueur: {len(new_hash)})")
            
            if admin_user:
                print(f"\n[INFO] Admin existant trouvé (ID: {admin_user.id})")
                print(f"  Username: {admin_user.username}")
                print(f"  Email: {admin_user.email}")
                print(f"  is_admin: {admin_user.is_admin}")
                
                # Vérifier si le mot de passe correspond déjà
                if check_password_hash(admin_user.password_hash, admin_password):
                    print("\n[INFO] Le mot de passe actuel est correct")
                    return True
                
                # Mettre à jour le mot de passe
                print("\n[INFO] Mise à jour du mot de passe...")
                admin_user.password_hash = new_hash
                admin_user.is_admin = True  # S'assurer qu'il est admin
                db.session.commit()
                print("[✓] Mot de passe admin mis à jour")
                
            else:
                print("\n[INFO] Aucun admin trouvé, création d'un nouvel admin...")
                admin_user = User(
                    username='admin',
                    email='admin@chez-meme.com',
                    password_hash=new_hash,
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("[✓] Nouveau admin créé avec succès")
            
            # Vérifier que ça fonctionne
            print("\n[VERIFICATION] Test du mot de passe...")
            test_user = User.query.filter_by(username='admin').first()
            if test_user and check_password_hash(test_user.password_hash, admin_password):
                print("[✓] Mot de passe vérifié et fonctionne !")
            else:
                print("[✗] ERREUR: Le mot de passe ne fonctionne pas")
                return False
            
            # Afficher les informations finales
            print("\n" + "=" * 80)
            print("[CONNEXION]")
            print(f"  URL: https://cheh-maienmaien.onrender.com/admin/login")
            print(f"  Username: admin")
            print(f"  Password: {admin_password}")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n[✗] ERREUR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = create_or_update_admin()
    sys.exit(0 if success else 1)


