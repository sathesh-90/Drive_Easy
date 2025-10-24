document.addEventListener("DOMContentLoaded", function() {
  // DOM Elements
  const driveOptions = document.querySelectorAll('.drive-option');
  const selfDriveFields = document.getElementById('selfDriveFields');
  const driverInfo = document.getElementById('driverInfo');
  const kmInput = document.getElementById('km_to_destination');
  const startInput = document.getElementById('start_datetime');
  const endInput = document.getElementById('end_datetime');
  const bookingForm = document.getElementById('bookingForm');
  const submitBtn = document.getElementById('submitBtn');
  const btnText = submitBtn.querySelector('.btn-text');
  const loadingOverlay = document.getElementById('loadingOverlay');
  
  // Validation elements
  const aadhaarInput = document.getElementById('aadhaar_number');
  const licenseInput = document.getElementById('license_number');
  const aadhaarValidation = document.getElementById('aadhaarValidation');
  const licenseValidation = document.getElementById('licenseValidation');

  // Pricing data
  const perHour = parseFloat(document.getElementById('per_hour').textContent);
  const perKm = parseFloat(document.getElementById('per_km').textContent);

  // Fare display elements
  const fareElements = {
    hours: document.getElementById('calculated_hours'),
    base: document.getElementById('base_amount'),
    driver: document.getElementById('driver_charge'),
    total: document.getElementById('total_amount'),
    advance: document.getElementById('advance_payment'),
    pending: document.getElementById('pending_payment')
  };

  // Initialize with current time as minimum
  const now = new Date();
  const timezoneOffset = now.getTimezoneOffset() * 60000;
  const localISOTime = new Date(now - timezoneOffset).toISOString().slice(0, 16);
  startInput.min = localISOTime;
  endInput.min = localISOTime;

  // Drive type selection
  driveOptions.forEach(option => {
    option.addEventListener('click', function() {
      driveOptions.forEach(opt => opt.classList.remove('selected'));
      this.classList.add('selected');
      const driveType = this.querySelector('input').value;
      toggleDriveOptions(driveType);
    });
  });

  function toggleDriveOptions(driveType) {
    if (driveType === 'self_drive') {
      selfDriveFields.style.display = 'block';
      driverInfo.style.display = 'none';
    } else {
      selfDriveFields.style.display = 'none';
      driverInfo.style.display = 'block';
    }
    calculateFare();
  }

  // Fare calculation
  function calculateFare() {
    let km = parseFloat(kmInput.value) || 0;
    let hours = 4;

    if (startInput.value && endInput.value) {
      const start = new Date(startInput.value);
      const end = new Date(endInput.value);
      const diff = (end - start) / (1000 * 60 * 60);
      hours = Math.max(Math.ceil(diff), 4);
    }

    const driveType = document.querySelector('.drive-option.selected input').value;
    const baseAmount = Math.max(perHour * hours, perKm * km, perHour * 4);
    const driverCharge = driveType === 'with_driver' ? 500 : 0;
    const total = baseAmount + driverCharge;
    const advance = total * 0.2;
    const pending = total - advance;

    // Update UI
    fareElements.hours.textContent = hours;
    fareElements.base.textContent = baseAmount.toFixed(2);
    fareElements.driver.textContent = driverCharge.toFixed(2);
    fareElements.total.textContent = total.toFixed(2);
    fareElements.advance.textContent = advance.toFixed(2);
    fareElements.pending.textContent = pending.toFixed(2);
  }

  // Validation functions
  function validateAadhaar() {
    const value = aadhaarInput.value.trim();
    if (value.length === 0) {
      resetValidation(aadhaarInput, aadhaarValidation);
      return false;
    }
    
    if (/^\d{12}$/.test(value)) {
      setValid(aadhaarInput, aadhaarValidation, "Valid Aadhaar number");
      return true;
    } else {
      setInvalid(aadhaarInput, aadhaarValidation, "Please enter a valid 12-digit Aadhaar number");
      return false;
    }
  }

  function validateLicense() {
    const value = licenseInput.value.trim();
    if (value.length === 0) {
      resetValidation(licenseInput, licenseValidation);
      return false;
    }
    
    if (value.length >= 5) {
      setValid(licenseInput, licenseValidation, "Valid license number");
      return true;
    } else {
      setInvalid(licenseInput, licenseValidation, "License number must be at least 5 characters");
      return false;
    }
  }

  function setValid(input, validation, message) {
    input.classList.remove('invalid');
    input.classList.add('valid');
    validation.textContent = message;
    validation.className = 'validation-message valid';
  }

  function setInvalid(input, validation, message) {
    input.classList.remove('valid');
    input.classList.add('invalid');
    validation.textContent = message;
    validation.className = 'validation-message invalid';
  }

  function resetValidation(input, validation) {
    input.classList.remove('valid', 'invalid');
    validation.textContent = '';
    validation.className = 'validation-message';
  }

  // Form submission
  function handleFormSubmit(e) {
    const driveType = document.querySelector('.drive-option.selected input').value;
    
    // If self drive, validate documents
    if (driveType === 'self_drive') {
      const isAadhaarValid = validateAadhaar();
      const isLicenseValid = validateLicense();
      
      if (!isAadhaarValid || !isLicenseValid) {
        e.preventDefault();
        // Scroll to first invalid field
        const firstInvalid = !isAadhaarValid ? aadhaarInput : licenseInput;
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalid.focus();
        return;
      }
    }
    
    // Show loading state
    e.preventDefault();
    submitBtn.disabled = true;
    btnText.textContent = "Processing...";
    submitBtn.classList.add('btn-loading');
    loadingOverlay.classList.add('active');
    
    // Simulate processing delay
    setTimeout(() => {
      bookingForm.submit();
    }, 2000);
  }

  // Event listeners
  [kmInput, startInput, endInput].forEach(el => {
    el.addEventListener('input', calculateFare);
  });
  
  aadhaarInput.addEventListener('input', validateAadhaar);
  licenseInput.addEventListener('input', validateLicense);
  bookingForm.addEventListener('submit', handleFormSubmit);

  // Initialize
  toggleDriveOptions('self_drive');
  calculateFare();
});
