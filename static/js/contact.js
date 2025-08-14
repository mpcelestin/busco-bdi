document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    const formResponse = document.getElementById('formResponse');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            // Show loading state
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.textContent;
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            fetch('/send_message', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    formResponse.textContent = 'Message sent successfully!';
                    formResponse.style.color = 'green';
                    contactForm.reset();
                } else {
                    formResponse.textContent = data.error || 'Failed to send message';
                    formResponse.style.color = 'red';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                formResponse.textContent = 'An error occurred. Please try again.';
                formResponse.style.color = 'red';
            })
            .finally(() => {
                submitBtn.textContent = originalBtnText;
                submitBtn.disabled = false;
                
                // Clear response after 5 seconds
                setTimeout(() => {
                    formResponse.textContent = '';
                }, 5000);
            });
        });
    }
});