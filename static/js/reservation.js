// Gestion du formulaire de réservation
class ReservationForm {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.setMinDate();
        this.loadAvailability();
    }

    bindEvents() {
        const form = document.querySelector('.reservation-form');
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');

        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSubmit(e);
            });
        }

        if (startDateInput && endDateInput) {
            startDateInput.addEventListener('change', () => {
                this.updateEndDateMin();
            });

            endDateInput.addEventListener('change', () => {
                this.validateDateRange();
            });
        }
    }

    setMinDate() {
        const today = new Date().toISOString().split('T')[0];
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');

        if (startDateInput) {
            startDateInput.min = today;
        }
        if (endDateInput) {
            endDateInput.min = today;
        }
    }

    updateEndDateMin() {
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');

        if (startDateInput && endDateInput && startDateInput.value) {
            // Ajouter un jour à la date de début pour la date de fin minimum
            const startDate = new Date(startDateInput.value);
            startDate.setDate(startDate.getDate() + 1);
            endDateInput.min = startDate.toISOString().split('T')[0];
        }
    }

    validateDateRange() {
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');

        if (startDateInput.value && endDateInput.value) {
            const startDate = new Date(startDateInput.value);
            const endDate = new Date(endDateInput.value);

            if (endDate <= startDate) {
                endDateInput.setCustomValidity('La date de fin doit être après la date de début');
                endDateInput.reportValidity();
            } else {
                endDateInput.setCustomValidity('');
            }

            // Vérifier la durée maximale (7 jours)
            const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
            if (daysDiff > 7) {
                endDateInput.setCustomValidity('La réservation ne peut pas dépasser 7 jours');
                endDateInput.reportValidity();
            } else {
                endDateInput.setCustomValidity('');
            }
        }
    }

    async loadAvailability() {
        try {
            const response = await fetch('/api/reservations');
            const reservations = await response.json();
            this.updateAvailabilityDisplay(reservations);
        } catch (error) {
            console.error('Erreur lors du chargement des disponibilités:', error);
        }
    }

    updateAvailabilityDisplay(reservations) {
        const availabilityGrid = document.getElementById('availabilityGrid');
        if (!availabilityGrid) return;

        // Calculer les prochaines disponibilités
        const today = new Date();
        const nextAvailableDates = this.findNextAvailableDates(today, reservations);

        availabilityGrid.innerHTML = '';

        if (nextAvailableDates.length === 0) {
            availabilityGrid.innerHTML = `
                <div class="no-availability">
                    <i class="fas fa-calendar-times"></i>
                    <p>Aucune disponibilité trouvée pour les prochains jours</p>
                </div>
            `;
            return;
        }

        nextAvailableDates.forEach(dateRange => {
            const availabilityCard = document.createElement('div');
            availabilityCard.className = 'availability-card';
            availabilityCard.innerHTML = `
                <div class="availability-date">
                    <i class="fas fa-calendar-check"></i>
                    <span>${this.formatDateRange(dateRange.start, dateRange.end)}</span>
                </div>
                <div class="availability-action">
                    <button class="btn btn-primary btn-small" onclick="selectDateRange('${dateRange.start}', '${dateRange.end}')">
                        Réserver
                    </button>
                </div>
            `;
            availabilityGrid.appendChild(availabilityCard);
        });
    }

    findNextAvailableDates(startDate, reservations) {
        const availableDates = [];
        const maxDaysToCheck = 30; // Vérifier les 30 prochains jours
        let currentDate = new Date(startDate);

        for (let i = 0; i < maxDaysToCheck; i++) {
            const isAvailable = !this.isDateReserved(currentDate, reservations);
            
            if (isAvailable) {
                // Trouver la fin de la période disponible
                let endDate = new Date(currentDate);
                while (endDate < new Date(startDate.getTime() + (maxDaysToCheck * 24 * 60 * 60 * 1000))) {
                    const nextDay = new Date(endDate);
                    nextDay.setDate(nextDay.getDate() + 1);
                    
                    if (this.isDateReserved(nextDay, reservations)) {
                        break;
                    }
                    endDate = nextDay;
                }

                availableDates.push({
                    start: currentDate.toISOString().split('T')[0],
                    end: endDate.toISOString().split('T')[0]
                });

                // Passer à la prochaine période non disponible
                currentDate = new Date(endDate);
                currentDate.setDate(currentDate.getDate() + 1);
            } else {
                currentDate.setDate(currentDate.getDate() + 1);
            }
        }

        return availableDates.slice(0, 5); // Limiter à 5 suggestions
    }

    isDateReserved(date, reservations) {
        return reservations.some(res => {
            const startDate = new Date(res.start_date);
            const endDate = new Date(res.end_date);
            const dateObj = new Date(date);
            return dateObj >= startDate && dateObj <= endDate;
        });
    }
    
    // Fonction pour vérifier si les réservations en attente bloquent une nouvelle réservation
    hasPendingConflict(startDate, endDate, reservations) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        return reservations.some(res => {
            if (res.type === 'pending') {
                const resStart = new Date(res.start_date);
                const resEnd = new Date(res.end_date);
                // Vérifier si les périodes se chevauchent
                return start < resEnd && end > resStart;
            }
            return false;
        });
    }

    formatDateRange(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (start.toDateString() === end.toDateString()) {
            return start.toLocaleDateString('fr-FR');
        }
        
        return `${start.toLocaleDateString('fr-FR')} - ${end.toLocaleDateString('fr-FR')}`;
    }

    async handleSubmit(e) {
        const form = e.target;
        const formData = new FormData(form);
        
        // Validation côté client
        if (!this.validateForm(formData)) {
            return;
        }

        // Afficher un indicateur de chargement
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Envoi en cours...';
        submitButton.disabled = true;

        try {
            const response = await fetch('/reserver', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                window.ChezMemeUtils.showNotification(data.message, 'success');
                // Rafraîchir les disponibilités
                this.loadAvailability();
                // Reset du formulaire
                form.reset();
            } else {
                window.ChezMemeUtils.showNotification(data.message || 'Erreur lors de l\'envoi de la réservation', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            window.ChezMemeUtils.showNotification('Erreur lors de l\'envoi de la réservation', 'error');
        } finally {
            // Restaurer le bouton
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }
    }

    validateForm(formData) {
        const guestName = formData.get('guest_name');
        const startDate = formData.get('start_date');
        const endDate = formData.get('end_date');

        // Validation du nom
        if (!guestName || guestName.trim().length < 2) {
            window.ChezMemeUtils.showNotification('Veuillez entrer un nom valide', 'error');
            return false;
        }

        // Validation des dates
        if (!startDate || !endDate) {
            window.ChezMemeUtils.showNotification('Veuillez sélectionner des dates', 'error');
            return false;
        }

        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (end <= start) {
            window.ChezMemeUtils.showNotification('La date de fin doit être après la date de début', 'error');
            return false;
        }

        const today = new Date().toISOString().split('T')[0];
        if (startDate < today) {
            window.ChezMemeUtils.showNotification('Impossible de réserver dans le passé', 'error');
            return false;
        }

        return true;
    }
}

// Fonction globale pour sélectionner une période de dates
function selectDateRange(startDate, endDate) {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    if (startDateInput && endDateInput) {
        startDateInput.value = startDate;
        endDateInput.value = endDate;
        
        // Déclencher les événements de changement
        startDateInput.dispatchEvent(new Event('change'));
        endDateInput.dispatchEvent(new Event('change'));
        
        // Faire défiler vers le formulaire
        document.querySelector('.reservation-form').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Initialiser le formulaire de réservation
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.reservation-form')) {
        new ReservationForm();
    }
});
