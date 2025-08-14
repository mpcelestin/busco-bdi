document.addEventListener('DOMContentLoaded', function() {
    // Message modal handling
    const modal = document.getElementById('messageModal');
    const closeBtn = document.querySelector('#messageModal .close');
    
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const messageId = this.getAttribute('data-id');
            
            // Populate modal
            document.getElementById('messageName').textContent = row.cells[0].textContent;
            document.getElementById('messageEmail').textContent = row.cells[1].textContent;
            document.getElementById('messageDate').textContent = row.cells[3].textContent;
            document.getElementById('messageText').textContent = row.cells[2].textContent;
            
            // Mark as read
            fetch(`/admin/mark_read/${messageId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        row.classList.remove('unread');
                        row.querySelector('.badge').textContent = 'Read';
                        row.querySelector('.badge').classList.remove('unread-badge');
                        row.querySelector('.badge').classList.add('read-badge');
                    }
                });
            
            modal.style.display = 'block';
        });
    });
    
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});