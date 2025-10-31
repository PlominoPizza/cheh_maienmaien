# 🚀 Guide de Déploiement - Chez Mémé

## 📋 Checklist de Déploiement

### 1. Préparer le code
- [x] Code source nettoyé et optimisé
- [x] Fichiers inutiles supprimés
- [x] Dependencies vérifiées

### 2. Configuration Render

#### Variables d'environnement requises :

```bash
# Sécurité
ADMIN_MDP=VotreMotDePasseSecurise123
SECRET_KEY=votre-cle-secrete-generee-aleatoirement

# Base de données (fourni automatiquement par Render)
DATABASE_URL=postgresql://...

# Cloudinary - Stockage persistant des images
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=votre-api-key
CLOUDINARY_API_SECRET=votre-api-secret

# Configuration Flask
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Configuration Gunicorn (optionnel)
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
```

#### Générer une SECRET_KEY :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Commandes Render

**Build Command** :
```bash
pip install -r requirements.txt && python seed_data.py
```

**Start Command** :
```bash
gunicorn -c gunicorn_config.py app:app
```

### 4. Configuration Initiale

1. Déploiement de l'application
2. Accéder à `/admin` avec les identifiants :
   - Identifiant : `admin`
   - Mot de passe : Valeur de `ADMIN_MDP`
3. Gérer les photos depuis l'interface admin

## 🔧 Maintenance

### Changer le mot de passe admin en production

1. Connectez-vous via SSH ou la console Render
2. Exécutez :
```bash
python update_admin_password.py
```

### Ajouter des photos

Via l'interface admin : `/admin/photos`

### Configuration Cloudinary (Recommandé)

**⚠️ Important** : Render en version gratuite utilise un système de fichiers éphémère. Les photos disparaîtront après chaque redémarrage du site.

**Solution** : Utilisez Cloudinary pour un stockage persistant gratuit (25 GB stockage + 25 GB bande passante/mois).

1. Créez un compte sur [cloudinary.com](https://cloudinary.com/)
2. Récupérez vos credentials (Cloud name, API Key, API Secret)
3. Ajoutez-les comme variables d'environnement dans Render (voir ci-dessus)

**Voir** `README_CLOUDINARY.md` pour plus de détails.

## 📊 Monitoring

- Logs disponibles dans le dashboard Render
- Métriques de performance incluses
- Alertes automatiques en cas de crash

## 🆘 Support

En cas de problème :
1. Vérifiez les logs dans Render
2. Vérifiez les variables d'environnement
3. Contactez le support


