let carrito = [];
const contadorCarrito = document.getElementById('contador-carrito');

function agregarProductoAlCarrito(productoId, productoNombre, productoPrecio, productoImagen) {
    const productoExistente = carrito.find(item => item.id === productoId);
    
    let imagenFinal = productoImagen;
    if (!productoImagen || productoImagen === 'None' || productoImagen === '') {
        imagenFinal = '/static/images/placeholder.png';
    }
    
    if (productoExistente) {
        productoExistente.cantidad += 1;
    } else {
        carrito.push({
            id: productoId,
            nombre: productoNombre,
            precio: parseFloat(productoPrecio),
            imagen: imagenFinal,
            cantidad: 1
        });
    }
    
    actualizarCarrito();
}

function actualizarCarrito() {
    const totalItems = carrito.reduce((sum, item) => sum + item.cantidad, 0);
    contadorCarrito.textContent = totalItems;
    localStorage.setItem('carrito', JSON.stringify(carrito));
    
    if (typeof window.updateBudgetButtonVisibility === 'function') {
        window.updateBudgetButtonVisibility();
    }
}

function sincronizarCarrito() {
    const carritoGuardado = localStorage.getItem('carrito');
    if (carritoGuardado) {
        carrito = JSON.parse(carritoGuardado);
    } else {
        carrito = []; 
    }
    actualizarCarrito();
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
    const resumenCantidad = document.getElementById('resumen-cantidad');
    const resumenTotal = document.getElementById('resumen-total');
    
    if (carrito.length === 0) {
        contenidoDiv.innerHTML = `
            <div class="carrito-vacio">
                <i class="fas fa-shopping-bag"></i>
                <p>Tu carrito está vacío</p>
                <p style="font-size: 0.9em; margin-top: 10px; color: #888;">Agrega algunos productos para continuar</p>
            </div>
        `;
        resumenCantidad.textContent = '0';
        resumenTotal.textContent = '$0.00';
    } else {
        let total = 0;
        let cantidadTotal = 0;
        
        const itemsHTML = carrito.map(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            cantidadTotal += item.cantidad;
            
            const imagenUrl = item.imagen && item.imagen !== 'None' ? item.imagen : '/static/images/placeholder.png';
            
            return `
                <div class="producto-carrito-card">
                    <img src="${imagenUrl}" 
                         class="producto-carrito-imagen" 
                         alt="${item.nombre}"
                         onerror="this.onerror=null; this.src='/static/images/placeholder.png'">
                    
                    <div class="producto-carrito-info">
                        <div class="producto-carrito-nombre">${item.nombre}</div>
                        <div class="producto-carrito-precio">$${item.precio}</div>
                    </div>
                    
                    <div class="controles-cantidad">
                        <button class="btn-cantidad" data-id="${item.id}" data-cambio="-1">-</button>
                        <span class="cantidad-actual">${item.cantidad}</span>
                        <button class="btn-cantidad" data-id="${item.id}" data-cambio="1">+</button>
                    </div>
                    
                    <button class="btn-eliminar-item" data-id="${item.id}" title="Eliminar producto">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        }).join('');
        
        contenidoDiv.innerHTML = itemsHTML;
        resumenCantidad.textContent = cantidadTotal;
        resumenTotal.textContent = `$${total.toFixed(2)}`;
        
        agregarListenersBotonesCarrito();
    }
    
    if (typeof window.updateBudgetButtonVisibility === 'function') {
        window.updateBudgetButtonVisibility();
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
    sincronizarCarrito();
    
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
    sincronizarCarrito();

    document.querySelectorAll('.btn-agregar-carrito').forEach(button => {
        button.addEventListener('click', function() {
            const productoId = this.getAttribute('data-producto-id');
            const productoNombre = this.getAttribute('data-producto-nombre');
            const productoPrecio = parseFloat(this.getAttribute('data-producto-precio'));
            const productoImagen = this.getAttribute('data-producto-imagen');

            agregarProductoAlCarrito(productoId, productoNombre, productoPrecio, productoImagen);
            
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

    const iconoCarrito = document.querySelector('.tienda-iconos .fa-shopping-bag').closest('div');
    if (iconoCarrito) {
        iconoCarrito.addEventListener('click', function() {
            mostrarCarrito();
        });
    }

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
});