#!/usr/bin/env python3
"""
Script pour migrer la colonne password_hash vers une taille plus grande
Usage: python migrate_password_hash.py
"""

import os
import sys
from app import app, db

def migrate_password_hash_column():
    """Migre la colonne password_hash de String(120) vers String(256)"""
    print("=" * 80)
    print("MIGRATION DE LA COLONNE password_hash")
    print("=" * 80)
    
    with app.app_context():
        try:
            database_url = os.environ.get('DATABASE_URL', 'sqlite:///chez_meme.db')
            print(f"\n[INFO] Database URL: {database_url[:50]}...")
            
            # Pour PostgreSQL
            if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
                print("\n[INFO] Détection PostgreSQL - Migration de la colonne...")
                
                # Modifier la colonne password_hash
                db.session.execute(db.text("""
                    ALTER TABLE "user" 
                    ALTER COLUMN password_hash TYPE VARCHAR(256);
                """))
                db.session.commit()
                
                print("[✓] Colonne password_hash mise à jour vers VARCHAR(256)")
                
            # Pour SQLite
            else:
                print("\n[INFO] Détection SQLite")
                print("[INFO] SQLite ne nécessite pas de modification - String(256) fonctionnera")
            
            print("\n" + "=" * 80)
            print("[TERMINÉ]")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n[✗] ERREUR: {e}")
            # Si l'erreur est "la colonne n'existe pas", c'est normal
            if "does not exist" in str(e) or "Unknown column" in str(e):
                print("[INFO] La colonne a peut-être déjà été migrée")
            else:
                import traceback
                traceback.print_exc()
                sys.exit(1)

if __name__ == '__main__':
    migrate_password_hash_column()

