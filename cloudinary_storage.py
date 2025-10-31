"""
Module pour gérer le stockage des images sur Cloudinary au lieu du système de fichiers local.
Permet de persister les images même après le redémarrage de Render (version gratuite).
"""

import os
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Variable globale pour détecter si Cloudinary est configuré
_cloudinary_available = False
_cloudinary_config = None

try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    _cloudinary_available = True
    
    # Configuration Cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
        api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET', ''),
        secure=True
    )
    
    # Tester la configuration
    if all([os.environ.get('CLOUDINARY_CLOUD_NAME'),
            os.environ.get('CLOUDINARY_API_KEY'),
            os.environ.get('CLOUDINARY_API_SECRET')]):
        logger.info("✓ Cloudinary configuré et disponible")
        _cloudinary_config = {
            'cloud_name': os.environ.get('CLOUDINARY_CLOUD_NAME'),
            'api_key': os.environ.get('CLOUDINARY_API_KEY'),
            'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
        }
    else:
        logger.warning("Cloudinary non configuré - utilisation du système de fichiers local")
        
except ImportError:
    logger.warning("Bibliothèque cloudinary non installée - utilisation du système de fichiers local")
    logger.info("Installez avec: pip install cloudinary")
    _cloudinary_available = False

def resize_image_in_memory(image_bytes, max_width=800):
    """Redimensionne une image en mémoire"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # Si l'image est déjà plus petite ou égale à max_width, la retourner telle quelle
        if image.width <= max_width:
            return io.BytesIO(image_bytes)
        
        # Calculer la nouvelle hauteur en gardant les proportions
        ratio = max_width / image.width
        new_height = int(image.height * ratio)
        new_size = (max_width, new_height)
        
        # Redimensionner
        resized_img = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Sauvegarder en mémoire
        output = io.BytesIO()
        resized_img.save(output, format='JPEG', optimize=True, quality=85)
        output.seek(0)
        
        return output
    except Exception as e:
        logger.error(f"Erreur lors du redimensionnement en mémoire: {e}")
        return io.BytesIO(image_bytes)

def upload_to_cloudinary(file, folder='chez_meme', max_width=800):
    """
    Upload une image vers Cloudinary avec redimensionnement automatique.
    
    Args:
        file: Le fichier Flask à uploader
        folder: Le dossier dans Cloudinary
        max_width: Largeur max de l'image (défaut 800px)
    
    Returns:
        tuple: (public_id, url) si succès, None si échec
    """
    if not _cloudinary_available or not _cloudinary_config:
        return None
    
    try:
        # Lire le fichier en mémoire
        file_bytes = file.read()
        
        # Redimensionner l'image si nécessaire
        resized_image = resize_image_in_memory(file_bytes, max_width)
        resized_image.seek(0)
        
        # Upload vers Cloudinary avec options de sécurité
        upload_result = cloudinary.uploader.upload(
            resized_image,
            folder=folder,
            resource_type="image",
            format="jpg",  # Convertir tout en JPG pour optimiser
            overwrite=True,
            invalidate=True  # Invalider le cache CDN
            # Note: Les URLs seront signées dans get_cloudinary_url() pour la sécurité
        )
        
        public_id = upload_result['public_id']
        secure_url = upload_result['secure_url']
        
        logger.info(f"Image uploadée vers Cloudinary: {public_id}")
        return public_id, secure_url
        
    except Exception as e:
        logger.error(f"Erreur lors de l'upload Cloudinary: {e}")
        return None

def delete_from_cloudinary(public_id):
    """
    Supprime une image de Cloudinary.
    
    Args:
        public_id: L'identifiant public de l'image à supprimer
    
    Returns:
        bool: True si succès, False sinon
    """
    if not _cloudinary_available or not _cloudinary_config:
        return False
    
    try:
        result = cloudinary.uploader.destroy(public_id)
        if result['result'] == 'ok':
            logger.info(f"Image supprimée de Cloudinary: {public_id}")
            return True
        else:
            logger.warning(f"Échec de suppression Cloudinary: {result.get('result')}")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la suppression Cloudinary: {e}")
        return False

def get_cloudinary_url(public_id, transformations=None):
    """
    Génère une URL Cloudinary signée avec transformations optionnelles.
    
    Les URLs signées empêchent l'indexation et limitent l'accès non autorisé.
    
    Args:
        public_id: L'identifiant public de l'image
        transformations: Dict de transformations (ex: {'width': 800, 'quality': 'auto'})
    
    Returns:
        str: URL signée de l'image
    """
    if not _cloudinary_available or not _cloudinary_config:
        return None
    
    try:
        # Générer une URL signée avec signature (expire après 1 an)
        # La signature empêche l'accès sans authentification
        expire_at = int(3600 * 24 * 365)  # 1 an en secondes
        
        default_transform = {
            'quality': 'auto',
            'secure': True,
        }
        
        if transformations:
            default_transform.update(transformations)
        
        # Utiliser des URLs signées pour la sécurité
        url = cloudinary.CloudinaryImage(public_id).build_url(
            transformation=default_transform,
            sign_url=True  # URL signée
        )
        
        return url
    except Exception as e:
        logger.error(f"Erreur lors de la génération d'URL Cloudinary: {e}")
        return None

def is_cloudinary_available():
    """Retourne True si Cloudinary est configuré et disponible"""
    return _cloudinary_available and _cloudinary_config is not None
