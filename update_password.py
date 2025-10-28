#!/usr/bin/env python3
"""
Script pour mettre à jour le mot de passe admin
Usage: python update_password.py
"""

import os
import sys
from app import app, db, User
from werkzeug.security import generate_password_hash

def update_admin_password():
    """Met à jour le mot de passe admin"""
    print("=" * 80)
    print("MISE À JOUR DU MOT DE PASSE ADMIN")
    print("=" * 80)
    
    # Récupérer le mot de passe depuis les variables d'environnement
    admin_password = os.environ.get('ADMIN_MDP', 'Olo fais moi le Q !')
    print(f"\n[MOT DE PASSE] Utilisation de: {admin_password}")
    
    with app.app_context():
        try:
            # Chercher l'admin
            admin = User.query.filter_by(username='admin').first()
            
            if admin:
                print(f"\n[INFO] Utilisateur admin trouvé (ID: {admin.id})")
                
                # Générer le nouveau hash
                new_hash = generate_password_hash(admin_password)
                
                # Mettre à jour le mot de passe
                admin.password_hash = new_hash
                admin.is_admin = True
                db.session.commit()
                
                print("[✓] Mot de passe admin mis à jour avec succès !")
                print(f"\n[CONNEXION]")
                print(f"  Username: admin")
                print(f"  Password: {admin_password}")
                
            else:
                print("\n[✗] Aucun utilisateur admin trouvé")
                print("[INFO] Création d'un nouvel utilisateur admin...")
                
                admin = User(
                    username='admin',
                    email='admin@chez-meme.com',
                    password_hash=generate_password_hash(admin_password),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                
                print("[✓] Utilisateur admin créé avec succès !")
                print(f"\n[CONNEXION]")
                print(f"  Username: admin")
                print(f"  Password: {admin_password}")
            
            # Vérifier que ça marche
            print("\n[VERIFICATION] Test de vérification du mot de passe...")
            from werkzeug.security import check_password_hash
            test_user = User.query.filter_by(username='admin').first()
            if test_user and check_password_hash(test_user.password_hash, admin_password):
                print("[✓] Le mot de passe est correct et fonctionne !")
            else:
                print("[✗] ERREUR: Le mot de passe ne fonctionne pas")
            
            print("\n" + "=" * 80)
            print("[TERMINÉ]")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n[✗] ERREUR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    update_admin_password()


