#!/usr/bin/env python3
"""
Script pour forcer la mise à jour de l'admin
À exécuter manuellement ou via cron pour forcer la mise à jour du mot de passe admin
"""

import os
import sys
from werkzeug.security import generate_password_hash

def force_update_admin():
    """Force la mise à jour du mot de passe admin"""
    print("=" * 80)
    print("FORCE UPDATE ADMIN - Mise à jour forcée du mot de passe")
    print("=" * 80)
    
    # Importer app et db
    try:
        from app import app, db, User
    except ImportError as e:
        print(f"ERREUR: Impossible d'importer app: {e}")
        sys.exit(1)
    
    with app.app_context():
        # Récupérer le mot de passe depuis les variables d'environnement
        admin_password = os.environ.get('ADMIN_MDP', 'Olo fais moi le Q !')
        
        if not admin_password:
            print("[ERREUR] ADMIN_MDP n'est pas défini")
            sys.exit(1)
        
        print(f"\n[MOT DE PASSE] Utilisation de: {admin_password}")
        print(f"[LONGUEUR] {len(admin_password)} caractères")
        
        try:
            # Supprimer tous les admins existants
            print("\n[ETAPE 1] Suppression de tous les admins existants...")
            admins = User.query.filter_by(username='admin').all()
            if admins:
                for admin in admins:
                    print(f"  → Suppression de l'admin existant (ID: {admin.id})")
                    db.session.delete(admin)
                db.session.commit()
                print("[OK] Admins existants supprimés")
            else:
                print("[OK] Aucun admin existant trouvé")
            
            # Créer un nouvel admin avec le bon mot de passe
            print("\n[ETAPE 2] Création d'un nouvel admin...")
            new_hash = generate_password_hash(admin_password)
            print(f"  → Hash généré (longueur: {len(new_hash)})")
            
            new_admin = User(
                username='admin',
                email='admin@chez-meme.com',
                password_hash=new_hash,
                is_admin=True
            )
            
            db.session.add(new_admin)
            db.session.commit()
            
            print("[✓] Nouvel admin créé avec succès")
            
            # Vérifier que ça fonctionne
            print("\n[ETAPE 3] Vérification...")
            check_admin = User.query.filter_by(username='admin').first()
            
            if check_admin:
                print(f"[✓] Admin vérifié dans la base")
                print(f"    ID: {check_admin.id}")
                print(f"    Username: {check_admin.username}")
                print(f"    Email: {check_admin.email}")
                print(f"    is_admin: {check_admin.is_admin}")
                
                # Tester le hash
                from werkzeug.security import check_password_hash
                if check_password_hash(check_admin.password_hash, admin_password):
                    print("[✓] Le mot de passe fonctionne correctement !")
                else:
                    print("[✗] ERREUR: Le mot de passe ne fonctionne pas")
                    sys.exit(1)
            else:
                print("[✗] ERREUR: Admin non trouvé après création")
                sys.exit(1)
            
            print("\n" + "=" * 80)
            print("[SUCCÈS] Admin mis à jour avec succès !")
            print("=" * 80)
            print(f"\n[CONNEXION]")
            print(f"  URL: https://cheh-maienmaien.onrender.com/login")
            print(f"  Username: admin")
            print(f"  Password: {admin_password}")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n[✗] ERREUR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    force_update_admin()

