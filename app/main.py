# Arquivo: main.py

from fastapi import FastAPI
from app.routes.usuario_router import router as usuario_router
# 1. Importar a função de inicialização
from app.database import inicializar_bd 


app = FastAPI(
    title="SGHSS - Sistema de Gestão Hospitalar",
    version="0.1.0"
)

# 2. Chamar a função de inicialização aqui!
inicializar_bd() 


app.include_router(usuario_router)

@app.get("/")
def root():
    return {"message": "SGHSS API está no ar!"}