# Solution pour développement local avec Python 3.14

## Problème
Python 3.14 (version alpha) a des problèmes de compatibilité avec plusieurs packages.

## Solutions

### Option 1 : Installer Python 3.12 (Recommandé)
1. Télécharger Python 3.12 depuis https://www.python.org/downloads/
2. Désinstaller Python 3.14
3. Installer Python 3.12
4. Installer les dépendances : `python -m pip install -r requirements.txt`

### Option 2 : Utiliser venv avec Python 3.12
Si vous avez Python 3.12 installé côte à côte :
```powershell
# Trouver l'exécutable Python 3.12
py -3.12 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Option 3 : Utiliser Docker
Utiliser Python 3.12 dans un container Docker.

## Importante pour Render
Les modifications effectuées (runtime.txt, render.yaml, pyproject.toml) assurent que **Render utilisera Python 3.12** lors du déploiement, donc **le déploiement devrait maintenant fonctionner** sur Render.

Pour tester maintenant :
1. Commit et push les changements
2. Le build devrait réussir sur Render avec Python 3.12
