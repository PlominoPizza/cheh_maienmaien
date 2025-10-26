# 🍵 Chez Mémé - Système de Réservation

Application web Flask pour gérer les réservations d'un appartement à Biarritz.

## 🚀 Déploiement Rapide sur Render

### 1. Configuration Render

Créez un nouveau **Web Service** sur Render et :

1. **Connectez votre dépôt Git**
2. **Définissez les variables d'environnement** :
   - `ADMIN_MDP` : Votre mot de passe admin
   - `SECRET_KEY` : Une clé secrète aléatoire (générez-en une avec `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `DATABASE_URL` : Fournie automatiquement par Render (PostgreSQL)
   - `FLASK_DEBUG` : `False` (pour la production)
   - `FLASK_HOST` : `0.0.0.0`
   - `FLASK_PORT` : `5000`

3. **Build Command** :
```bash
pip install -r requirements.txt && python seed_data.py
```

4. **Start Command** :
```bash
gunicorn -c gunicorn_config.py app:app
```

### 2. Accès Admin

- **URL** : `https://votre-app.onrender.com/`
- **Identifiant** : `admin`
- **Mot de passe** : Celui défini dans `ADMIN_MDP`

### 3. Gestion Locale

Pour le développement local :

```bash
# Installation
pip install -r requirements.txt

# Configuration admin (optionnel)
python update_admin_password.py

# Lancement
python app.py
```

## 📁 Structure

```
cheh_maienmaien/
├── app.py                  # Application Flask principale
├── seed_data.py           # Initialisation de la base de données
├── gunicorn_config.py     # Configuration Gunicorn (production)
├── requirements.txt       # Dépendances Python
├── render.yaml            # Configuration Render
├── Procfile               # Commande de démarrage
├── static/                # Fichiers statiques (CSS, JS, images)
└── templates/             # Templates HTML
```

## 🛠️ Fonctionnalités

- ✅ Réservation en ligne avec calendrier
- ✅ Gestion admin des réservations
- ✅ Gestion des photos de la maison
- ✅ Calendrier de disponibilités
- ✅ Protection contre les conflits de dates

## 🔐 Sécurité

- Les mots de passe sont hashés avec Werkzeug
- Session sécurisée avec `SECRET_KEY`
- Protection contre l'injection SQL (SQLAlchemy)
- Les uploads sont sécurisés (validation, nom unique)

## 📧 Contact

chez.meme.officiel@gmail.com

## 📝 License

Projet privé - Tous droits réservés
