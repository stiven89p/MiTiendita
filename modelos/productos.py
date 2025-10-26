from typing import Optional, List
from datetime import datetime, timezone, timedelta
from sqlmodel import SQLModel, Field, Relationship

class ProductoBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(hours=-5))))
    fecha_actualizacion: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(hours=-5))))
    activo: bool = True
    precio: Optional[float] = None
    stock: Optional[int] = None
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.categoria_id")

class Producto(ProductoBase, table=True):
    producto_id: Optional[int] = Field(default=None, primary_key=True)
    categoria: Optional["Categoria"] = Relationship(back_populates="productos")


class ProductoActualizar(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    precio: Optional[float] = None
    stock: Optional[int] = None

class ProductoLeer(ProductoBase):
    pass

class ProductoEliminar(ProductoBase):
    pass

from modelos.categoria import Categoria

