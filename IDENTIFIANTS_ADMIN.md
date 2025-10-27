# Identifiants de connexion Admin

## 🔐 Identifiants par défaut

**Utilisateur** : `admin`

**Mot de passe** : Défini via la variable d'environnement `ADMIN_MDP` sur Render

Actuellement configuré : `Olo fais moi le Q !`

## 🚀 Étapes pour déployer sur Render

### 1. Configuration des variables d'environnement sur Render

Assurez-vous d'avoir ces variables configurées dans votre Web Service sur Render :

```
ADMIN_MDP=Olo fais moi le Q !
SECRET_KEY=changez-moi-en-production
DATABASE_URL=<URL de PostgreSQL configurée automatiquement>
```

### 2. Déploiement

Les modifications apportées permettront :

1. **Création automatique des tables** au premier démarrage
2. **Création automatique de l'admin** si `ADMIN_MDP` est défini
3. **Logs détaillés** pour diagnostiquer les problèmes

### 3. Connexion

1. Visitez votre URL Render (ex: `https://votre-app.onrender.com`)
2. Allez sur `/admin/login`
3. Utilisez :
   - Username : `admin`
   - Password : `Olo fais moi le Q !`

## 🐛 Si vous ne pouvez toujours pas vous connecter

### Vérification des logs

Consultez les logs de votre application sur Render. Vous devriez voir :

```
Tables de base de données créées/vérifiées.
Utilisateur admin trouvé dans la base de données
```

OU

```
Utilisateur admin créé automatiquement
```

### Vérification dans la base de données

Si vous avez accès à la console PostgreSQL sur Render :

```sql
SELECT username, is_admin FROM "user" WHERE username = 'admin';
```

Si l'admin n'existe pas, la prochaine requête devrait le créer automatiquement.

### Script de secours

Vous pouvez aussi exécuter manuellement :

```bash
python create_admin.py
```

Cela créera ou mettra à jour l'admin avec le mot de passe depuis `ADMIN_MDP`.

## ⚠️ Sécurité

**Important** : Changez le mot de passe après le premier login !

Pour cela, vous pouvez :
1. Modifier `ADMIN_MDP` sur Render
2. Exécuter `python create_admin.py` pour mettre à jour l'admin

