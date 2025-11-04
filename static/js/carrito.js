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

function abrirDetallesProducto(productoId) {
    const productoElement = document.querySelector(`[data-producto-id="${productoId}"]`).closest('.producto-card');
    
    const contenido = `
        <div class="producto-detalle-imagen-container">
            ${productoElement.querySelector('.producto-imagen').outerHTML}
        </div>
        <div class="producto-detalle-info">
            <h2>${productoElement.querySelector('.producto-nombre').textContent}</h2>
            <div class="producto-detalle-precio">${productoElement.querySelector('.producto-precio').textContent}</div>
            <div class="producto-detalle-caracteristicas">
                ${productoElement.querySelector('.producto-detalles').innerHTML}
            </div>
            <div class="botones-detalle">
                <button class="btn-agregar-detalle" onclick="agregarAlCarritoDesdeModal('${productoId}')">
                    <i class="fas fa-plus"></i> Añadir al Carrito
                </button>
                <button class="btn-eliminar-detalle" onclick="eliminarDelCarritoDesdeModal('${productoId}')">
                    <i class="fas fa-trash"></i> Eliminar
                </button>
            </div>
        </div>
    `;
    
    document.getElementById('contenidoProducto').innerHTML = contenido;
    mostrarModal('modalProducto');
}

function mostrarCarrito() {
    if (carrito.length === 0) {
        document.getElementById('contenidoCarrito').innerHTML = `
            <div class="carrito-vacio">
                <i class="fas fa-shopping-bag" style="font-size: 48px; margin-bottom: 15px; color: #ffe4f4;"></i>
                <p>Tu carrito está vacío</p>
            </div>
        `;
    } else {
        let total = 0;
        const itemsHTML = carrito.map(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            
            return `
                <div class="item-carrito">
                    <div class="item-carrito-imagen-container">
                        <div style="width: 80px; height: 80px; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #522b0b;">
                            <i class="fas fa-image"></i>
                        </div>
                    </div>
                    <div class="item-carrito-info">
                        <h4>${item.nombre}</h4>
                        <div class="item-carrito-precio">$${item.precio}</div>
                    </div>
                    <div class="item-carrito-cantidad">
                        <button class="btn-cantidad" onclick="cambiarCantidad('${item.id}', -1)">-</button>
                        <span>${item.cantidad}</span>
                        <button class="btn-cantidad" onclick="cambiarCantidad('${item.id}', 1)">+</button>
                    </div>
                    <button class="btn-eliminar-item" onclick="eliminarItemCarrito('${item.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        }).join('');
        
        document.getElementById('contenidoCarrito').innerHTML = `
            ${itemsHTML}
            <div class="carrito-total">
                Total: $${total.toFixed(2)}
            </div>
            <button class="btn-comprar">
                <i class="fas fa-credit-card"></i> Proceder al Pago
            </button>
        `;
    }
    
    mostrarModal('modalCarrito');
}

function agregarAlCarritoDesdeModal(productoId) {
    const boton = document.querySelector(`[data-producto-id="${productoId}"]`);
    boton.click();
    actualizarCarrito();
}

function eliminarDelCarritoDesdeModal(productoId) {
    eliminarItemCarrito(productoId);
    cerrarModales();
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
        item.cantidad += cambio;
        if (item.cantidad <= 0) {
            eliminarItemCarrito(productoId);
        } else {
            actualizarCarrito();
            if (document.getElementById('modalCarrito').classList.contains('mostrar')) {
                mostrarCarrito();
            }
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

    document.querySelectorAll('.producto-imagen, .producto-nombre').forEach(element => {
        element.style.cursor = 'pointer';
        element.addEventListener('click', function() {
            const productoCard = this.closest('.producto-card');
            const productoId = productoCard.querySelector('.btn-agregar-carrito').getAttribute('data-producto-id');
            abrirDetallesProducto(productoId);
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
});