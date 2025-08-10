document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('story-form');
    const submitBtn = document.getElementById('generate-btn');
    
    if (form && submitBtn) {
        form.addEventListener('submit', function() {
            // Add loading state to button
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Story...';
            
            // Show loading message
            const loadingAlert = document.createElement('div');
            loadingAlert.className = 'alert alert-info mt-3';
            loadingAlert.innerHTML = '<i class="fas fa-magic"></i> Creating your story... This may take up to 30 seconds.';
            form.appendChild(loadingAlert);
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});