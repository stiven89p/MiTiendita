from typing import List
from datetime import datetime, timezone, timedelta
from sqlmodel import select
from fastapi import APIRouter, HTTPException, Form, Query
from db import SessionDep
from modelos.productos import Producto, ProductoLeer
from modelos.categoria import Categoria

router = APIRouter(
    prefix="/productos",
    tags=["productos"],
)

@router.post("/", response_model=ProductoLeer)
async def crear_producto(session: SessionDep,
                         nombre: str = Form(...),
                         descripcion: str = Form(None),
                         activo: bool = Form(True),
                         precio: int = Form(None),
                         stock: int = Form(None),
                         categoria_id: int = Form(...)
                         ):
    """
       Crear un nuevo producto.

       Registra un nuevo producto en la base de datos, asociado a una categoría existente y activa.
       Verifica que no exista otro producto con el mismo nombre y que los valores de stock sean válidos.

       Args:
           session (SessionDep): Dependencia que provee la sesión de la base de datos.
           nombre (str): Nombre del producto. Obligatorio.
           descripcion (str | None): Descripción opcional del producto.
           activo (bool): Estado activo del producto. Por defecto `True`.
           precio (int | None): Precio del producto.
           stock (int | None): Cantidad disponible en inventario. Debe ser mayor o igual a 0.
           categoria_id (int): ID de la categoría a la que pertenece el producto.

       Returns:
           Producto: Instancia del producto recién creado.

       Raises:
           HTTPException: 400 si el stock es negativo.
           HTTPException: 404 si la categoría no existe.
           HTTPException: 400 si la categoría está inactiva.
           HTTPException: 400 si ya existe un producto con el mismo nombre.
       """
    if stock is not None and stock < 0:
        raise HTTPException(status_code=400, detail="El stock no puede ser negativo")

    categoria = session.get(Categoria, categoria_id)

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if not categoria.activo:
        raise HTTPException(status_code=400, detail="La categoría está inactiva")


    nuevo_producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        activo=activo,
        precio=precio,
        stock=stock,
        categoria_id=categoria_id,
    )
    productos_comprobacion = session.query(Producto).filter(Producto.nombre==nuevo_producto.nombre).all()
    if productos_comprobacion:
        raise HTTPException(status_code=400, detail="El producto con ese nombre ya existe")
    session.add(nuevo_producto)
    session.commit()
    session.refresh(nuevo_producto)
    return nuevo_producto

@router.get("/", response_model=List[ProductoLeer])
async def leer_productos(session: SessionDep):
    productos = (
        session.query(Producto)
        .join(Categoria)
        .filter(Producto.activo == True, Categoria.activo == True)
        .all()
    )
    """
        Leer productos activos.

        Recupera todos los productos activos cuyas categorías también estén activas.

        Args:
            session (SessionDep): Dependencia que provee la sesión de la base de datos.

        Returns:
            List[Producto]: Lista de productos activos con categorías activas.

        Raises:
            HTTPException: 404 si no se encuentran productos.
        """
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return productos

@router.get("/precio/", response_model=List[ProductoLeer])
async def leer_productos_por_precio(
    session: SessionDep,
    precio_min: int = Query(..., gt=0),
    precio_max: int = Query(..., gt=0)
    ):
    """
        Leer productos por rango de precios.

        Devuelve todos los productos cuyo precio se encuentre entre los valores mínimos y máximos especificados.

        Args:
            session (SessionDep): Dependencia que provee la sesión de la base de datos.
            precio_min (int): Valor mínimo del rango de precios. Debe ser mayor que 0.
            precio_max (int): Valor máximo del rango de precios. Debe ser mayor que 0.

        Returns:
            List[Producto]: Lista de productos cuyo precio está dentro del rango.

        Raises:
            HTTPException: 400 si `precio_min` es mayor que `precio_max`.
            HTTPException: 404 si no se encuentran productos en el rango indicado.
        """
    if precio_min > precio_max:
        raise HTTPException(
            status_code=400, detail="El precio mínimo no puede ser mayor que el precio máximo"
        )
    consulta = select(Producto).where(
        Producto.precio.between(precio_min, precio_max)
    )
    productos = session.exec(consulta).all()
    if not productos:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron productos entre {precio_min} y {precio_max}",
        )
    return productos

@router.get("/stock/", response_model=List[ProductoLeer])
async def leer_productos_por_stock(
    session: SessionDep,
    stock_min: int = Query(..., gt=0),
    stock_max: int = Query(..., gt=0)
    ):
    """
        Leer productos por rango de stock.

        Devuelve todos los productos cuyo stock esté dentro del rango especificado.

        Args:
            session (SessionDep): Dependencia que provee la sesión de la base de datos.
            stock_min (int): Valor mínimo del stock. Debe ser mayor que 0.
            stock_max (int): Valor máximo del stock. Debe ser mayor que 0.

        Returns:
            List[Producto]: Lista de productos con stock dentro del rango.

        Raises:
            HTTPException: 400 si `stock_min` es mayor que `stock_max`.
            HTTPException: 404 si no se encuentran productos en el rango indicado.
        """
    if stock_min > stock_max:
        raise HTTPException(
            status_code=400, detail="El stock mínimo no puede ser mayor que el stock máximo"
        )
    consulta = select(Producto).where(
        Producto.stock.between(stock_min, stock_max)
    )
    productos = session.exec(consulta).all()
    if not productos:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron productos entre {stock_min} y {stock_max}",
        )
    return productos

@router.get("/{producto_id}/", response_model=ProductoLeer)
async def leer_producto_por_id(producto_id: int, session: SessionDep):
    """
        Leer un producto por ID.

        Recupera un producto específico a partir de su identificador.

        Args:
            producto_id (int): ID del producto a consultar.
            session (SessionDep): Dependencia que provee la sesión de la base de datos.

        Returns:
            Producto: Instancia del producto correspondiente.

        Raises:
            HTTPException: 404 si el producto no existe.
        """
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.get("/categoria/{categoria_id}/", response_model=List[ProductoLeer])
async def leer_productos_por_categoria(categoria_id: int, session: SessionDep):
    """
        Leer productos por categoría.

        Obtiene todos los productos pertenecientes a una categoría específica.

        Args:
            categoria_id (int): ID de la categoría a consultar.
            session (SessionDep): Dependencia que provee la sesión de la base de datos.

        Returns:
            List[Producto]: Lista de productos asociados a la categoría.

        Raises:
            HTTPException: 404 si no se encuentran productos para la categoría indicada.
        """
    productos = session.query(Producto).filter(Producto.categoria_id==categoria_id).all()
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos para esta categoria")
    return productos

@router.get("/activo/{activo}/", response_model=List[ProductoLeer])
async def leer_productos_por_estado(activo: bool, session: SessionDep):
    """
        Leer productos por estado activo.

        Recupera todos los productos que coinciden con el estado de actividad indicado.

        Args:
            activo (bool): Estado de los productos a consultar.
            session (SessionDep): Dependencia que provee la sesión de la base de datos.

        Returns:
            List[Producto]: Lista de productos con el estado solicitado.

        Raises:
            HTTPException: 404 si no se encuentran productos con ese estado.
        """
    productos = session.query(Producto).filter(Producto.activo == activo).all()
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos con este estado")
    return productos

@router.get("/categoria/{categoria_id}/activo/{activo}/")
async def leer_productos_por_categoria_y_estado(categoria_id: int, activo: bool, session: SessionDep):
    """
        Leer productos por categoría y estado activo.

        Obtiene todos los productos que pertenecen a una categoría específica y que coinciden con el estado de actividad indicado.

        Args:
            categoria_id (int): ID de la categoría a consultar.
            activo (bool): Estado de los productos a consultar.
            session (SessionDep): Dependencia que provee la sesión de la base de datos.

        Returns:
            List[Producto]: Lista de productos que coinciden con la categoría y el estado solicitado.

        Raises:
            HTTPException: 404 si no se encuentran productos que coincidan con los criterios.
        """
    productos = session.query(Producto).filter(Producto.categoria_id==categoria_id, Producto.activo==activo).all()
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos con estos criterios")
    return productos

@router.put("/{producto_id}/", response_model=Producto)
async def actualizar_producto(producto_id: int,
                                session: SessionDep,
                                nombre: str = Form(None),
                                descripcion: str = Form(None),
                                activo: bool = Form(None),
                                precio: int = Form(None),
                                stock: int = Form(None),
                                ):
    """
       Actualizar un producto existente.

       Modifica los campos proporcionados (nombre, descripción, activo, precio, stock) del producto especificado.
       Solo se actualizan los campos que no sean `None`. Actualiza además la fecha de modificación.

       Args:
           producto_id (int): ID del producto a actualizar.
           session (SessionDep): Dependencia que provee la sesión de la base de datos.
           nombre (str | None): Nuevo nombre. Si es `None`, no se modifica.
           descripcion (str | None): Nueva descripción. Si es `None`, no se modifica.
           activo (bool | None): Nuevo estado. Si es `None`, no se modifica.
           precio (int | None): Nuevo precio. Si es `None`, no se modifica.
           stock (int | None): Nuevo valor de stock. Si es `None`, no se modifica.

       Returns:
           Producto: Instancia del producto actualizada.

       Raises:
           HTTPException: 400 si el stock es negativo.
           HTTPException: 404 si el producto no existe.
       """
    if stock is not None and stock < 0:
        raise HTTPException(status_code=400, detail="El stock no puede ser negativo")

    producto = session.get(Producto, producto_id)

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if nombre is not None:
        producto.nombre = nombre
    if descripcion is not None:
        producto.descripcion = descripcion
    if activo is not None:
        producto.activo = activo
    if precio is not None:
        producto.precio = precio
    if stock is not None:
        producto.stock = stock

    producto.fecha_actualizacion = datetime.now(timezone(timedelta(hours=-5)))

    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto

@router.delete("/{producto_id}", response_model=ProductoLeer)
async def eliminar_producto(producto_id: int, session: SessionDep):
    """
        Eliminar un producto.

        Borra de la base de datos el producto correspondiente al identificador proporcionado.

        Args:
            producto_id (int): ID del producto a eliminar.
            session (SessionDep): Dependencia que provee la sesión de la base de datos.

        Returns:
            ProductoLeer: Representación del producto eliminado.

        Raises:
            HTTPException: 404 si el producto no existe.
        """
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    producto.eliminacion = False
    producto.activo = False
    producto.precio = 0
    producto.stock = 0

    session.commit()
    return producto



