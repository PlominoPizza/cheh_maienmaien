// Gestion de l'interface admin
class AdminDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initStatsAnimation();
        this.initAutoRefresh();
    }

    bindEvents() {
        // Gestion des actions de réservation
        document.querySelectorAll('.reservation-actions .btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleReservationAction(e.target);
            });
        });

        // Gestion des actions rapides
        document.querySelectorAll('.action-card').forEach(card => {
            card.addEventListener('click', (e) => {
                this.handleQuickAction(card);
            });
        });

        // Gestion de la recherche dans le tableau
        this.initTableSearch();
    }

    handleReservationAction(button) {
        const action = button.textContent.trim();
        const reservationCard = button.closest('.reservation-card');
        const reservationId = this.extractReservationId(reservationCard);

        if (action.includes('Approuver')) {
            this.approveReservation(reservationId, reservationCard);
        } else if (action.includes('Rejeter')) {
            this.rejectReservation(reservationId, reservationCard);
        }
    }

    extractReservationId(card) {
        // Extraire l'ID de la réservation depuis l'URL du bouton
        const approveBtn = card.querySelector('a[href*="approve"]');
        if (approveBtn) {
            const href = approveBtn.getAttribute('href');
            const match = href.match(/approve\/(\d+)/);
            return match ? match[1] : null;
        }
        return null;
    }

    async approveReservation(reservationId, card) {
        if (!reservationId) return;

        try {
            const response = await fetch(`/admin/approve/${reservationId}`);
            if (response.ok) {
                this.updateReservationStatus(card, 'approved');
                window.ChezMemeUtils.showNotification('Réservation approuvée !', 'success');
            } else {
                throw new Error('Erreur lors de l\'approbation');
            }
        } catch (error) {
            console.error('Erreur:', error);
            window.ChezMemeUtils.showNotification('Erreur lors de l\'approbation', 'error');
        }
    }

    async rejectReservation(reservationId, card) {
        if (!reservationId) return;

        try {
            const response = await fetch(`/admin/reject/${reservationId}`);
            if (response.ok) {
                this.updateReservationStatus(card, 'rejected');
                window.ChezMemeUtils.showNotification('Réservation rejetée', 'info');
            } else {
                throw new Error('Erreur lors du rejet');
            }
        } catch (error) {
            console.error('Erreur:', error);
            window.ChezMemeUtils.showNotification('Erreur lors du rejet', 'error');
        }
    }

    updateReservationStatus(card, status) {
        // Mettre à jour l'apparence de la carte
        card.classList.remove('pending', 'approved', 'rejected');
        card.classList.add(status);

        // Mettre à jour la bordure
        const borderColors = {
            'approved': '#10b981',
            'rejected': '#ef4444',
            'pending': '#f59e0b'
        };
        card.style.borderLeftColor = borderColors[status];

        // Masquer les boutons d'action
        const actions = card.querySelector('.reservation-actions');
        if (actions) {
            actions.style.display = 'none';
        }

        // Ajouter un indicateur de statut
        const statusIndicator = document.createElement('div');
        statusIndicator.className = 'status-indicator';
        statusIndicator.innerHTML = `
            <i class="fas fa-${status === 'approved' ? 'check' : 'times'}-circle"></i>
            ${status === 'approved' ? 'Approuvée' : 'Rejetée'}
        `;
        statusIndicator.style.cssText = `
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: ${status === 'approved' ? '#10b981' : '#ef4444'};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        `;
        card.style.position = 'relative';
        card.appendChild(statusIndicator);
    }

    handleQuickAction(card) {
        const title = card.querySelector('h3').textContent;
        
        switch (title) {
            case 'Voir le calendrier':
                window.location.href = '/calendrier';
                break;
            case 'Gérer les activités':
                window.location.href = '/activites';
                break;
            case 'Exporter les données':
                this.exportData();
                break;
            case 'Paramètres':
                this.showSettings();
                break;
        }
    }

    exportData() {
        // Simulation d'export de données
        window.ChezMemeUtils.showNotification('Export en cours...', 'info');
        
        setTimeout(() => {
            // Créer un fichier CSV simulé
            const csvContent = this.generateCSV();
            this.downloadCSV(csvContent, 'reservations.csv');
            window.ChezMemeUtils.showNotification('Export terminé !', 'success');
        }, 2000);
    }

    generateCSV() {
        const headers = ['ID', 'Invitée', 'Email', 'Date début', 'Date fin', 'Statut', 'Demandé par', 'Date demande'];
        const rows = Array.from(document.querySelectorAll('.reservation-row')).map(row => {
            const cells = row.querySelectorAll('td');
            return [
                cells[0]?.textContent || '',
                cells[1]?.textContent || '',
                cells[2]?.textContent || '',
                cells[3]?.textContent || '',
                cells[4]?.textContent || '',
                cells[5]?.textContent || '',
                cells[6]?.textContent || '',
                cells[7]?.textContent || ''
            ].join(',');
        });

        return [headers.join(','), ...rows].join('\n');
    }

    downloadCSV(content, filename) {
        const blob = new Blob([content], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    showSettings() {
        window.ChezMemeUtils.showNotification('Paramètres bientôt disponibles !', 'info');
    }

    initTableSearch() {
        // Ajouter une barre de recherche si elle n'existe pas
        const tableContainer = document.querySelector('.reservations-table');
        if (tableContainer && !document.querySelector('.table-search')) {
            const searchContainer = document.createElement('div');
            searchContainer.className = 'table-search';
            searchContainer.innerHTML = `
                <div class="search-box">
                    <i class="fas fa-search"></i>
                    <input type="text" placeholder="Rechercher dans les réservations..." id="tableSearch">
                </div>
            `;
            searchContainer.style.cssText = `
                margin-bottom: 1rem;
                padding: 1rem;
                background: var(--bg-light);
                border-radius: 10px;
            `;
            
            tableContainer.parentNode.insertBefore(searchContainer, tableContainer);

            // Gestion de la recherche
            const searchInput = document.getElementById('tableSearch');
            searchInput.addEventListener('input', (e) => {
                this.filterTable(e.target.value);
            });
        }
    }

    filterTable(searchTerm) {
        const rows = document.querySelectorAll('.reservation-row');
        const term = searchTerm.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(term)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    initStatsAnimation() {
        // Animation des statistiques
        const statCards = document.querySelectorAll('.stat-card');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateStatCard(entry.target);
                }
            });
        }, { threshold: 0.5 });

        statCards.forEach(card => {
            observer.observe(card);
        });
    }

    animateStatCard(card) {
        const numberElement = card.querySelector('.stat-info h3');
        const number = parseInt(numberElement.textContent);
        
        if (!isNaN(number)) {
            this.animateNumber(numberElement, number);
        }
    }

    animateNumber(element, target) {
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 30);
    }

    initAutoRefresh() {
        // Actualisation automatique des données toutes les 30 secondes
        setInterval(() => {
            this.refreshData();
        }, 30000);
    }

    refreshData() {
        // Recharger la page pour avoir les dernières données
        // En production, on ferait un appel AJAX
        const refreshIndicator = document.createElement('div');
        refreshIndicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Actualisation...';
        refreshIndicator.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--primary-color);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            z-index: 1000;
        `;
        
        document.body.appendChild(refreshIndicator);
        
        setTimeout(() => {
            document.body.removeChild(refreshIndicator);
            window.location.reload();
        }, 1000);
    }
}

// Gestion des notifications admin
class AdminNotifications {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkPendingReservations();
    }

    bindEvents() {
        // Gestion des notifications en temps réel
        this.initWebSocket();
    }

    initWebSocket() {
        // Simulation de WebSocket pour les notifications en temps réel
        // En production, on utiliserait une vraie connexion WebSocket
        setInterval(() => {
            this.simulateNewReservation();
        }, 60000); // Toutes les minutes
    }

    simulateNewReservation() {
        // Simulation d'une nouvelle réservation (à supprimer en production)
        if (Math.random() < 0.1) { // 10% de chance
            this.showNewReservationNotification();
        }
    }

    showNewReservationNotification() {
        const notification = document.createElement('div');
        notification.className = 'admin-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-bell"></i>
                <div>
                    <strong>Nouvelle réservation !</strong>
                    <p>Une nouvelle demande de réservation est en attente</p>
                </div>
                <button class="close-notification">&times;</button>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--warning-color);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Fermer la notification
        const closeBtn = notification.querySelector('.close-notification');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto-fermeture après 5 secondes
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    checkPendingReservations() {
        const pendingCount = document.querySelectorAll('.reservation-card.pending').length;
        if (pendingCount > 0) {
            this.showPendingNotification(pendingCount);
        }
    }

    showPendingNotification(count) {
        const notification = document.createElement('div');
        notification.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${count} réservation${count > 1 ? 's' : ''} en attente</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--warning-color);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 25px;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            animation: pulse 2s infinite;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }
}

// Initialisation des composants admin
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.admin-dashboard')) {
        new AdminDashboard();
        new AdminNotifications();
    }
});
