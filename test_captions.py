#!/usr/bin/env python3
# Script de test pour vérifier les légendes

import os
import sys
from app_simple import app, db, Photo

def test_captions():
    """Teste la sauvegarde et modification des légendes"""
    
    with app.app_context():
        print("=== Test des légendes ===")
        
        # Afficher les photos actuelles
        photos = Photo.query.all()
        print(f"\nPhotos actuelles ({len(photos)}):")
        for photo in photos:
            print(f"  ID: {photo.id}, Fichier: {photo.filename}, Légende: '{photo.caption}'")
        
        if photos:
            # Tester la modification d'une légende
            first_photo = photos[0]
            old_caption = first_photo.caption
            new_caption = f"Légende modifiée pour {first_photo.filename}"
            
            print(f"\nModification de la légende:")
            print(f"  Avant: '{old_caption}'")
            
            first_photo.caption = new_caption
            db.session.commit()
            
            # Vérifier la modification
            updated_photo = Photo.query.get(first_photo.id)
            print(f"  Après: '{updated_photo.caption}'")
            
            if updated_photo.caption == new_caption:
                print("  OK - Modification réussie!")
            else:
                print("  ERREUR - Modification échouée!")
            
            # Restaurer l'ancienne légende
            updated_photo.caption = old_caption
            db.session.commit()
            print(f"  Restauré: '{updated_photo.caption}'")
        
        print("\n=== Fin du test ===")

if __name__ == '__main__':
    test_captions()
