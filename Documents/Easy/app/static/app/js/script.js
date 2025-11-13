// Mobile Menu Toggle
    document.querySelector('.mobile-menu').addEventListener('click', function() {
        document.getElementById('nav-menu').classList.toggle('show');
    });

    // DOM Elements
    const rentButtons = document.querySelectorAll('.rent-btn');
    const bookingModal = document.getElementById('booking-modal');
    const confirmationModal = document.getElementById('confirmation-modal');
    const closeModalButtons = document.querySelectorAll('.close-modal, #cancel-booking');
    const bookingForm = document.getElementById('booking-form');
    const searchForm = document.querySelector('.search-form');
    
    // Initialize date pickers
    function initDatePickers() {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        const formatDate = (date) => date.toISOString().split('T')[0];
        
        // Search form dates
        document.getElementById('pickup-date').value = formatDate(today);
        document.getElementById('pickup-date').min = formatDate(today);
        document.getElementById('return-date').value = formatDate(tomorrow);
        document.getElementById('return-date').min = formatDate(tomorrow);
        
        // Booking form dates
        document.getElementById('booking-pickup-date').value = formatDate(today);
        document.getElementById('booking-pickup-date').min = formatDate(today);
        document.getElementById('booking-return-date').value = formatDate(tomorrow);
        document.getElementById('booking-return-date').min = formatDate(tomorrow);
    }
    
    // Open Booking Modal
    function openBookingModal(car, price) {
        document.getElementById('selected-car').value = car;
        document.getElementById('daily-rate').value = price;
        
        // Update summary
        document.getElementById('summary-car').textContent = car;
        document.getElementById('summary-rate').textContent = `₹${price}`;
        
        initDatePickers();
        calculateTotal();
        
        bookingModal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }

    // Close Modals
    function closeModals() {
        bookingModal.style.display = 'none';
        confirmationModal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Re-enable scrolling
    }

    // Event Listeners
    rentButtons.forEach(button => {
        button.addEventListener('click', function() {
            openBookingModal(
                this.getAttribute('data-car'),
                this.getAttribute('data-price')
            );
        });
    });

    closeModalButtons.forEach(button => {
        button.addEventListener('click', closeModals);
    });

    window.addEventListener('click', function(event) {
        if (event.target === bookingModal || event.target === confirmationModal) {
            closeModals();
        }
    });

    // Calculate rental cost
    function calculateTotal() {
        const pickupDate = new Date(pickupDateInput.value);
        const returnDate = new Date(returnDateInput.value);
        const driverOption = document.getElementById('driver-option');
        
        if (pickupDate && returnDate && returnDate > pickupDate) {
            const days = Math.ceil((returnDate - pickupDate) / (1000 * 60 * 60 * 24));
            const dailyRate = parseInt(document.getElementById('daily-rate').value);
            const driverFee = driverOption.value === 'with-driver' ? 500 : 0;
            const total = (dailyRate * days) + (driverFee * days);
            
            document.getElementById('summary-days').textContent = days;
            document.getElementById('summary-driver').textContent = `₹${driverFee * days}`;
            document.getElementById('summary-total').textContent = `₹${total}`;
            
            // Set minimum advance payment (30%)
            const advanceInput = document.getElementById('advance-payment');
            advanceInput.min = Math.ceil(total * 0.3);
            advanceInput.max = total;
            advanceInput.placeholder = `Minimum ₹${advanceInput.min}`;
            
            // Validate advance payment in real-time
            if (parseInt(advanceInput.value) < parseInt(advanceInput.min)) {
                advanceInput.setCustomValidity(`Minimum advance is ₹${advanceInput.min}`);
            } else {
                advanceInput.setCustomValidity('');
            }
        }
    }

    // Form elements with change listeners
    const pickupDateInput = document.getElementById('booking-pickup-date');
    const returnDateInput = document.getElementById('booking-return-date');
    const driverOption = document.getElementById('driver-option');
    const advancePayment = document.getElementById('advance-payment');
    
    [pickupDateInput, returnDateInput, driverOption, advancePayment].forEach(element => {
        element.addEventListener('change', calculateTotal);
        element.addEventListener('input', calculateTotal);
    });

    // Handle form submission
    bookingForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!this.checkValidity()) {
            this.reportValidity();
            return;
        }
        
        // Get form values
        const formData = {
            car: document.getElementById('selected-car').value,
            name: document.getElementById('customer-name').value,
            email: document.getElementById('customer-email').value,
            phone: document.getElementById('customer-phone').value,
            address: document.getElementById('customer-address').value,
            pickupLocation: document.getElementById('pickup-location-booking').value,
            pickupDate: document.getElementById('booking-pickup-date').value,
            returnDate: document.getElementById('booking-return-date').value,
            estimatedKm: document.getElementById('estimated-km').value,
            driverOption: document.getElementById('driver-option').value,
            paymentMethod: document.getElementById('payment-method').value,
            totalAmount: document.getElementById('summary-total').textContent,
            advancePaid: document.getElementById('advance-payment').value,
            bookingRef: 'DE-' + Math.floor(Math.random() * 1000000)
        };
        
        // Update confirmation modal
        document.getElementById('confirmation-car').textContent = formData.car;
        document.getElementById('confirmation-name').textContent = formData.name;
        document.getElementById('confirmation-ref').textContent = formData.bookingRef;
        document.getElementById('confirmation-dates').textContent = 
            `${new Date(formData.pickupDate).toLocaleDateString()} to ${new Date(formData.returnDate).toLocaleDateString()}`;
        document.getElementById('confirmation-pickup').textContent = 
            document.getElementById('pickup-location-booking').options[document.getElementById('pickup-location-booking').selectedIndex].text;
        document.getElementById('confirmation-total').textContent = formData.totalAmount;
        document.getElementById('confirmation-advance').textContent = `₹${formData.advancePaid}`;
        document.getElementById('confirmation-balance').textContent = 
            `₹${parseInt(formData.totalAmount.replace('₹','')) - parseInt(formData.advancePaid)}`;
        
        // Show confirmation modal
        bookingModal.style.display = 'none';
        confirmationModal.style.display = 'block';
        
        // Reset form
        bookingForm.reset();
        localStorage.setItem('lastBooking', JSON.stringify(formData));
    });

    // Search form handling
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const location = document.getElementById('pickup-location').value;
            const pickupDate = document.getElementById('pickup-date').value;
            const returnDate = document.getElementById('return-date').value;
            
            // In a real app, you would filter cars here
            alert(`Searching for cars at ${location} from ${pickupDate} to ${returnDate}`);
            document.getElementById('cars').scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Initialize date pickers on load
    document.addEventListener('DOMContentLoaded', function() {
        initDatePickers();
        
        // Load last booking if exists (for demo purposes)
        const lastBooking = localStorage.getItem('lastBooking');
        if (lastBooking) {
            console.log('Last booking:', JSON.parse(lastBooking));
        }
    });


    document.addEventListener("DOMContentLoaded", function () {
  const trigger = document.querySelector(".profile-trigger");
  const menu = document.querySelector(".profile-menu");

  trigger.addEventListener("click", function () {
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
  });

  // Close menu when clicking outside
  document.addEventListener("click", function (event) {
    if (!trigger.contains(event.target) && !menu.contains(event.target)) {
      menu.style.display = "none";
    }
  });
});
