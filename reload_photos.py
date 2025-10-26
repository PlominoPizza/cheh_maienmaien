#!/usr/bin/env python3
# Script pour recharger les photos depuis le dossier uploads

import os
import sys
from app_simple import app, db, Photo

def reload_photos():
    """Recharge toutes les photos du dossier uploads dans la base de données"""
    
    with app.app_context():
        # Dossier des images
        upload_folder = 'static/uploads/images'
        
        if not os.path.exists(upload_folder):
            print(f"Dossier {upload_folder} introuvable")
            return
        
        # Lister tous les fichiers images
        image_files = []
        for filename in os.listdir(upload_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                image_files.append(filename)
        
        print(f"Images trouvées dans le dossier: {len(image_files)}")
        
        if not image_files:
            print("Aucune image trouvée")
            return
        
        # Supprimer les anciennes entrées
        Photo.query.delete()
        print("Anciennes entrées supprimées")
        
        # Ajouter chaque image à la base de données
        for i, filename in enumerate(sorted(image_files)):
            # Créer une légende par défaut basée sur le nom du fichier
            caption = f"Photo {i+1}"
            
            photo = Photo(
                filename=filename,
                caption=caption,
                display_order=i
            )
            
            db.session.add(photo)
            print(f"Ajouté: {filename} - Légende: {caption}")
        
        # Sauvegarder
        db.session.commit()
        print(f"\n{len(image_files)} photos rechargées avec succès!")
        
        # Afficher le résumé
        photos = Photo.query.order_by(Photo.display_order).all()
        print("\nPhotos dans la base de données:")
        for photo in photos:
            print(f"  - {photo.filename} : '{photo.caption}'")

if __name__ == '__main__':
    reload_photos()
