# Configuration hCaptcha pour les réservations

## 1. Obtenir les clés hCaptcha

1. Créez un compte sur [hCaptcha](https://www.hcaptcha.com/)
2. Créez un nouveau site
3. Récupérez votre **Site Key** et votre **Secret Key**

## 2. Configurer les variables d'environnement

Ajoutez ces variables dans votre fichier `.env` :

```bash
HCAPTCHA_SITE_KEY=votre_site_key
HCAPTCHA_SECRET_KEY=votre_secret_key
```

Ou exportez-les dans votre terminal :

```bash
export HCAPTCHA_SITE_KEY="votre_site_key"
export HCAPTCHA_SECRET_KEY="votre_secret_key"
```

## 3. Mettre à jour la base de données

Après avoir ajouté le modèle `ReservationPending`, mettez à jour votre base de données :

```bash
python
```

```python
from app import db, app
with app.app_context():
    db.create_all()
    print("Base de données mise à jour !")
```

## 4. Fonctionnalités

### Système de modération des réservations

- **Captcha**: Toutes les demandes de réservation doivent compléter un captcha
- **Validation admin**: Les réservations sont envoyées dans une file d'attente pour validation
- **Gestion des attaques**: Outil de suppression rapide par dates dans l'espace admin

### Espace admin - Réservations en attente

Accédez à `/admin/pending` pour voir toutes les réservations en attente de validation.

**Fonctionnalités disponibles :**
- ✅ Approuver une réservation
- ❌ Rejeter une réservation
- 🔍 Rechercher par nom/prénom ou surnom
- 🗑️ Supprimer toutes les réservations en attente
- 🗑️ Supprimer les réservations entre deux dates (dans l'espace admin principal)

### Informations de sécurité

Chaque réservation en attente enregistre :
- Adresse IP
- User Agent (navigateur)
- Date et heure de la demande
- Nom complet et surnom

## 5. Désactiver le captcha (développement)

Si vous souhaitez désactiver le captcha en développement, laissez simplement les variables d'environnement vides. Le système retournera `True` automatiquement si les clés ne sont pas configurées.

**Attention :** Ne désactivez jamais le captcha en production !




