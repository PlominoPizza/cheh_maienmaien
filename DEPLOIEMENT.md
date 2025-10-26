# Guide de Déploiement - Chez Mémé 🚀

## 🌟 Solutions Freemium Recommandées

### 1. **Render** (⭐ RECOMMANDÉ - Le plus simple)

**Avantages :**
- ✅ Plan gratuit généreux (500h/mois)
- ✅ PostgreSQL gratuit inclus
- ✅ SSL automatique
- ✅ Pas de carte bancaire requise
- ✅ Déploiement en 5 minutes

**Guide de déploiement sur Render :**

1. Créez un compte sur [render.com](https://render.com)
2. Cliquez sur "New +" → "Web Service"
3. Connectez votre repository GitHub
4. Configurez :
   - **Name** : `chez-meme`
   - **Environment** : `Python 3`
   - **Root Directory** : `cheh_maienmaien`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`
5. Sous "Environment", ajoutez :
   - `SECRET_KEY` : générez une clé secrète aléatoire
   - `PYTHON_VERSION` : `3.10.0`
6. Cliquez sur "Create Web Service"

**Important :** Pour SQLite avec upload d'images :
- Les fichiers sont stockés dans le filesystem éphemère
- Les données persistent entre les redémarrages
- Pour la persistance à long terme, migrez vers PostgreSQL (gratuit sur Render)

---

### 2. **Railway** 

**Avantages :**
- ✅ Plan gratuit : 500h/mois + 5$ crédit
- ✅ Database PostgreSQL gratuite
- ✅ Déploiement instantané depuis GitHub
- ✅ Variables d'environnement faciles

**Guide de déploiement sur Railway :**

1. Créez un compte sur [railway.app](https://railway.app)
2. Cliquez sur "New Project" → "Deploy from GitHub repo"
3. Sélectionnez votre repository
4. Railway détecte automatiquement votre app Flask
5. Ajoutez une database PostgreSQL (gratuite) si vous migrez de SQLite
6. Configurez les variables d'environnement
7. Railway déploie automatiquement

**Note :** Adaptez votre code pour PostgreSQL si besoin

---

### 3. **PythonAnywhere**

**Avantages :**
- ✅ Plan gratuit pour débuter
- ✅ Console Python intégrée
- ✅ Simplicité de déploiement

**Limitations :**
- 1 app web gratuite
- 1 Go d'espace stockage
- URL : `votreapp.pythonanywhere.com`
- Pas de support custom domain gratuit

**Guide de déploiement sur PythonAnywhere :**

1. Créez un compte sur [pythonanywhere.com](https://www.pythonanywhere.com)
2. Ouvrez la console Bash
3. Clonez votre repository :
   ```bash
   git clone https://github.com/votreusername/votre-repo.git
   cd votre-repo/cheh_maienmaien
   ```
4. Installez les dépendances :
   ```bash
   pip3.10 install --user -r requirements.txt
   ```
5. Allez dans "Web" → "Add a new web app"
6. Choisissez "Flask" et Python 3.10
7. Modifiez le fichier WSGI dans l'éditeur :
   ```python
   import sys
   path = '/home/votreusername/votre-repo/cheh_maienmaien'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import app as application
   ```
8. Redémarrez l'application

---

### 4. **Fly.io**

**Avantages :**
- ✅ Plan gratuit généreux
- ✅ Déploiement rapide
- ✅ Support des volumes persistants

**Guide de déploiement sur Fly.io :**

1. Installez `flyctl` : 
   ```bash
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. Créez un compte : `fly auth signup`

3. Créez un `fly.toml` :
   ```toml
   app = "votre-app-name"
   primary_region = "cdg"  # Paris

   [build]

   [env]
     PYTHON_VERSION = "3.10"

   [[services]]
     http_checks = []
     internal_port = 5000
     processes = ["app"]
     protocol = "tcp"
     script_checks = []

   [[services.ports]]
     force_https = true
     handlers = ["http"]
     port = 80

   [[services.ports]]
     handlers = ["tls", "http"]
     port = 443

   [services.concurrency]
     hard_limit = 25
     soft_limit = 20

   [[services.tcp_checks]]
     grace_period = "1s"
     interval = "15s"
     restart_limit = 0
     timeout = "2s"
   ```

4. Déployez : `fly deploy`

---

## 🔄 Migration de SQLite vers PostgreSQL (Recommandé pour production)

Pour Render et Railway, je recommande de migrer vers PostgreSQL pour la persistance.

### Modifications nécessaires :

1. Modifiez `app.py` :

```python
import os

# Utiliser PostgreSQL en production, SQLite en local
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chez_meme.db'
```

2. Ajoutez `psycopg2-binary` à requirements.txt :
```
psycopg2-binary==2.9.9
```

3. Sur Render :
   - Créez une base PostgreSQL gratuite
   - Copiez le "Internal Database URL"
   - Ajoutez-le comme variable d'environnement `DATABASE_URL`

---

## 🔧 Configuration des Variables d'Environnement

Sur toutes les plateformes, ajoutez :

```
SECRET_KEY=votre-cle-secrete-super-longue-et-aleatoire
EMAIL_USERNAME=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-application
EMAIL_RECIPIENTS=email1@example.com,email2@example.com
DATABASE_URL=postgresql://user:pass@host:5432/db (optionnel)
```

---

## 📧 Configuration Email pour SMTP

Pour l'envoi d'emails en production, vous pouvez utiliser :

- **Gmail** (déjà configuré dans votre app)
- **SendGrid** (plan gratuit : 100 emails/jour)
- **Mailgun** (plan gratuit : 5000 emails/mois)
- **Brevo (ex-Sendinblue)** (plan gratuit : 300 emails/jour)

Modifiez les credentials dans votre code ou utilisez des variables d'environnement.

---

## 🎯 Recommandation Finale

**Pour débuter rapidement :** Render.com 🏆
- Le plus simple
- Déploiement automatique depuis GitHub
- SSL gratuit
- Pas de configuration complexe

**Étapes rapides avec Render :**
1. Poussez votre code sur GitHub
2. Connectez GitHub à Render
3. Ajoutez gunicorn (déjà fait dans requirements.txt)
4. Déployez !
5. URL : `https://votre-app.onrender.com`

---

## ⚠️ Notes Importantes

- **Ne commitez JAMAIS** vos credentials email dans le code
- Utilisez les variables d'environnement pour les secrets
- Sur les plateformes gratuites, l'application se met en veille après 15 min d'inactivité
- Le premier démarrage peut prendre 30-50 secondes
- Pensez à changer le mot de passe admin par défaut !

---

Bon déploiement ! 🚀


