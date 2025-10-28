# Migration : Ajout du système de statuts pour les réservations

## Changements apportés

### Nouveau système de statuts
- **En attente de validation** : Toute nouvelle réservation
- **Validée** : Réservation approuvée par l'admin
- **Passée** : Réservation avec dates passées

### Modification de la base de données

Le modèle `ReservationPending` a maintenant un champ `status` avec les valeurs possibles :
- `pending` : En attente de validation (par défaut)
- `approved` : Validée
- `expired` : Passée

## Migration de la base de données

Pour mettre à jour votre base de données locale, exécutez :

```bash
cd cheh_maienmaien
python
```

Puis dans le shell Python :

```python
from app import db, app
with app.app_context():
    # Créer les nouvelles tables et colonnes
    db.create_all()
    print("Base de données mise à jour !")
    print("Nouveau champ 'status' ajouté à ReservationPending")
```

## Fonctionnalités ajoutées

### 1. Captcha avec bouton désactivé
- Le bouton "Envoyer la demande" est désactivé tant que le captcha n'est pas complété
- Le bouton s'active automatiquement quand le captcha est résolu
- Le bouton se désactive si le captcha expire

### 2. Affichage dans le calendrier
- **Uniquement** les réservations avec statut "Validée" apparaissent dans le calendrier
- Les réservations en attente ne bloquent pas le calendrier

### 3. Gestion automatique des réservations passées
- Les réservations avec `end_date < aujourd'hui` passent automatiquement en statut "Passée" (`expired`)
- Cette vérification se fait automatiquement à chaque appel de l'API `/api/reservations`

### 4. Interface admin
- Affichage du statut pour chaque réservation en attente
- Badges colorés selon le statut :
  - ⏳ **En attente** : Jaune
  - ✅ **Validée** : Vert
  - ⏰ **Passée** : Gris

## Comportement du système

1. **Nouvelle réservation** :
   - Statut : `pending` (En attente de validation)
   - Demandée via le formulaire avec captcha
   - Non affichée dans le calendrier public

2. **Validation par l'admin** :
   - Cliquer sur "✅ Approuver" dans `/admin/pending`
   - Statut : `approved` (Validée)
   - Copie la réservation dans la table `Reservation`
   - **Affichée dans le calendrier**

3. **Réservation passée** :
   - Détection automatique des réservations avec `end_date < aujourd'hui`
   - Passage automatique en statut `expired` (Passée)
   - Non affichée dans le calendrier

4. **Calendrier** :
   - Affiche **uniquement** les réservations avec statut "Validée" (approved)
   - Les réservations passées ne s'affichent pas

