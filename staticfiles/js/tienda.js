const API_BASE_URL = '/api';

function updateBudgetButtonVisibility() {
    const cartItems = JSON.parse(localStorage.getItem('carrito') || '[]');
    const createBudgetBtn = document.getElementById('create-budget-btn');
    
    if (cartItems.length > 0 && createBudgetBtn) {
        createBudgetBtn.style.display = 'block';
    } else if (createBudgetBtn) {
        createBudgetBtn.style.display = 'none';
    }
}

function actualizarCarritoDisplay() {
    if (typeof mostrarCarrito === 'function') {
        mostrarCarrito();
    }
    updateBudgetButtonVisibility();
}

function setupEventListeners() {
    const createBudgetBtn = document.getElementById('create-budget-btn');
    if (createBudgetBtn) {
        createBudgetBtn.addEventListener('click', function() {
            cerrarModales();
            
            const modalPresupuesto = document.getElementById('modalCrearPresupuesto');
            if (modalPresupuesto) {
                modalPresupuesto.classList.add('mostrar');
                
                const cartItems = JSON.parse(localStorage.getItem('carrito') || '[]');
                const container = document.getElementById('cart-items-container');
                
                if (container && cartItems.length > 0) {
                    container.innerHTML = '';
                    
                    const titleField = document.getElementById('budgetTitle');
                    const nameField = document.getElementById('customerName');
                    if (titleField) titleField.value = '';
                    if (nameField) nameField.value = '{{ user.username }}';
                    
                    cartItems.forEach(item => {
                        const productInput = document.createElement('input');
                        productInput.type = 'hidden';
                        productInput.name = 'product_ids';
                        productInput.value = item.id;
                        
                        const quantityInput = document.createElement('input');
                        quantityInput.type = 'hidden';
                        quantityInput.name = 'quantities';
                        quantityInput.value = item.cantidad;
                        
                        container.appendChild(productInput);
                        container.appendChild(quantityInput);
                    });
                }
            }
        });
    }

    const budgetForm = document.getElementById('budgetForm');
    if (budgetForm) {
        budgetForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            const url = window.budgetCreateUrl || '{% url "create_budget_from_cart" %}';
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Presupuesto creado y enviado a su correo exitosamente.');
                    
                    if (typeof window.actualizarCarritoDisplay === 'function') {
                        window.actualizarCarritoDisplay();
                    }
                    
                    document.getElementById('modalCrearPresupuesto').classList.remove('mostrar');
                    updateBudgetButtonVisibility();
                } else {
                    alert('Error al crear el presupuesto: ' + (data.error || 'Error desconocido'));
                }
            })
            .catch(error => {
                alert('Ocurrió un error al enviar el presupuesto: ' + error.message);
            });
        });
    }

    document.querySelectorAll('.cerrar-modal').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.classList.remove('mostrar');
            });
        });
    });
    
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                document.querySelectorAll('.modal').forEach(m => {
                    m.classList.remove('mostrar');
                });
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    updateBudgetButtonVisibility();
    setupEventListeners();
});

window.updateBudgetButtonVisibility = updateBudgetButtonVisibility;
window.actualizarCarritoDisplay = actualizarCarritoDisplay;