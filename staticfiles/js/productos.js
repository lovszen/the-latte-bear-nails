function mostrarDetalleProducto(productoId) {
    console.log('Cargando producto ID:', productoId);
    
    fetch(`/api/productos/${productoId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(producto => {
            if (producto.error) {
                throw new Error(producto.error);
            }
            
            const contenido = document.getElementById('contenidoProducto');
            if (!contenido) {
                throw new Error('Elemento contenidoProducto no encontrado');
            }
            
            contenido.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        ${producto.imagen ? 
                            `<img src="${producto.imagen}" class="producto-detalle-imagen" alt="${producto.nombre}">` : 
                            '<div class="producto-imagen-placeholder">Sin Imagen</div>'
                        }
                    </div>
                    <div class="col-md-6">
                        <h2>${producto.nombre}</h2>
                        <div class="producto-detalle-precio">$${producto.precio}</div>
                        
                        <div class="producto-detalle-caracteristicas">
                            <p><strong>Forma:</strong> ${producto.forma_display || producto.forma}</p>
                            <p><strong>Tamaño:</strong> ${producto.tamaño_display || producto.tamaño}</p>
                            <p><strong>Color principal:</strong> ${producto.color_principal_display || producto.color_principal}</p>
                            ${producto.color_secundario ? 
                                `<p><strong>Color secundario:</strong> ${producto.color_secundario_display || producto.color_secundario}</p>` : ''
                            }
                        </div>
                        
                        <p>${producto.descripcion || 'Sin descripción disponible.'}</p>
                        
                        <div class="botones-detalle">
                            <button class="btn-agregar-detalle"
                                    data-producto-id="${producto.id}"
                                    data-producto-nombre="${producto.nombre}"
                                    data-producto-precio="${producto.precio}"
                                    data-producto-imagen="${producto.imagen || ''}">
                                Agregar al Carrito
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            const modal = document.getElementById('modalProducto');
            if (modal) {
                modal.classList.add('mostrar');
                
                const btnAgregar = contenido.querySelector('.btn-agregar-detalle');
                if (btnAgregar) {
                    btnAgregar.addEventListener('click', function() {
                        if (typeof agregarProductoAlCarrito === 'function') {
                            agregarProductoAlCarrito(
                                this.getAttribute('data-producto-id'),
                                this.getAttribute('data-producto-nombre'),
                                this.getAttribute('data-producto-precio'),
                                this.getAttribute('data-producto-imagen')
                            );
                        }
                        modal.classList.remove('mostrar');
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error cargando producto:', error);
            alert('Error al cargar los detalles del producto: ' + error.message);
        });
}

window.mostrarDetalleProducto = mostrarDetalleProducto;