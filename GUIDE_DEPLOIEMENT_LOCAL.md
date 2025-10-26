# 🚀 Guide de Déploiement Local - Chez Mémé

## ⚠️ Problème actuel
Vous avez Python 3.14 (version alpha) installé, ce qui cause des problèmes de compatibilité avec certains packages.

## ✅ Solutions rapides

### Option 1 : Démarrer l'application (Windows)

#### Étape 1 : Se placer dans le dossier du projet
```powershell
cd cheh_maienmaien
```

#### Étape 2 : Initialiser la base de données et démarrer
```powershell
python app.py
```

Cette commande va :
- Créer la base de données SQLite (`chez_meme.db`)
- Créer l'utilisateur admin par défaut
- Ajouter des activités exemple
- Démarrer le serveur Flask sur http://localhost:5000

#### Étape 3 : Accéder au site
Ouvrez votre navigateur sur : **http://localhost:5000**

#### Identifiants par défaut
- **URL admin** : http://localhost:5000/admin
- **Username** : `admin`
- **Password** : `admin123`

---

## 🔧 Si vous avez des erreurs

### Erreur : Packages manquants
```powershell
python -m pip install Flask Flask-SQLAlchemy SQLAlchemy
```

### Erreur : Python 3.14 incompatible
Installez Python 3.12 depuis : https://www.python.org/downloads/release/python-3120/

Après installation :
```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 app.py
```

---

## 📦 Alternative : Utiliser un environnement virtuel

### Créer l'environnement
```powershell
py -3.12 -m venv venv
```

### Activer l'environnement
```powershell
.\venv\Scripts\activate
```

### Installer les dépendances
```powershell
pip install -r requirements.txt
```

### Démarrer l'application
```powershell
python app.py
```

### Désactiver l'environnement
```powershell
deactivate
```

---

## 🎯 Fonctionnalités disponibles en local

1. **Page d'accueil** : http://localhost:5000
2. **Calendrier** : http://localhost:5000/calendrier
3. **Informations appartement** : http://localhost:5000/appartement
4. **Liste des activités** : http://localhost:5000/activites
5. **Réservation** : http://localhost:5000/reserver
6. **Admin** : http://localhost:5000/admin

---

## ⚙️ Configuration

### Variables d'environnement (optionnel)
Créez un fichier `.env` à la racine du projet :
```
SECRET_KEY=votre-clé-secrète
DATABASE_URL=sqlite:///chez_meme.db
EMAIL_USERNAME=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe
```

### Base de données
Par défaut, l'application utilise **SQLite** (fichier `chez_meme.db` dans le dossier `instance/`).

Pour PostgreSQL en local :
```powershell
$env:DATABASE_URL="postgresql://user:pass@localhost:5432/chez_meme"
python app.py
```

---

## 📧 Configuration email (optionnel)

Pour que les emails de réservation fonctionnent :

1. Gmail : Créez un **mot de passe d'application**
   - https://myaccount.google.com/apppasswords
   
2. Utilisez ce mot de passe dans le code ou un fichier `.env`

---

## 🛠️ Commandes utiles

### Réinitialiser la base de données
```powershell
# Supprimer le fichier de base de données
Remove-Item instance\chez_meme.db

# Redémarrer l'application (la BD sera recréée)
python app.py
```

### Mode debug
Le mode debug est déjà activé par défaut. Modifications = rechargement automatique.

---

## 🐛 Dépannage

### Port 5000 déjà utilisé
Changez le port dans `app.py` ligne 333 :
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Erreur "Module not found"
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --force-reinstall
```

### Base de données corrompue
```powershell
# Supprimer et recréer
Remove-Item instance\chez_meme.db
python app.py
```

---

## 📝 Résumé

**Commande la plus simple pour démarrer** :
```powershell
cd cheh_maienmaien
python app.py
```

Puis ouvrez : http://localhost:5000

**Admin** : http://localhost:5000/admin
- Username : `admin`
- Password : `admin123`
