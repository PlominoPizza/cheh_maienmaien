// Calendrier interactif
class Calendar {
    constructor() {
        this.currentDate = new Date();
        this.reservations = [];
        this.init();
    }

    init() {
        this.loadReservations();
        this.renderCalendar();
        this.bindEvents();
    }

    async loadReservations() {
        try {
            const response = await fetch('/api/reservations');
            this.reservations = await response.json();
            this.renderCalendar();
        } catch (error) {
            console.error('Erreur lors du chargement des réservations:', error);
        }
    }

    renderCalendar() {
        const calendarGrid = document.getElementById('calendarGrid');
        const currentMonthElement = document.getElementById('currentMonth');
        
        if (!calendarGrid || !currentMonthElement) return;

        // Mettre à jour le titre du mois
        const monthNames = [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ];
        currentMonthElement.textContent = `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;

        // Calculer le premier jour du mois et le nombre de jours
        const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();

        // Créer le calendrier
        calendarGrid.innerHTML = '';

        // Ajouter les jours de la semaine
        const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
        dayNames.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            dayHeader.textContent = day;
            dayHeader.style.cssText = `
                background: var(--primary-color);
                color: white;
                padding: 1rem;
                text-align: center;
                font-weight: 600;
                border-radius: 5px;
            `;
            calendarGrid.appendChild(dayHeader);
        });

        // Ajouter les jours vides du mois précédent
        for (let i = 0; i < startingDayOfWeek; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'calendar-day other-month';
            emptyDay.style.cssText = `
                background: #f9fafb;
                padding: 1rem;
                min-height: 80px;
                color: #9ca3af;
            `;
            calendarGrid.appendChild(emptyDay);
        }

        // Ajouter les jours du mois
        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            const currentDayDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), day);
            
            dayElement.className = 'calendar-day';
            
            // Vérifier si c'est aujourd'hui
            if (this.isSameDay(currentDayDate, today)) {
                dayElement.classList.add('today');
            }

            // Vérifier si c'est réservé
            const reservation = this.getReservationForDate(currentDayDate);
            if (reservation) {
                dayElement.classList.add('reserved');
                dayElement.title = `Réservé par ${reservation.guest_name}`;
            }

            dayElement.innerHTML = `
                <div class="day-number">${day}</div>
                ${reservation ? `<div class="day-info">${reservation.guest_name}</div>` : ''}
            `;

            // Ajouter l'événement de clic
            dayElement.addEventListener('click', () => {
                this.handleDayClick(currentDayDate, reservation);
            });

            calendarGrid.appendChild(dayElement);
        }
    }

    isSameDay(date1, date2) {
        return date1.getDate() === date2.getDate() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getFullYear() === date2.getFullYear();
    }

    getReservationForDate(date) {
        const dateString = date.toISOString().split('T')[0];
        return this.reservations.find(res => {
            const startDate = new Date(res.start_date);
            const endDate = new Date(res.end_date);
            return date >= startDate && date <= endDate;
        });
    }

    handleDayClick(date, reservation) {
        if (reservation) {
            this.showReservationModal(reservation);
        } else {
            // Rediriger vers la page de réservation avec la date pré-remplie
            const dateString = date.toISOString().split('T')[0];
            window.location.href = `/reserver?date=${dateString}`;
        }
    }

    showReservationModal(reservation) {
        const modal = document.getElementById('reservationModal');
        const details = document.getElementById('reservationDetails');
        
        if (modal && details) {
            details.innerHTML = `
                <div class="reservation-modal-content">
                    <h4>Réservation confirmée</h4>
                    <p><strong>Invité:</strong> ${reservation.guest_name}</p>
                    <p><strong>Dates:</strong> ${this.formatDateRange(reservation.start_date, reservation.end_date)}</p>
                    <p><strong>Demandé par:</strong> ${reservation.user}</p>
                </div>
            `;
            modal.style.display = 'block';
        }
    }

    formatDateRange(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        return `${start.toLocaleDateString('fr-FR')} - ${end.toLocaleDateString('fr-FR')}`;
    }

    bindEvents() {
        const prevButton = document.getElementById('prevMonth');
        const nextButton = document.getElementById('nextMonth');
        const modal = document.getElementById('reservationModal');
        const closeButton = modal?.querySelector('.close');

        if (prevButton) {
            prevButton.addEventListener('click', () => {
                this.currentDate.setMonth(this.currentDate.getMonth() - 1);
                this.renderCalendar();
            });
        }

        if (nextButton) {
            nextButton.addEventListener('click', () => {
                this.currentDate.setMonth(this.currentDate.getMonth() + 1);
                this.renderCalendar();
            });
        }

        if (closeButton) {
            closeButton.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }

        // Fermer le modal en cliquant à l'extérieur
        if (modal) {
            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
    }
}

// Initialiser le calendrier quand la page est chargée
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('calendarGrid')) {
        new Calendar();
    }
});
