# Changelog

## [2.0.0] - 2025-01-XX

### Ajouté
- Système de versionning automatique
- Wall of Shame - page publique et gestion admin
- Leaderboard avec classement - page publique et gestion admin
- Support d'upload de photos pour le Leaderboard
- Améliorations responsive design pour tous les écrans
- Système de migrations de base de données
- Optimisations pour la production

### Modifié
- Navigation principale : ajout des onglets Activités, Wall of Shame, Leaderboard
- Footer simplifié (suppression section "Mes liens")
- Page admin login : texte de rappel modifié
- Leaderboard : nombre de "nuits" au lieu de "visites"
- Wall of Shame : nouveau texte avec call-to-action
- Texte et styles améliorés pour une meilleure lisibilité

### Optimisé
- Images avec `max-width: 100%` et `object-fit` pour un meilleur scaling
- Boutons responsive avec `flex-wrap` et tailles adaptatives
- Media queries améliorées pour mobile et tablettes
- Code Python réorganisé pour faciliter les mises à jour futures

### Compatibilité
- Compatible avec les versions précédentes de la base de données (migration automatique)
- Anciennes réservations préservées
- Photos existantes conservées

