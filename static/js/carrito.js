let carrito = [];
const contadorCarrito = document.getElementById('contador-carrito');

function actualizarCarrito() {
    const totalItems = carrito.reduce((sum, item) => sum + item.cantidad, 0);
    contadorCarrito.textContent = totalItems;
    localStorage.setItem('carrito', JSON.stringify(carrito));
}

function mostrarModal(modalId) {
    document.getElementById(modalId).classList.add('mostrar');
}

function cerrarModales() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('mostrar');
    });
}

function mostrarCarrito() {
    const contenidoDiv = document.getElementById('contenidoCarrito');
    const botonesDiv = document.querySelector('#modalCarrito .budget-actions');
    
    if (carrito.length === 0) {
        contenidoDiv.innerHTML = `
            <div class="carrito-vacio">
                <i class="fas fa-shopping-bag" style="font-size: 48px; margin-bottom: 15px; color: #ffe4f4;"></i>
                <p>Tu carrito está vacío</p>
            </div>
        `;
        botonesDiv.style.display = 'none';
    } else {
        
        let total = 0;
        const itemsHTML = carrito.map(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            
            return `
                <div class="item-carrito">
                    <div class="item-carrito-info">
                        <h4>${item.nombre}</h4>
                        <div class="item-carrito-precio">$${item.precio}</div>
                    </div>
                    <div class="item-carrito-cantidad">
                        <button class="btn-cantidad" data-id="${item.id}" data-cambio="-1">-</button>
                        <span>${item.cantidad}</span>
                        <button class="btn-cantidad" data-id="${item.id}" data-cambio="1">+</button>
                    </div>
                    <button class="btn-eliminar-item" data-id="${item.id}"><i class="fas fa-trash"></i></button>
                </div>
            `;
        }).join('');
        
        contenidoDiv.innerHTML = `
            ${itemsHTML}
            <div class="carrito-total">
                Total: $${total.toFixed(2)}
            </div>
        `;
        
        botonesDiv.style.display = 'block';
        
        agregarListenersBotonesCarrito();
    }
    
    mostrarModal('modalCarrito');
}

function agregarListenersBotonesCarrito() {
    document.querySelectorAll('.btn-cantidad').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const cambio = parseInt(this.getAttribute('data-cambio'));
            cambiarCantidad(id, cambio);
        });
    });

    document.querySelectorAll('.btn-eliminar-item').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            eliminarItemCarrito(id);
        });
    });

    const btnPagar = document.getElementById('btn-proceder-pago');
    if (btnPagar && btnPagar.getAttribute('listener-set') !== 'true') {
        btnPagar.addEventListener('click', procederAlPagoDirecto);
        btnPagar.setAttribute('listener-set', 'true');
    }
}

function procederAlPagoDirecto() {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    if (carrito.length === 0) {
        alert("Tu carrito está vacío.");
        return;
    }

    const itemsParaMP = carrito.map(item => ({
        title: item.nombre, 
        quantity: item.cantidad, 
        unit_price: item.precio,
        currency_id: "ARS" 
    }));

    const csrfToken = document.querySelector('form#budgetForm [name=csrfmiddlewaretoken]').value;
    
    const botonPagarEl = document.getElementById('btn-proceder-pago'); 
    botonPagarEl.disabled = true;
    botonPagarEl.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Procesando...';

    fetch("/api/payments/create/", { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ items: itemsParaMP }) 
    })
    .then(response => response.json())
    .then(data => {
        if (data.init_point) {
            
            window.location.href = data.init_point;
        } else {
            
            console.error('Error del servidor:', data.error);
            alert('Error al crear el pago: ' + data.error);
            botonPagarEl.disabled = false;
            botonPagarEl.innerHTML = '<i class="bi bi-credit-card"></i> Proceder al Pago';
        }
    })
    .catch(error => {
        console.error('Error en fetch:', error);
        alert('Error de conexión. No se pudo contactar al servidor.');
        botonPagarEl.disabled = false;
        botonPagarEl.innerHTML = '<i class="bi bi-credit-card"></i> Proceder al Pago';
    });
}

function eliminarItemCarrito(productoId) {
    carrito = carrito.filter(item => item.id !== productoId);
    actualizarCarrito();
    if (document.getElementById('modalCarrito').classList.contains('mostrar')) {
        mostrarCarrito();
    }
}

function cambiarCantidad(productoId, cambio) {
    const item = carrito.find(item => item.id === productoId);
    if (item) {
        if (item.cantidad + cambio >= 1) {
            item.cantidad += cambio;
        } else {
            item.cantidad = 1;
        }
        actualizarCarrito();
        if (document.getElementById('modalCarrito').classList.contains('mostrar')) {
            mostrarCarrito();
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    
    const carritoGuardado = localStorage.getItem('carrito');
    if (carritoGuardado) {
        carrito = JSON.parse(carritoGuardado);
        actualizarCarrito();
    }

    document.querySelectorAll('.btn-agregar-carrito').forEach(button => {
        button.addEventListener('click', function() {
            const productoId = this.getAttribute('data-producto-id');
            const productoNombre = this.getAttribute('data-producto-nombre');
            const productoPrecio = parseFloat(this.getAttribute('data-producto-precio'));

            const productoExistente = carrito.find(item => item.id === productoId);
            
            if (productoExistente) {
                productoExistente.cantidad += 1;
            } else {
                carrito.push({
                    id: productoId,
                    nombre: productoNombre,
                    precio: productoPrecio,
                    cantidad: 1
                });
            }
            
            actualizarCarrito();
            
            
            this.textContent = '✓ Agregado';
            this.style.backgroundColor = '#c8e6c9';
            this.style.borderColor = '#c8e6c9';
            
            setTimeout(() => {
                this.textContent = 'Agregar al Carrito';
                this.style.backgroundColor = '#ffe4f4';
                this.style.borderColor = '#ffe4f4';
            }, 1500);
        });
    });

    document.querySelector('.icono-carrito').addEventListener('click', function() {
        mostrarCarrito();
    });

    document.querySelectorAll('.cerrar-modal').forEach(btn => {
        btn.addEventListener('click', cerrarModales);
    });

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                cerrarModales();
            }
        });
    });
    
    
    document.getElementById('budgetForm').addEventListener('submit', function(e) {
        e.preventDefault();
        alert("La lógica de crear presupuesto está desactivada para la prueba.");
    });
});