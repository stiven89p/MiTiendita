from fastapi import FastAPI
from db import create_tables
from routers import categoria
from routers import productos
from routers import venta

app = FastAPI(lifespan=create_tables,title="API de Gestión de Categorías", version="1.0.0")

app.include_router(categoria.router)
app.include_router(productos.router)
app.include_router(venta.router)
