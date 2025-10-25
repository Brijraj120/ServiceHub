// Client-side JavaScript for Service Request Portal

document.addEventListener('DOMContentLoaded', function() {
    // Add animation to service cards
    const serviceCards = document.querySelectorAll('.service-card');
    if (serviceCards.length > 0) {
        serviceCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('animate__animated', 'animate__fadeInUp');
        });
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    if (forms.length > 0) {
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // Highlight all invalid fields
                    const invalidFields = form.querySelectorAll(':invalid');
                    invalidFields.forEach(field => {
                        field.classList.add('is-invalid');
                        
                        // Add event listener to remove invalid class when user starts typing
                        field.addEventListener('input', function() {
                            this.classList.remove('is-invalid');
                        });
                    });
                    
                    // Scroll to the first invalid field
                    if (invalidFields.length > 0) {
                        invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                        invalidFields[0].focus();
                    }
                }
                
                form.classList.add('was-validated');
            });
        });
    }

    // Phone number formatting
    const phoneInput = document.getElementById('customer_phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value.length <= 3) {
                    value = value;
                } else if (value.length <= 6) {
                    value = value.slice(0, 3) + '-' + value.slice(3);
                } else {
                    value = value.slice(0, 3) + '-' + value.slice(3, 6) + '-' + value.slice(6, 10);
                }
            }
            e.target.value = value;
        });
    }
}); 