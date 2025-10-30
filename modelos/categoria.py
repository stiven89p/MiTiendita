from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class CategoriaBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    activo: bool = True

class Categoria(CategoriaBase, table=True):
    categoria_id: Optional[int] = Field(default=None, primary_key=True)
    productos: List["Producto"] = Relationship(back_populates="categoria")
    eliminacion: bool = True


class CategoriaActualizar(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = Field(default_factory=datetime.utcnow)
    activo: Optional[bool] = None

class CategoriaLeer(SQLModel):
    categoria_id: Optional[int]
    nombre: str
    descripcion: Optional[str] = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    activo: bool = True

class CategoriaConProductos(CategoriaLeer):
    productos: List["ProductoLeer"] = []


from modelos.productos import Producto, ProductoLeer