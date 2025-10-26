from typing import List
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Form
from db import SessionDep
from modelos.productos import Producto, ProductoActualizar, ProductoLeer
from modelos.categoria import Categoria

router = APIRouter(
    prefix="/productos",
    tags=["productos"],
)

@router.post("/", response_model=Producto)
async def crear_producto(session: SessionDep,
                         nombre: str = Form(...),
                         descripcion: str = Form(None),
                         activo: bool = Form(True),
                         precio: float = Form(None),
                         stock: int = Form(None),
                         categoria_id: int = Form(...)
                         ):
    if stock<0:
        raise HTTPException(status_code=400, detail="El stock no puede ser negativo")

    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

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
    productos = session.query(Producto).filter(Producto.activo==True).all()
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return productos

@router.get("/{producto_id}/", response_model=Producto)
async def leer_producto(producto_id: int, session: SessionDep):
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.get("/{categoria_id}/", response_model=List[Producto])
async def leer_productos_por_categoria(categoria_id: int, session: SessionDep):
    productos = session.query(Producto).filter(Producto.categoria_id==categoria_id).all()
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos para esta categoria")
    return productos

@router.get("/activo/{activo}/", response_model=List[Producto])
async def leer_productos_por_categoria(activo: bool, session: SessionDep):
    productos = session.query(Producto).filter(Producto.activo == activo).all()
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos con este estado")
    return productos


@router.put("/{producto_id}", response_model=Producto)
async def actualizar_producto(producto_id: int,
                                session: SessionDep,
                                nombre: str = Form(None),
                                descripcion: str = Form(None),
                                activo: bool = Form(None),
                                precio: float = Form(None),
                                stock: int = Form(None),
                                ):
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
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    session.delete(producto)
    session.commit()
    return producto



