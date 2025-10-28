from typing import List
from datetime import datetime, timezone, timedelta
from sqlmodel import select
from fastapi import APIRouter,Depends, HTTPException, Form, Query
from db import SessionDep
from modelos.productos import Producto, ProductoActualizar, ProductoLeer
from modelos.categoria import Categoria
from modelos.venta import Venta, VentaItem


router = APIRouter(
    prefix="/ventas",
    tags=["ventas"],
)

@router.post("/", response_model=Venta)
async def crear_venta(session: SessionDep):
    nueva_venta = Venta()

    session.add(nueva_venta)
    session.commit()
    session.refresh(nueva_venta)
    return nueva_venta

from sqlmodel import SQLModel
from sqlalchemy.orm import selectinload
from typing import Optional

# --- MODELOS DE RESPUESTA ---
class ProductoResponse(SQLModel):
    producto_id: int
    nombre: str
    descripcion: Optional[str]
    precio: Optional[float]
    stock: Optional[int]


class VentaItemResponse(SQLModel):
    id: int
    cantidad: int
    precio_unitario: int
    producto: Optional[ProductoResponse]


class VentaResponse(SQLModel):
    venta_id: int
    fecha_venta: datetime
    total: int
    items: List[VentaItemResponse]


# --- ENDPOINT ---
@router.get("/", response_model=List[VentaResponse])
async def leer_ventas(session: SessionDep):
    query = (
        select(Venta)
        .options(selectinload(Venta.items).selectinload(VentaItem.producto))
    )
    ventas = session.exec(query).all()

    if not ventas:
        raise HTTPException(status_code=404, detail="No se encontraron ventas")

    return ventas



@router.post("/{venta_id}/items/", response_model=VentaItem)
async def agregar_item_venta(
    venta_id: int,
    producto_id: int = Form(...),
    cantidad: int = Form(...),
    session: SessionDep = SessionDep(),
):
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