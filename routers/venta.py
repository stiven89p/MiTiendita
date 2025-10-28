from typing import List
from sqlalchemy.orm import selectinload
from sqlmodel import select
from fastapi import APIRouter,HTTPException, Form
from db import SessionDep
from modelos.categoria import Categoria
from modelos.productos import Producto
from modelos.venta import Venta, VentaItem, VentaResponse


router = APIRouter(
    prefix="/ventas",
    tags=["ventas"],
)

@router.post("/", response_model=Venta)
async def crear_venta(session: SessionDep):
    """
        Crear una nueva venta.

        Registra una nueva venta vacía en la base de datos. Esta venta puede posteriormente
        recibir ítems asociados mediante el endpoint de agregar items.

        Args:
            session (SessionDep): Dependencia que provee la sesión de la base de datos.

        Returns:
            Venta: Instancia de la venta recién creada.

        Raises:
            HTTPException: 400 si ocurre un error al crear la venta.
        """
    nueva_venta = Venta()

    session.add(nueva_venta)
    session.commit()
    session.refresh(nueva_venta)
    return nueva_venta

@router.post("/{venta_id}/items/", response_model=VentaItem)
async def agregar_item_venta(
    venta_id: int,
    producto_id: int = Form(...),
    cantidad: int = Form(...),
    session: SessionDep = SessionDep(),
):
    """
        Agregar un ítem a una venta existente.

        Asocia un producto activo a una venta determinada, validando que tanto la categoría
        como el producto estén activos y que exista suficiente stock. Actualiza el total
        de la venta y el stock del producto.

        Args:
            venta_id (int): ID de la venta a la que se agregará el ítem.
            producto_id (int): ID del producto a vender.
            cantidad (int): Cantidad del producto a agregar.
            session (SessionDep): Dependencia que provee la sesión de la base de datos.

        Returns:
            VentaItem: Ítem de venta recién agregado con la información del producto y el precio unitario.

        Raises:
            HTTPException: 404 si no se encuentran productos activos con categoría activa.
            HTTPException: 404 si la venta no existe.
            HTTPException: 404 si el producto no existe o está inactivo.
            HTTPException: 400 si el stock del producto es insuficiente.
        """
    categoria = (
        session.query(Producto)
        .join(Categoria)
        .filter(Producto.activo == True, Categoria.activo == True)
        .all()
    )
    if not categoria:
        raise HTTPException(status_code=404, detail="No se encontraron productos activos con categoría activa")

    venta = session.get(Venta, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    producto = session.get(Producto, producto_id)
    if not producto or not producto.activo:
        raise HTTPException(status_code=404, detail="Producto no encontrado o inactivo")

    if producto.stock < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente para el producto")

    precio_unitario = producto.precio
    nuevo_item = VentaItem(
        venta_id=venta_id,
        producto_id=producto_id,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
    )

    producto.stock -= cantidad
    venta.total += precio_unitario * cantidad

    session.add(nuevo_item)
    session.add(producto)
    session.add(venta)
    session.commit()
    session.refresh(nuevo_item)
    return nuevo_item

@router.get("/", response_model=List[VentaResponse])
async def leer_ventas(session: SessionDep):
    """
        Leer todas las ventas registradas.

        Obtiene la lista completa de ventas con sus ítems asociados y los detalles de cada producto.

        Args:
            session (SessionDep): Dependencia que provee la sesión de la base de datos.

        Returns:
            List[VentaResponse]: Lista de ventas con los productos e ítems asociados.

        Raises:
            HTTPException: 404 si no se encuentran ventas registradas.
        """
    query = (
        select(Venta)
        .options(selectinload(Venta.items).selectinload(VentaItem.producto))
    )
    ventas = session.exec(query).all()

    if not ventas:
        raise HTTPException(status_code=404, detail="No se encontraron ventas")

    return ventas

@router.get("/{venta_id}/", response_model=List[VentaResponse])
async def leer_ventas(session: SessionDep, venta_id: int):
    """
        Leer una venta por ID.

        Recupera una venta específica junto con sus ítems y los detalles de cada producto asociado.

        Args:
            session (SessionDep): Dependencia que provee la sesión de la base de datos.
            venta_id (int): Identificador de la venta a consultar.

        Returns:
            List[VentaResponse]: Lista con la información de la venta solicitada y sus ítems.

        Raises:
            HTTPException: 404 si no se encuentra la venta indicada.
        """
    query = (
        select(Venta)
        .options(selectinload(Venta.items).selectinload(VentaItem.producto))
        .where(Venta.venta_id == venta_id)
    )
    ventas = session.exec(query).all()

    if not ventas:
        raise HTTPException(status_code=404, detail="No se encontraron ventas")

    return ventas