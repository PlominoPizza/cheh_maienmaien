# 🔐 Gestion Sécurisée des Identifiants Admin

## ⚠️ IMPORTANT : Sécurité

**NE JAMAIS** committer les mots de passe ou les secrets dans le code source !

## 🛠️ Configuration de l'Admin

### Option 1 : Variables d'environnement (Recommandé)

1. Créer un fichier `.env` à la racine du projet :
```bash
ADMIN_MDP=VotreMotDePasseSecurise123
SECRET_KEY=cle-secrete-tres-longue-et-aleatoire
DATABASE_URL=sqlite:///chez_meme.db
```

2. Le fichier `.env` est automatiquement ignoré par Git (déjà dans `.gitignore`)

### Option 2 : Script sécurisé

Utiliser le script `update_admin_password.py` pour configurer l'admin :

```bash
python update_admin_password.py
```

Le script vous demandera de saisir le mot de passe de manière sécurisée (sans affichage).

## 🚀 Pour Production

En production (ex: Render), définissez les variables d'environnement dans les paramètres du service :

- `ADMIN_MDP` : Votre mot de passe admin
- `SECRET_KEY` : Une clé secrète aléatoire
- `DATABASE_URL` : URL de la base de données (fournie par Render pour PostgreSQL)

## 📝 Identifiants Admin

- **Identifiant** : `admin`
- **Mot de passe** : Défini par `ADMIN_MDP` (variable d'environnement)

## 🔒 Bonnes Pratiques

1. ✅ Utiliser des mots de passe forts (min. 12 caractères, mixte)
2. ✅ Ne jamais partager les `.env` 
3. ✅ Utiliser des secrets différents en développement et production
4. ✅ Régénérer les clés secrètes après un commit accidentel
5. ✅ Surveiller les logs d'accès

## 🆘 En cas de compromission

Si vous avez accidentellement commité un secret :

1. **Immediate** : Changer tous les mots de passe
2. Rendre la clé secrète invalide
3. Nettoyer l'historique Git si nécessaire
4. Signaler le problème

