#!/usr/bin/env python3
"""
Script pour créer ou mettre à jour l'utilisateur admin
Usage: python create_admin.py
"""

import os
import sys
from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        print("=" * 60)
        print("CRÉATION DE L'UTILISATEUR ADMIN")
        print("=" * 60)
        
        # Récupérer le mot de passe depuis les variables d'environnement
        admin_password = os.environ.get('ADMIN_MDP')
        
        if not admin_password:
            print("\n[ERREUR] ADMIN_MDP n'est pas défini")
            print("Définissez ADMIN_MDP dans les variables d'environnement")
            sys.exit(1)
        
        print(f"\n[MOT DE PASSE] Utilisation du mot de passe depuis ADMIN_MDP")
        print(f"[LONGUEUR] {len(admin_password)} caractères")
        print(f"[PREMIERS CHARS] {admin_password[:5]}...")
        
        # Chercher l'admin existant
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            print(f"\n[EXISTANT] Utilisateur admin trouvé (ID: {admin_user.id})")
            # Mettre à jour le mot de passe
            admin_user.password_hash = generate_password_hash(admin_password)
            admin_user.is_admin = True
            db.session.commit()
            print("[OK] Mot de passe admin mis à jour avec le hash sécurisé")
        else:
            # Créer l'admin
            admin_user = User(
                username='admin',
                email='admin@chez-meme.com',
                password_hash=generate_password_hash(admin_password),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("[OK] Utilisateur admin créé avec succès")
        
        print("\n" + "=" * 60)
        print("[CONNEXION] Vous pouvez maintenant vous connecter avec :")
        print(f"  Identifiant: admin")
        print(f"  Mot de passe: {admin_password}")
        print("=" * 60)

if __name__ == '__main__':
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\nOpération annulée.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


