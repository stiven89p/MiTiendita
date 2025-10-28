# MiTienda - Modelos y Mapa de Endpoints

## Resumen
Proyecto FastAPI + SQLModel para gestionar categorías, productos y ventas. Incluye endpoint para crear una venta con varios ítems validando stock y restando cantidades en la misma transacción.

## Ubicación de archivos importantes
- `modelos/categoria.py`
- `modelos/productos.py`
- `modelos/venta.py`
- `routers/categoria.py`
- `routers/productos.py`
- `routers/venta.py`
- `db.py`

---

## Modelos (resumen)
- Categoria
  - `id: Optional[int]` \(PK\)
  - `nombre: str`
  - `descripcion: Optional[str]`
  - `activo: bool` \- si está `False`, no mostrar sus productos

- Producto
  - `id: Optional[int]` \(PK\)
  - `nombre: str`
  - `descripcion: Optional[str]`
  - `precio: Optional[float]`
  - `stock: Optional[int]` \- puede ser `None` (validar y rechazar operaciones si es inválido)
  - `activo: bool`
  - `categoria_id: int` \(FK \-> `categoria.id`\)

- Venta
  - `id: Optional[int]` \(PK\)
  - `fecha_venta: datetime`
  - `total: float`
  - relación `items: List[VentaItem]`

- VentaItem
  - `id: Optional[int]` \(PK\)
  - `venta_id: int` \(FK \-> `venta.id`\)
  - `producto_id: int` \(FK \-> `producto.id`\)
  - `cantidad: int`
  - `precio_unitario: float`

---

## Reglas de negocio importantes
- No mostrar productos cuya `categoria.activo` es `False`.
- No permitir venta si `producto.activo` es `False`.
- Si `producto.stock` es `None` o menor que la cantidad requerida, rechazar la operación con 400.
- Todas las operaciones que afectan stock y creación de venta deben ejecutarse en la misma transacción; en error, hacer rollback.

---

## Mapa de Endpoints

### Categorías (`routers/categoria.py`)
- `GET /categorias/` \- listar categorías
- `GET /categorias/{id}/` \- detalle categoría
- `POST /categorias/` \- crear categoría
- `PUT /categorias/{id}/` \- actualizar (incluir `activo` para habilitar/deshabilitar)
- `DELETE /categorias/{id}/` \- eliminar

### Productos (`routers/productos.py`)
- `GET /productos/` \- listar productos **solo** de categorías activas por defecto. Ejemplo de filtro:
  - SQL: `select(Producto).join(Categoria).where(Categoria.activo == True)`
- `GET /productos/{id}/` \- detalle (incluir `categoria`)
- `POST /productos/` \- crear producto (validar que `categoria` exista y esté activa si es necesario)
- `PUT /productos/{id}/` \- actualizar producto (manejar `stock` `None` y `activo`)
- `DELETE /productos/{id}/` \- eliminar

## Ventas (`routers/venta.py`)

- `GET /ventas/` \- listar ventas con `items` y cada `item.producto` (usar `selectinload` para precargar relaciones).
- `GET /ventas/{venta_id}/` \- detalle de una venta con ítems y productos embebidos.
- `POST /ventas/` \- crear venta vacía (opcional).
- `POST /ventas/{venta_id}/items/` \- agregar un item a una venta (valida stock y resta).
    - Request Body:
        ```json
        {
        "producto_id": int,
        "cantidad": int
        }
        ```
    - Validaciones:
        - Verificar que el producto exista y esté activo.
        - Verificar que el stock sea suficiente (no `None` y >= cantidad).
        - Si válido, restar stock y crear `VentaItem`.
        - Actualizar total de la venta.