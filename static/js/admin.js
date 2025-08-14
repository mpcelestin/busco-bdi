document.addEventListener('DOMContentLoaded', function() {
    // Modal handling
    const modal = document.getElementById('addProductModal');
    const addBtn = document.getElementById('addProductBtn');
    const closeBtn = document.querySelector('.close');
    
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            modal.style.display = 'block';
        });
    }
    
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
    
    // Product form submission
    const productForm = document.getElementById('productForm');
    if (productForm) {
        productForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch('/admin/add_product', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Product added successfully!');
                    window.location.reload();
                } else {
                    alert('Error: ' + (data.error || 'Failed to add product'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while adding the product');
            });
        });
    }
    
    // Approve product buttons
    document.querySelectorAll('.approve-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.getAttribute('data-id');
            
            fetch(`/admin/approve_product/${productId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert('Failed to approve product');
                }
            });
        });
    });
    
    // Delete product buttons
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this product?')) {
                const productId = this.getAttribute('data-id');
                
                fetch(`/admin/delete_product/${productId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Failed to delete product');
                    }
                });
            }
        });
    });
});