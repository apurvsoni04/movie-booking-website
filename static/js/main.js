document.addEventListener('DOMContentLoaded', () => {
    // Only target seats inside the theatre container to avoid conflict with legened seats
    const theatreContainer = document.querySelector('.theatre-container');
    if (!theatreContainer) return;

    // Filter out both sold and reserved seats from interaction
    const seats = theatreContainer.querySelectorAll('.seat:not(.sold):not(.reserved)');
    const seatDisplay = document.getElementById('selected-seats-display');
    const amountDisplay = document.getElementById('total-amount-display');
    const seatInput = document.getElementById('selected-seats-input');
    const amountInput = document.getElementById('total-amount-input');
    const bookBtn = document.getElementById('book-btn');

    let selectedSeats = [];

    seats.forEach(seat => {
        seat.addEventListener('click', () => {
            // Extra guard clause
            if (seat.classList.contains('sold') || seat.classList.contains('reserved')) return;

            const seatId = seat.getAttribute('data-id');

            if (seat.classList.contains('selected')) {
                seat.classList.remove('selected');
                selectedSeats = selectedSeats.filter(id => id !== seatId);
            } else {
                seat.classList.add('selected');
                selectedSeats.push(seatId);
            }
            updateBookingSummary();
        });
    });

    function updateBookingSummary() {
        let total = 0;
        // Specifically select only selected seats within the theatre container
        const selectedElements = theatreContainer.querySelectorAll('.seat.selected');

        selectedElements.forEach(seat => {
            const price = parseFloat(seat.getAttribute('data-price')) || 0;
            total += price;
        });

        seatDisplay.textContent = selectedSeats.length > 0 ? selectedSeats.join(', ') : '-';
        amountDisplay.textContent = total.toFixed(2);

        // Update hidden inputs for form submission
        seatInput.value = selectedSeats.join(',');
        amountInput.value = total.toFixed(2);

        if (selectedSeats.length > 0) {
            bookBtn.removeAttribute('disabled');
        } else {
            bookBtn.setAttribute('disabled', 'true');
        }
    }
});
