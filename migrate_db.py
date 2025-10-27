#!/usr/bin/env python3
"""
Script de migration de la base de données
Gère les changements de schéma de manière seamless
Version: 2.0.0
"""

import os
import sys
from app import app, db
from sqlalchemy import inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migre la base de données vers la nouvelle version"""
    with app.app_context():
        logger.info("=" * 60)
        logger.info("MIGRATION DE LA BASE DE DONNEES")
        logger.info("=" * 60)
        
        try:
            # Vérifier l'état actuel de la base de données
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            logger.info(f"Tables existantes: {existing_tables}")
            
            # Créer toutes les tables si elles n'existent pas
            logger.info("\n1. Verification/creation des tables principales...")
            db.create_all()
            
            # Ajouter les nouvelles tables si elles n'existent pas
            if 'leaderboard' in existing_tables:
                logger.info("\n2. Migration de la table Leaderboard...")
                # Vérifier si la colonne image_url existe
                columns = [col['name'] for col in inspector.get_columns('leaderboard')]
                
                if 'image_url' not in columns:
                    logger.info("   Ajout de la colonne 'image_url' à la table Leaderboard")
                    db.session.execute(db.text("""
                        ALTER TABLE leaderboard 
                        ADD COLUMN image_url VARCHAR(200)
                    """))
                    db.session.commit()
                    logger.info("   Colonne 'image_url' ajoutée avec succès")
                else:
                    logger.info("   Colonne 'image_url' déjà présente")
            
            if 'wall_of_shame' in existing_tables:
                logger.info("\n3. Migration de la table WallOfShame...")
                columns = [col['name'] for col in inspector.get_columns('wall_of_shame')]
                
                if 'display_order' not in columns:
                    logger.info("   Ajout de la colonne 'display_order'")
                    db.session.execute(db.text("""
                        ALTER TABLE wall_of_shame 
                        ADD COLUMN display_order INTEGER DEFAULT 0
                    """))
                    db.session.commit()
                    logger.info("   Colonne ajoutée avec succès")
            
            logger.info("\n" + "=" * 60)
            logger.info("Migration terminee avec succes")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"\nErreur lors de la migration: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    try:
        migrate_database()
    except KeyboardInterrupt:
        logger.info("\n\nMigration annulee.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

