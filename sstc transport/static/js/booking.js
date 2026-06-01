document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('bookingForm');
    const priceEstimate = document.getElementById('priceEstimate');
    const bookingModal = new bootstrap.Modal(document.getElementById('bookingModal'));

    // Calculate price when form inputs change
    form.addEventListener('input', async function() {
        if (form.pickup.value && form.dropoff.value && form.quantity.value) {
            const formData = new FormData(form);
            const response = await fetch('/calculate_price', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            document.getElementById('distance').textContent = data.distance;
            document.getElementById('price').textContent = data.price;
            priceEstimate.style.display = 'block';
        }
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        formData.append('price', document.getElementById('price').textContent);

        const response = await fetch('/book', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Update booking details in modal
        const bookingDetails = document.getElementById('bookingDetails');
        bookingDetails.innerHTML = `
            <h6>Booking ID: ${data.booking.id}</h6>
            <p><strong>Name:</strong> ${data.booking.name}</p>
            <p><strong>Email:</strong> ${data.booking.email}</p>
            <p><strong>Phone:</strong> ${data.booking.phone}</p>
            <p><strong>From:</strong> ${data.booking.pickup}</p>
            <p><strong>To:</strong> ${data.booking.dropoff}</p>
            <p><strong>Driver:</strong> ${data.booking.driver.name}</p>
            <p><strong>Vehicle:</strong> ${data.booking.driver.vehicle}</p>
            <p><strong>Contact:</strong> ${data.booking.driver.phone}</p>
        `;

        // Update tracking link
        document.getElementById('trackingLink').href = `/tracking/${data.booking.id}`;

        // Show modal
        bookingModal.show();

        // Reset form
        form.reset();
        priceEstimate.style.display = 'none';
    });
});