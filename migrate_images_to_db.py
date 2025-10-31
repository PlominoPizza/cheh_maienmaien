#!/usr/bin/env python3
"""
Script de migration pour ajouter les colonnes nécessaires au stockage d'images en base de données.
À exécuter une seule fois après le déploiement des nouvelles modifications.
"""

import os
import sys
from sqlalchemy import text
from app import app, db, Photo, WallOfShame, Leaderboard

def migrate_database():
    """Ajoute les colonnes nécessaires pour le stockage d'images en DB"""
    with app.app_context():
        try:
            # Vérifier le type de base de données
            database_url = os.environ.get('DATABASE_URL', 'sqlite:///chez_meme.db')
            is_postgresql = database_url.startswith('postgresql://') or database_url.startswith('postgres://')
            
            from app import logger
            logger.info("=" * 60)
            logger.info("Migration : Ajout des colonnes pour stockage images en DB")
            logger.info("=" * 60)
            
            # Migration pour la table Photo
            try:
                inspector = db.inspect(db.engine)
                photo_columns = [col['name'] for col in inspector.get_columns('photo')]
                
                if 'image_token' not in photo_columns:
                    if is_postgresql:
                        db.session.execute(text("ALTER TABLE photo ADD COLUMN image_token VARCHAR(64)"))
                        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_photo_image_token ON photo(image_token)"))
                        logger.info("✓ Colonne image_token ajoutée à la table photo")
                    else:
                        logger.warning("SQLite ne supporte pas ALTER TABLE ADD COLUMN. Utilisez migrate_db.py")
                
                if 'image_data' not in photo_columns:
                    if is_postgresql:
                        db.session.execute(text("ALTER TABLE photo ADD COLUMN image_data BYTEA"))
                        logger.info("✓ Colonne image_data ajoutée à la table photo")
                    else:
                        logger.warning("SQLite ne supporte pas ALTER TABLE ADD COLUMN")
                
                if 'mime_type' not in photo_columns:
                    if is_postgresql:
                        db.session.execute(text("ALTER TABLE photo ADD COLUMN mime_type VARCHAR(50)"))
                        logger.info("✓ Colonne mime_type ajoutée à la table photo")
                    else:
                        logger.warning("SQLite ne supporte pas ALTER TABLE ADD COLUMN")
                        
            except Exception as e:
                logger.warning(f"Erreur lors de la migration de la table photo: {e}")
            
            # Migration pour la table wall_of_shame
            try:
                inspector = db.inspect(db.engine)
                wall_columns = [col['name'] for col in inspector.get_columns('wall_of_shame')]
                
                if 'image_token' not in wall_columns:
                    if is_postgresql:
                        db.session.execute(text("ALTER TABLE wall_of_shame ADD COLUMN image_token VARCHAR(64)"))
                        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_wall_of_shame_image_token ON wall_of_shame(image_token)"))
                        logger.info("✓ Colonne image_token ajoutée à la table wall_of_shame")
                
                if 'image_data' not in wall_columns:
                    if is_postgresql:
                        db.session.execute(text("ALTER TABLE wall_of_shame ADD COLUMN image_data BYTEA"))
                        logger.info("✓ Colonne image_data ajoutée à la table wall_of_shame")
                
                if 'mime_type' not in wall_columns:
                    if is_postgresql:
                        db.session.execute(text("ALTER TABLE wall_of_shame ADD COLUMN mime_type VARCHAR(50)"))
                        logger.info("✓ Colonne mime_type ajoutée à la table wall_of_shame")
                        
            except Exception as e:
                logger.warning(f"Erreur lors de la migration de la table wall_of_shame: {e}")
            
            # Migration pour la table leaderboard
            try:
                inspector = db.inspect(db.engine)
                leader_columns = [col['name'] for col in inspector.get_columns('leaderboard')]
                
                if 'image_token' not in leader_columns:
                    if is_postgresql:
                        db.session.execute(text("ALTER TABLE leaderboard ADD COLUMN image_token VARCHAR(64)"))
                        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_leaderboard_image_token ON leaderboard(image_token)"))
                        logger.info("✓ Colonne image_token ajoutée à la table leaderboard")
                
                if 'image_data' not in leader_columns:
                    if is_postgresql:
                        db.session.execute(text("ALTER TABLE leaderboard ADD COLUMN image_data BYTEA"))
                        logger.info("✓ Colonne image_data ajoutée à la table leaderboard")
                
                if 'mime_type' not in leader_columns:
                    if is_postgresql:
                        db.session.execute(text("ALTER TABLE leaderboard ADD COLUMN mime_type VARCHAR(50)"))
                        logger.info("✓ Colonne mime_type ajoutée à la table leaderboard")
                        
            except Exception as e:
                logger.warning(f"Erreur lors de la migration de la table leaderboard: {e}")
            
            db.session.commit()
            logger.info("=" * 60)
            logger.info("Migration terminée avec succès !")
            logger.info("=" * 60)
            logger.info("\nLes nouvelles images seront automatiquement stockées en base de données.")
            logger.info("Les anciennes images (si elles existent) continueront de fonctionner via le système de fichiers.")
            
        except Exception as e:
            logger.error(f"Erreur lors de la migration: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    migrate_database()

