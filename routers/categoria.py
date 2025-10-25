from typing import List
from fastapi import APIRouter, HTTPException, Form
from db import SessionDep
from modelos.categoria import Categoria, CategoriaActualizar, CategoriaLeer

router = APIRouter(
    prefix="/categorias",
    tags=["categorias"],
)

@router.post("/", response_model=CategoriaLeer)
async def crear_categoria(session: SessionDep,
                          nombre: str = Form(...),
                          descripcion: str = Form(None),
                          activo: bool = Form(True),
                          ):

    nueva_categoria = Categoria(
        nombre=nombre,
        descripcion=descripcion,
        activo=activo
    )
    session.add(nueva_categoria)
    session.commit()
    session.refresh(nueva_categoria)
    return nueva_categoria

@router.get("/", response_model=List[CategoriaLeer])
async def leer_categorias(session: SessionDep):
    categorias = session.query(Categoria).all()
    return categorias

@router.get("/{categoria_id}", response_model=CategoriaLeer)
async def leer_categoria(categoria_id: int, session: SessionDep):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@router.put("/{categoria_id}", response_model=Categoria)
async def actualizar_categoria(categoria_id: int,
                               session: SessionDep,
                               nombre: str = Form(None),
                               descripcion: str = Form(None),
                               activo: bool = Form(None),
                               ):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if nombre is not None:
        categoria.nombre = nombre
    if descripcion is not None:
        categoria.descripcion = descripcion
    if activo is not None:
        categoria.activo = activo

    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


