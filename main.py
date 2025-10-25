from fastapi import FastAPI
from db import create_tables
from routers import categoria


app = FastAPI(lifespan=create_tables,title="API de Gestión de Categorías", version="1.0.0")

app.include_router(categoria.router)
