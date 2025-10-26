# Chez Mémé - Site de Réservation de Collocation

## 🏠 Description

Site web pour la gestion des réservations de la chambre d'amis dans la collocation "Chez Mémé". 
Un projet fun et moderne pour faire marrer les amis tout en gérant efficacement les réservations !

## ✨ Fonctionnalités

- **📅 Calendrier interactif** : Visualisation des disponibilités et réservations
- **🛏️ Système de réservation** : Demande de réservation avec validation admin
- **👑 Interface admin** : Gestion des réservations et validation
- **🏠 Présentation de l'appart** : Galerie photos et plan interactif
- **🏃‍♂️ Activités locales** : Surf, VTT, randonnée, escalade
- **📱 Design responsive** : Compatible mobile et desktop

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Lancement du serveur
```bash
python app.py
```

Le site sera accessible à l'adresse : `http://localhost:5000`

## 🔑 Connexion Admin

- **Utilisateur** : `admin`
- **Mot de passe** : `admin123`

⚠️ **Important** : Changez ces identifiants en production !

## 📁 Structure du projet

```
chez_meme/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── chez_meme.db          # Base de données SQLite (créée automatiquement)
├── templates/            # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── calendrier.html
│   ├── reserver.html
│   ├── appartement.html
│   ├── activites.html
│   ├── admin.html
│   └── login.html
└── static/               # Assets statiques
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── main.js
    │   ├── calendar.js
    │   ├── reservation.js
    │   ├── apartment.js
    │   ├── activities.js
    │   └── admin.js
    └── images/           # Images (à ajouter)
```

## 🎯 Utilisation

### Pour les invités
1. Consultez le calendrier pour voir les disponibilités
2. Cliquez sur "Réserver" pour faire une demande
3. Remplissez le formulaire avec vos informations
4. Attendez la validation de l'admin

### Pour l'admin
1. Connectez-vous avec les identifiants admin
2. Consultez les réservations en attente
3. Approuvez ou rejetez les demandes
4. Gérez le calendrier et les activités

## 🛠️ Personnalisation

### Modifier les activités
Éditez le fichier `app.py` dans la fonction `init_db()` pour ajouter/modifier les activités.

### Changer les couleurs
Modifiez les variables CSS dans `static/css/style.css` :
```css
:root {
    --primary-color: #6366f1;    /* Couleur principale */
    --secondary-color: #8b5cf6;  /* Couleur secondaire */
    --accent-color: #06b6d4;     /* Couleur d'accent */
}
```

### Ajouter des images
Placez vos images dans le dossier `static/images/` et mettez à jour les références dans les templates.

## 🔧 Développement

### Base de données
La base de données SQLite est créée automatiquement au premier lancement.
Pour la réinitialiser, supprimez le fichier `chez_meme.db`.

### Mode debug
Le serveur Flask est lancé en mode debug par défaut pour faciliter le développement.

### Logs
Les erreurs et informations sont affichées dans la console.

## 📝 Notes

- Le site est optimisé pour être fun et décontracté
- Tous les textes sont en français
- Le design est moderne et responsive
- Les animations sont fluides et engageantes

## 🎉 Amusez-vous bien !

Ce projet a été créé avec ❤️ pour faire marrer vos amis tout en gérant efficacement votre collocation.

---

*"Chez Mémé, où l'ambiance est toujours au rendez-vous !"* 🏠✨
