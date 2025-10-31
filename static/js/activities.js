// Gestion des activités et filtres
class ActivitiesManager {
    constructor() {
        this.activities = [];
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.loadActivities();
        this.bindEvents();
        this.initAnimations();
    }

    loadActivities() {
        // Les activités sont déjà chargées côté serveur
        this.activities = Array.from(document.querySelectorAll('.activity-card'));
    }

    bindEvents() {
        // Gestion des filtres
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleFilterClick(e.target);
            });
        });

        // Gestion des boutons d'action des activités
        document.querySelectorAll('.activity-card .btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleActivityAction(e.target);
            });
        });
    }

    handleFilterClick(button) {
        // Mettre à jour l'état actif
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        // Appliquer le filtre
        this.currentFilter = button.dataset.filter;
        this.filterActivities();
    }

    filterActivities() {
        this.activities.forEach(activity => {
            const activityType = activity.dataset.type;
            
            if (this.currentFilter === 'all' || activityType === this.currentFilter) {
                activity.style.display = 'block';
                activity.style.animation = 'fadeInUp 0.6s ease';
            } else {
                activity.style.display = 'none';
            }
        });

        // Mettre à jour le compteur d'activités
        this.updateActivityCount();
    }

    updateActivityCount() {
        const visibleActivities = this.activities.filter(activity => 
            activity.style.display !== 'none'
        ).length;

        const countElement = document.querySelector('.activities-count');
        if (countElement) {
            countElement.textContent = `${visibleActivities} activité${visibleActivities > 1 ? 's' : ''} trouvée${visibleActivities > 1 ? 's' : ''}`;
        }
    }

    handleActivityAction(button) {
        const action = button.textContent.trim();
        const activityCard = button.closest('.activity-card');
        const activityName = activityCard.querySelector('h3').textContent;

        switch (action) {
            case 'Plus d\'infos':
                this.showActivityDetails(activityCard);
                break;
            case 'Itinéraire':
                this.showRoute(activityName);
                break;
        }
    }

    showActivityDetails(activityCard) {
        const name = activityCard.querySelector('h3').textContent;
        const description = activityCard.querySelector('p').textContent;
        const metaItems = activityCard.querySelectorAll('.meta-item');
        
        let details = `<h4>${name}</h4><p>${description}</p>`;
        
        metaItems.forEach(item => {
            const icon = item.querySelector('i').className;
            const text = item.textContent.trim();
            details += `<p><i class="${icon}"></i> ${text}</p>`;
        });

        window.ChezMemeUtils.showNotification(details, 'info');
    }

    showRoute(activityName) {
        // Simulation d'un itinéraire (à remplacer par une vraie intégration)
        const routes = {
            'Plage de la Côte Sauvage': 'Prendre la D123 vers l\'ouest, puis suivre les panneaux "Plage"',
            'Forêt de Fontainebleau': 'Prendre l\'A6 direction Paris, sortie Fontainebleau',
            'Sentier des Crêtes': 'Suivre le GR5 depuis le centre-ville',
            'Rocher de l\'Aigle': 'Prendre la route forestière après le village de Montagne'
        };

        const route = routes[activityName] || 'Itinéraire non disponible';
        window.ChezMemeUtils.showNotification(`Itinéraire vers ${activityName}: ${route}`, 'info');
    }

    initAnimations() {
        // Animation d'apparition des activités
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        this.activities.forEach(activity => {
            activity.style.opacity = '0';
            activity.style.transform = 'translateY(30px)';
            activity.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(activity);
        });
    }
}

// Gestion des activités populaires
class PopularActivities {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initRatingAnimation();
    }

    bindEvents() {
        // Gestion des clics sur les activités populaires
        document.querySelectorAll('.popular-item').forEach(item => {
            item.addEventListener('click', () => {
                this.showPopularActivityDetails(item);
            });
        });
    }

    showPopularActivityDetails(item) {
        const title = item.querySelector('h3').textContent;
        const description = item.querySelector('p').textContent;
        const stats = item.querySelectorAll('.popular-stats span');
        
        let details = `<h4>${title}</h4><p>${description}</p>`;
        
        stats.forEach(stat => {
            details += `<p>${stat.innerHTML}</p>`;
        });

        window.ChezMemeUtils.showNotification(details, 'info');
    }

    initRatingAnimation() {
        // Animation des étoiles de notation
        document.querySelectorAll('.popular-stats .fa-star').forEach(star => {
            star.addEventListener('mouseenter', () => {
                star.style.color = '#fbbf24';
                star.style.transform = 'scale(1.2)';
                star.style.transition = 'all 0.3s ease';
            });

            star.addEventListener('mouseleave', () => {
                star.style.color = '';
                star.style.transform = 'scale(1)';
            });
        });
    }
}

// Gestion des équipements
class EquipmentManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initEquipmentAnimation();
    }

    bindEvents() {
        // Gestion des interactions avec les équipements
        document.querySelectorAll('.equipment-category').forEach(category => {
            category.addEventListener('mouseenter', () => {
                this.highlightEquipment(category);
            });
        });
    }

    highlightEquipment(category) {
        category.style.transform = 'translateY(-5px)';
        category.style.boxShadow = 'var(--shadow-lg)';
        category.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            category.style.transform = 'translateY(0)';
            category.style.boxShadow = 'var(--shadow)';
        }, 2000);
    }

    initEquipmentAnimation() {
        // Animation d'apparition des équipements
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.equipment-category').forEach(category => {
            category.style.opacity = '0';
            category.style.transform = 'translateY(20px)';
            category.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(category);
        });
    }
}

// Initialisation des composants
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.activities-section')) {
        new ActivitiesManager();
        new PopularActivities();
        new EquipmentManager();
    }
});
