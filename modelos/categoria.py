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


class CategoriaActualizar(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = Field(default_factory=datetime.utcnow)
    activo: Optional[bool] = None

class CategoriaLeer(CategoriaBase):
    pass

class CategoriaEliminar(CategoriaBase):
    activo: bool = False
