# Guide : Ajouter PostgreSQL sur Render

## 📋 Étape par étape

### Option 1 : Ajouter PostgreSQL quand vous créez votre Web Service

1. **Créez votre Web Service** (comme expliqué dans DEPLOIEMENT.md)

2. **Avant de cliquer sur "Create Web Service"**, allez dans la section **"Add Database"**

3. Cliquez sur **"Add PostgreSQL"**

4. Render va créer automatiquement :
   - Une base PostgreSQL gratuite
   - Une variable d'environnement `DATABASE_URL` 
   - Une variable `DATABASE_URL_POOL` pour le connection pooling

5. Puis cliquez sur **"Create Web Service"**

---

### Option 2 : Ajouter PostgreSQL après la création

Si vous avez déjà créé votre Web Service sans la database :

1. Allez sur votre dashboard Render

2. Dans la liste de vos services, cherchez votre application

3. Cliquez sur **"New +"** en haut à droite

4. Choisissez **"PostgreSQL"**

5. Configurez :
   - **Name** : `chez-meme-db` (ou autre nom)
   - **Database** : `chezmeme` (optionnel, Render en génère un)
   - **User** : Généré automatiquement
   - **Region** : `Frankfurt` (plus proche de la France)
   - **PostgreSQL Version** : `15` (la plus récente)

6. Dans **"Add Environment Variables"** → sélectionnez votre Web Service

7. Cliquez sur **"Create Database"**

8. Render va automatiquement ajouter la variable `DATABASE_URL` à votre Web Service

---

## 🔗 Connecter votre app à PostgreSQL

### Méthode automatique (si vous avez suivi les étapes ci-dessus)

Render ajoute automatiquement la variable `DATABASE_URL` à votre Web Service.

Votre code dans `app.py` va automatiquement utiliser PostgreSQL au lieu de SQLite grâce à cette configuration :

```python
# Dans app.py (déjà configuré)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///chez_meme.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
```

### Méthode manuelle (si besoin)

1. Allez dans votre **Web Service** sur Render
2. Cliquez sur l'onglet **"Environment"**
3. Cherchez la variable **`DATABASE_URL`** (générée automatiquement)
4. Copiez sa valeur
5. Si elle n'existe pas, cliquez **"Add Environment Variable"** → **Name**: `DATABASE_URL` → **Value**: copiez l'URL de votre database

---

## 🔍 Vérifier que PostgreSQL est bien connecté

1. Allez sur votre **PostgreSQL database** dans Render
2. Cliquez sur l'onglet **"Connections"**
3. Vous verrez les statistiques de connexion

### Via votre app

Le premier démarrage de votre app va initialiser les tables automatiquement grâce à cette fonction dans `app.py` :

```python
def init_db():
    with app.app_context():
        db.create_all()
        # ... création des données par défaut
```

Les logs de Render afficheront :
```
Base de données initialisée !
Admin par défaut: username='admin', password='admin123'
```

---

## 🔐 Récupérer les credentials PostgreSQL

Si vous avez besoin de connecter manuellement (avec un client SQL) :

1. Allez sur votre **PostgreSQL database** dans Render
2. Cliquez sur l'onglet **"Connections"**
3. Sous **"External Connection"**, vous verrez :
   - **Host**
   - **Port**
   - **Database**
   - **User**
   - **Password**

Vous pouvez utiliser ces infos avec des outils comme :
- **pgAdmin**
- **DBeaver**
- **DataGrip**
- Ou via la ligne de commande : `psql`

**URL de connexion complète :**
```
postgresql://user:password@host:5432/database
```

---

## 💡 Plan gratuit PostgreSQL sur Render

### Limitations du plan gratuit

- **90 jours rétention** des backups
- **RAM** : 256 MB
- **Disque** : 3 GB
- **Parfait pour votre app** 🎉

### Passage à un plan payant

Si vous atteignez les limites (rare pour une app de réservation) :

- **Starter Plan** : 7$/mois
  - 512 MB RAM
  - 10 GB disque
  - 180 jours backup

---

## 🛠️ Migrer de SQLite vers PostgreSQL

### En local (pour tester)

1. Installez PostgreSQL sur votre machine
2. Créez une base de données :
   ```bash
   createdb chezmeme
   ```

3. Modifiez votre `.env` :
   ```
   DATABASE_URL=postgresql://localhost:5432/chezmeme
   ```

4. Lancez l'app :
   ```bash
   python app.py
   ```

### Sur Render

Pas besoin de migrer manuellement ! Votre app va :
1. Se connecter à PostgreSQL
2. Créer les tables automatiquement au premier démarrage
3. Initialiser les données par défaut (admin, activités)

---

## ❓ Problèmes fréquents

### "PG::ConnectionBad" dans les logs

**Solution :** La variable `DATABASE_URL` n'est pas correctement configurée

1. Vérifiez que PostgreSQL est bien attaché à votre Web Service
2. Redéployez l'application

### Les données ne persistent pas

**Solution :** Assurez-vous que PostgreSQL est bien connecté et pas SQLite

1. Vérifiez les variables d'environnement
2. Regardez les logs au démarrage

### "OperationalError: could not connect to server"

**Solution :** La database est en veille

Sur le plan gratuit, Render met la database en veille après 90 jours d'inactivité
- Cliquez sur "Wake up" dans Render
- Attendez 2-3 minutes
- Redémarrez votre Web Service

---

## ✅ Checklist de déploiement

- [ ] Créez votre Web Service
- [ ] Ajoutez PostgreSQL (gratuit)
- [ ] `DATABASE_URL` est automatiquement ajouté
- [ ] Lancez le déploiement
- [ ] Vérifiez les logs - pas d'erreurs de connexion
- [ ] Testez l'app sur l'URL fournie

---

Bon déploiement ! 🚀

