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
    """Crear una nueva categoría.

        Crea y persiste una nueva instancia de `Categoria` en la base de datos usando los
        campos recibidos a través de formularios.

        Args:
            session (SessionDep): Dependencia que provee la sesión de la base de datos.
            nombre (str): Nombre de la categoría. Obligatorio.
            descripcion (str | None): Descripción opcional de la categoría.
            activo (bool): Indica si la categoría está activa. Por defecto `True`.

        Returns:
            CategoriaLeer: Esquema de lectura con los datos de la categoría creada.

        Raises:
            HTTPException: Código 400 si ya existe una categoría con el mismo `nombre`.
        """

    nueva_categoria = Categoria(
        nombre=nombre,
        descripcion=descripcion,
        activo=activo
    )

    categorias_comprobacion = session.query(Categoria).filter(Categoria.nombre==nueva_categoria.nombre).all()
    if categorias_comprobacion:
        raise HTTPException(status_code=400, detail="La categoría con ese nombre ya existe")
    session.add(nueva_categoria)
    session.commit()
    session.refresh(nueva_categoria)
    return nueva_categoria

@router.get("/", response_model=List[Categoria])
async def leer_categorias(session: SessionDep):
    """
    Leer categorías activas.

    Obtiene todas las categorías marcadas como activas desde la base de datos.

    Args:
        session (SessionDep): Dependencia que provee la sesión de la base de datos.

    Returns:
        List[Categoria]: Lista de instancias de `Categoria` activas.

    Raises:
        HTTPException: 404 si no se encuentran categorías.
    """
    categorias = session.query(Categoria).filter(Categoria.activo==True).all()
    if not categorias:
        raise HTTPException(status_code=404, detail="No se encontraron categorías")
    return categorias

@router.get("/categoria_id/{categoria_id}/", response_model=Categoria)
async def leer_categoria_id(categoria_id: int, session: SessionDep):
    """
    Leer una categoría por ID.

    Recupera una categoría por su identificador.

    Args:
        categoria_id (int): ID de la categoría a recuperar.
        session (SessionDep): Dependencia que provee la sesión de la base de datos.

    Returns:
        Categoria: Instancia de `Categoria` encontrada.

    Raises:
        HTTPException: 404 si la categoría no existe.
    """
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@router.get("/activo/{activo}/", response_model=List[Categoria])
async def leer_categorias_activo(activo: bool, session: SessionDep):
    """
    Leer categorías por estado activo.

    Obtiene todas las categorías que coinciden con el estado activo proporcionado.

    Args:
        activo (bool): Estado activo para filtrar categorías.
        session (SessionDep): Dependencia que provee la sesión de la base de datos.

    Returns:
        List[Categoria]: Lista de instancias de `Categoria` que coinciden con el estado activo.

    Raises:
        HTTPException: 404 si no se encuentran categorías.
    """
    categorias = session.query(Categoria).filter(Categoria.activo==activo).all()
    if not categorias:
        raise HTTPException(status_code=404, detail="No se encontraron categorías")
    return categorias

@router.put("/{categoria_id}/", response_model=Categoria)
async def actualizar_categoria(categoria_id: int,
                               session: SessionDep,
                               nombre: str = Form(None),
                               descripcion: str = Form(None),
                               activo: bool = Form(None),
                               ):
    """
    Actualizar una categoría existente.

    Actualiza los campos proporcionados (nombre, descripción, activo) de la categoría especificada.
    Sólo los parámetros no nulos serán aplicados.

    Args:
        categoria_id (int): ID de la categoría a actualizar.
        session (SessionDep): Dependencia que provee la sesión de la base de datos.
        nombre (str | None): Nuevo nombre. Si es `None` no se modifica.
        descripcion (str | None): Nueva descripción. Si es `None` no se modifica.
        activo (bool | None): Nuevo estado. Si es `None` no se modifica.

    Returns:
        Categoria: Instancia de `Categoria` actualizada.

    Raises:
        HTTPException: 404 si la categoría no existe.
    """
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


@router.delete("/{categoria_id}", response_model=Categoria)
async def eliminar_categoria(categoria_id: int, session: SessionDep):
    """
    Eliminar una categoría y sus productos asociados.

    Borra la categoría indicada y elimina los productos relacionados antes de borrar la categoría.

    Args:
        categoria_id (int): ID de la categoría a eliminar.
        session (SessionDep): Dependencia que provee la sesión de la base de datos.

    Returns:
        Categoria: Instancia de `Categoria` eliminada (tal como estaba antes del borrado).

    Raises:
        HTTPException: 404 si la categoría no existe.
    """
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    for producto in categoria.productos:
        session.delete(producto)

    session.delete(categoria)
    session.commit()
    return categoria

