// Gestion de la galerie d'appartement
class ApartmentGallery {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initVirtualTour();
    }

    bindEvents() {
        // Gestion des clics sur les photos
        document.querySelectorAll('.photo-item img').forEach(img => {
            img.addEventListener('click', (e) => {
                this.openPhotoModal(e.target.src, e.target.alt);
            });
        });

        // Gestion du modal des photos
        const modal = document.getElementById('photoModal');
        const closeButton = modal?.querySelector('.close');

        if (closeButton) {
            closeButton.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }

        if (modal) {
            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }

        // Gestion des interactions avec le plan
        document.querySelectorAll('.plan-room').forEach(room => {
            room.addEventListener('click', () => {
                this.highlightRoom(room);
            });
        });
    }

    openPhotoModal(src, alt) {
        const modal = document.getElementById('photoModal');
        const modalImage = document.getElementById('modalImage');
        const modalCaption = document.getElementById('modalCaption');

        if (modal && modalImage && modalCaption) {
            modalImage.src = src;
            modalCaption.textContent = alt;
            modal.style.display = 'block';
        }
    }

    highlightRoom(roomElement) {
        // Retirer la surbrillance des autres pièces
        document.querySelectorAll('.plan-room').forEach(room => {
            room.classList.remove('highlighted');
        });

        // Ajouter la surbrillance à la pièce cliquée
        roomElement.classList.add('highlighted');

        // Afficher des informations sur la pièce
        this.showRoomInfo(roomElement.textContent.trim());

        // Retirer la surbrillance après 3 secondes
        setTimeout(() => {
            roomElement.classList.remove('highlighted');
        }, 3000);
    }

    showRoomInfo(roomName) {
        const roomInfo = {
            'Salon': 'Espace de détente principal avec canapé, TV et coin lecture',
            'Cuisine': 'Cuisine équipée avec tous les ustensiles nécessaires',
            'Chambre Principale': 'Chambre principale avec lit double et dressing',
            'Chambre d\'Amis': 'Chambre d\'accueil avec lit double et bureau',
            'Salle de Bain': 'Salle de bain complète avec douche et WC',
            'Terrasse': 'Terrasse privée avec mobilier de jardin'
        };

        const info = roomInfo[roomName] || 'Pièce de l\'appartement';
        window.ChezMemeUtils.showNotification(info, 'info');
    }

    initVirtualTour() {
        // Simulation d'une visite virtuelle (à remplacer par une vraie implémentation)
        const tourButton = document.querySelector('.tour-placeholder button');
        if (tourButton) {
            tourButton.addEventListener('click', () => {
                this.startVirtualTour();
            });
        }
    }

    startVirtualTour() {
        // Animation de transition vers la visite virtuelle
        const tourContainer = document.querySelector('.tour-container');
        if (tourContainer) {
            tourContainer.style.transition = 'all 0.5s ease';
            tourContainer.style.transform = 'scale(1.05)';
            
            setTimeout(() => {
                tourContainer.style.transform = 'scale(1)';
                window.ChezMemeUtils.showNotification('Visite virtuelle bientôt disponible !', 'info');
            }, 500);
        }
    }
}

// Gestion des spécifications de l'appartement
class ApartmentSpecs {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initSpecsAnimation();
    }

    bindEvents() {
        // Animation au survol des spécifications
        document.querySelectorAll('.spec-item').forEach(item => {
            item.addEventListener('mouseenter', () => {
                this.animateSpecItem(item);
            });
        });
    }

    animateSpecItem(item) {
        item.style.transform = 'translateX(10px)';
        item.style.transition = 'transform 0.3s ease';
        
        setTimeout(() => {
            item.style.transform = 'translateX(0)';
        }, 300);
    }

    initSpecsAnimation() {
        // Animation d'apparition des spécifications
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.spec-item').forEach(item => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(item);
        });
    }
}

// Gestion des interactions avec la galerie
class GalleryInteractions {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initLazyLoading();
    }

    bindEvents() {
        // Gestion du clavier pour la navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    initLazyLoading() {
        // Chargement paresseux des images
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Initialisation des composants
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.apartment-gallery')) {
        new ApartmentGallery();
        new ApartmentSpecs();
        new GalleryInteractions();
    }
});
