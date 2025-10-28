from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class VentaItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    venta_id: Optional[int] = Field(default=None, foreign_key="venta.venta_id")
    producto_id: int = Field(foreign_key="producto.producto_id")
    cantidad: int
    precio_unitario: int

    venta: Optional["Venta"] = Relationship(back_populates="items")
    producto: Optional["Producto"] = Relationship()



class Venta(SQLModel, table=True):
    venta_id: Optional[int] = Field(default=None, primary_key=True)
    fecha_venta: datetime = Field(default_factory=datetime.utcnow)
    total: int = Field(default_factory=int)

    items: List[VentaItem] = Relationship(back_populates="venta")

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



from modelos.productos import Producto
