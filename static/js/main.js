// Main JavaScript file for Cure24

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Add visual feedback for premium checkbox
    const premiumCheckbox = document.getElementById('is_premium');
    if (premiumCheckbox) {
        premiumCheckbox.addEventListener('change', function() {
            const premiumCard = document.querySelector('.premium-preview');
            if (premiumCard) {
                if (this.checked) {
                    premiumCard.classList.add('premium-listing');
                    premiumCard.querySelector('.premium-badge').style.display = 'block';
                } else {
                    premiumCard.classList.remove('premium-listing');
                    premiumCard.querySelector('.premium-badge').style.display = 'none';
                }
            }
        });
    }
});
