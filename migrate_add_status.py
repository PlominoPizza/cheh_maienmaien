#!/usr/bin/env python3
"""Script de migration pour ajouter la colonne status à reservation_pending"""
from app import app, db, ReservationPending

with app.app_context():
    # Créer toutes les tables si elles n'existent pas
    db.create_all()
    
    try:
        # Ajouter la colonne status si elle n'existe pas
        from sqlalchemy import text
        
        # Vérifier si la colonne existe
        result = db.session.execute(
            text("PRAGMA table_info(reservation_pending)")
        ).fetchall()
        
        columns = [col[1] for col in result]
        
        if 'status' not in columns:
            print("Ajout de la colonne 'status' à la table reservation_pending...")
            db.session.execute(text("ALTER TABLE reservation_pending ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"))
            db.session.commit()
            print("Colonne 'status' ajoutee avec succes!")
        else:
            print("La colonne 'status' existe deja")
        
        # Créer les tables si elles n'existent pas
        db.create_all()
        print("Base de données mise à jour!")
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

