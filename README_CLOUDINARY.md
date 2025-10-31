# 📸 Configuration Cloudinary - Persistance des Images

## 📋 Problème résolu

Avec Render en version gratuite, le système de fichiers est **éphémère**. Cela signifie que les fichiers (comme les photos) disparaissent lorsque le site redémarre ou s'éteint.

**Solution implémentée** : Utilisation de Cloudinary pour stocker les images de manière persistante.

## ✅ Avantages de Cloudinary

- **Gratuit** : 25 GB de stockage + 25 GB de bande passante/mois
- **Persistant** : Les images restent disponibles même après redémarrage
- **CDN intégré** : Images servies rapidement depuis le monde entier
- **Optimisation automatique** : Redimensionnement et compression
- **Sécurisé** : HTTPS et URLs signées

## 🔧 Configuration

### 1. Créer un compte Cloudinary

1. Allez sur [cloudinary.com](https://cloudinary.com/)
2. Créez un compte gratuit
3. Récupérez vos credentials depuis le dashboard

### 2. Ajouter les variables d'environnement sur Render

Dans le dashboard Render, ajoutez ces variables d'environnement :

```bash
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=votre-api-key
CLOUDINARY_API_SECRET=votre-api-secret
```

**Où trouver ces valeurs** :
1. Connectez-vous à votre dashboard Cloudinary
2. La page d'accueil affiche :
   - Cloud name
   - API Key
   - API Secret (cliquez pour afficher)

### 3. Redéployer

Après avoir ajouté les variables d'environnement :
1. Redéployez votre service Render (rebuild automatique)
2. Les photos seront maintenant stockées sur Cloudinary !

## 🎯 Fonctionnement

### Mode automatique
Le système détecte automatiquement si Cloudinary est configuré :
- ✅ **Cloudinary disponible** : Upload et stockage sur Cloudinary
- ⚠️ **Cloudinary non configuré** : Retombe sur le stockage local (temporaire)

### Structures de dossiers Cloudinary
- **Photos d'accueil** : `chez_meme/photos/`
- **Wall of Shame** : `chez_meme/wall-of-shame/`
- **Leaderboard** : `chez_meme/leaderboard/`

### Migration des anciennes images

Les anciennes images stockées localement resteront fonctionnelles en mode local, mais :
1. Redémarrez le site (images locales disparaissent)
2. Uploadez de nouvelles images via `/admin/photos`
3. Les nouvelles images sont stockées sur Cloudinary

## 🔍 Dépannage

### Les images ne s'affichent pas

1. **Vérifiez que Cloudinary est bien configuré** :
   ```bash
   # Dans les logs Render, cherchez :
   "✓ Cloudinary configuré et disponible"
   ```

2. **Vérifiez les variables d'environnement** :
   - `CLOUDINARY_CLOUD_NAME` doit être défini
   - `CLOUDINARY_API_KEY` doit être défini
   - `CLOUDINARY_API_SECRET` doit être défini

3. **Vérifiez les limites du plan gratuit** :
   - Stockage : 25 GB
   - Bandwidth : 25 GB/mois

### Logs utiles

```python
# Vous verrez dans les logs :
"Cloudinary configuré et disponible"  # ✅ OK
"Cloudinary non configuré - utilisation du système de fichiers local"  # ⚠️ Pas configuré
"Image uploadée vers Cloudinary: public_id"  # ✅ Upload réussi
"Erreur lors de l'upload Cloudinary: ..."  # ❌ Erreur
```

## 📊 Suivi d'utilisation

Dans votre dashboard Cloudinary :
1. **Usage** : Consultez votre utilisation actuelle
2. **Media Library** : Voir toutes les images uploadées
3. **Analytics** : Statistiques de bande passante

## 💰 Coûts (Plan Gratuit)

- **Gratuit pour** :
  - 25 GB de stockage
  - 25 GB de bande passante/mois
  - 25 MB max par fichier
  
- **Si vous dépassez les limites** :
  - Vous serez notifié par email
  - Options d'upgrade disponibles sur cloudinary.com

## 🔐 Sécurité

- Les images sont servies en HTTPS
- URLs signées pour plus de sécurité
- Pas de stockage sur le serveur éphémère
- Config par variables d'environnement (sécurisé)

## 📝 Notes

- Les anciennes images téléversées avant l'activation de Cloudinary ne fonctionneront plus après redémarrage
- Il faut les retéléverser via `/admin/photos`
- Les nouvelles images sont automatiquement sur Cloudinary

## 🚀 Prochaines étapes (optionnel)

Pour optimiser davantage :
1. **Transformation d'images** : Utiliser les transformations Cloudinary (redimensionnement à la volée)
2. **Cache** : Améliorer les performances avec un cache CDN
3. **Backup** : Activer les backups automatiques

---

**✅ Configuration terminée !** Vos photos resteront visibles même après redémarrage de Render.



