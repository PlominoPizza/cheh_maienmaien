#!/usr/bin/env python3
"""
Script pour mettre à jour le mot de passe de l'utilisateur admin
Usage: python update_admin_password.py
"""

import os
import sys
from getpass import getpass
from app import app, db, User
from werkzeug.security import generate_password_hash

def main():
    with app.app_context():
        print("=" * 60)
        print("Mise à jour du mot de passe admin")
        print("=" * 60)
        
        # Vérifier si l'admin existe
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("\n[ERREUR] Utilisateur 'admin' introuvable.")
            print("Création de l'utilisateur admin...")
            
            # Utiliser le mot de passe depuis l'environnement ou demander
            password = os.environ.get('ADMIN_MDP')
            if not password:
                print("\nVeuillez entrer un nouveau mot de passe:")
                password = getpass()
            
            admin_user = User(
                username='admin',
                email='admin@chez-meme.com',
                password_hash=generate_password_hash(password),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("[OK] Utilisateur admin créé avec succès!")
        else:
            print("\nUtilisateur admin trouvé.")
            print("\nVeuillez entrer le nouveau mot de passe:")
            password = getpass()
            
            if not password:
                print("[ERREUR] Le mot de passe ne peut pas être vide.")
                sys.exit(1)
            
            # Demander confirmation
            print("\nVeuillez confirmer le mot de passe:")
            confirm_password = getpass()
            
            if password != confirm_password:
                print("[ERREUR] Les mots de passe ne correspondent pas.")
                sys.exit(1)
            
            # Mettre à jour le mot de passe
            admin_user.password_hash = generate_password_hash(password)
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("[OK] Mot de passe admin mis à jour avec succès!")
            print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOpération annulée.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

