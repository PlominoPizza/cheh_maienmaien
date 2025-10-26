// Calendrier multi-mois pour les réservations
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();

document.addEventListener('DOMContentLoaded', function() {
    const calendarContainer = document.getElementById('calendar');
    
    if (!calendarContainer) return;
    
    // Récupérer les réservations depuis l'API
    fetch('/api/reservations')
        .then(response => response.json())
        .then(reservations => {
            displayCalendar(reservations);
        })
        .catch(error => {
            console.error('Erreur lors du chargement des réservations:', error);
            displayCalendar([]);
        });
});

function displayCalendar(reservations) {
    const calendarContainer = document.getElementById('calendar');
    
    // Créer le header du calendrier avec navigation
    const monthNames = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ];
    
    const calendarHTML = `
        <div class="calendar-header">
            <button class="calendar-nav-btn" onclick="changeMonth(-1)">‹</button>
            <h3>${monthNames[currentMonth]} ${currentYear}</h3>
            <button class="calendar-nav-btn" onclick="changeMonth(1)">›</button>
        </div>
        <div class="calendar-grid">
            <div class="calendar-day-header">Lun</div>
            <div class="calendar-day-header">Mar</div>
            <div class="calendar-day-header">Mer</div>
            <div class="calendar-day-header">Jeu</div>
            <div class="calendar-day-header">Ven</div>
            <div class="calendar-day-header">Sam</div>
            <div class="calendar-day-header">Dim</div>
            ${generateCalendarDays(currentYear, currentMonth, reservations)}
        </div>
    `;
    
    calendarContainer.innerHTML = calendarHTML;
}

function changeMonth(direction) {
    currentMonth += direction;
    
    // Gérer le passage d'année
    if (currentMonth > 11) {
        currentMonth = 0; // Janvier
        currentYear++;
    } else if (currentMonth < 0) {
        currentMonth = 11; // Décembre
        currentYear--;
    }
    
    // Limiter jusqu'à septembre 2026 (pour voir l'effet RIP)
    if (currentYear > 2026 || (currentYear === 2026 && currentMonth > 8)) {
        currentMonth = 8; // Septembre
        currentYear = 2026;
    }
    
    // Ne pas aller avant le mois actuel
    const today = new Date();
    if (currentYear < today.getFullYear() || 
        (currentYear === today.getFullYear() && currentMonth < today.getMonth())) {
        currentMonth = today.getMonth();
        currentYear = today.getFullYear();
    }
    
    // Recharger le calendrier
    fetch('/api/reservations')
        .then(response => response.json())
        .then(reservations => {
            displayCalendar(reservations);
        })
        .catch(error => {
            console.error('Erreur lors du chargement des réservations:', error);
            displayCalendar([]);
        });
}

function generateCalendarDays(year, month, reservations) {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    
    // Trouver le premier lundi du mois
    const startDate = new Date(firstDay);
    const dayOfWeek = firstDay.getDay();
    const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    startDate.setDate(firstDay.getDate() + mondayOffset);
    
    let html = '';
    const currentDate = new Date(startDate);
    
    // Générer 42 cases (6 semaines)
    for (let i = 0; i < 42; i++) {
        const isCurrentMonth = currentDate.getMonth() === month;
        const isToday = currentDate.toDateString() === new Date().toDateString();
        const dateString = currentDate.toISOString().split('T')[0];
        
        // Vérifier si cette date est après le 26 août 2026 (RIP Chez mémé)
        const ripDate = new Date(2026, 7, 26); // 26 août 2026 (mois 7 = août)
        const isAfterRipDate = currentDate > ripDate;
        
        // Vérifier si cette date est réservée
        const reservation = reservations.find(r => {
            const startDate = new Date(r.start_date);
            const endDate = new Date(r.end_date);
            
            // Normaliser les dates pour la comparaison (enlever l'heure)
            const currentDateNormalized = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate());
            const startDateNormalized = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
            const endDateNormalized = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
            
            // Inclure le jour d'arrivée mais EXCLURE le jour de départ
            return currentDateNormalized >= startDateNormalized && currentDateNormalized < endDateNormalized;
        });
        
        let className = 'calendar-day';
        if (!isCurrentMonth) className += ' other-month';
        if (isToday) className += ' today';
        if (reservation || isAfterRipDate) className += ' reserved';
        
        let content = currentDate.getDate();
        if (reservation) {
            content = `<div class="reservation-info">${currentDate.getDate()}<br><small>${reservation.guest_name}</small></div>`;
        } else if (isAfterRipDate) {
            content = `<div class="reservation-info">${currentDate.getDate()}<br><small>RIP Chez mémé</small></div>`;
        }
        
        html += `<div class="${className}">${content}</div>`;
        
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return html;
}
