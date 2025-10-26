#!/usr/bin/env python3
# Script pour améliorer les légendes des photos

import os
import sys
from app_simple import app, db, Photo

def improve_captions():
    """Améliore les légendes des photos avec des descriptions plus appropriées"""
    
    with app.app_context():
        photos = Photo.query.order_by(Photo.display_order).all()
        
        print(f"Amélioration des légendes pour {len(photos)} photos...")
        
        # Légendes améliorées
        improved_captions = [
            "Vue d'ensemble de la maison",
            "Séjour et coin détente", 
            "Cuisine équipée",
            "Chambre principale",
            "Terrasse et jardin",
            "Vue sur Biarritz"
        ]
        
        for i, photo in enumerate(photos):
            if i < len(improved_captions):
                old_caption = photo.caption
                photo.caption = improved_captions[i]
                print(f"Photo {i+1}: '{old_caption}' -> '{improved_captions[i]}'")
        
        db.session.commit()
        print("\nLégendes améliorées avec succès!")
        
        # Afficher le résultat
        print("\nPhotos avec nouvelles légendes:")
        for photo in photos:
            print(f"  - {photo.filename} : '{photo.caption}'")

if __name__ == '__main__':
    improve_captions()

