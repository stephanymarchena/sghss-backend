from fastapi import FastAPI
from app.routes.usuario_router import router as usuario_router
from app.database import inicializar_bd 
from app.routes.auth_router import router as auth_router


app = FastAPI(
    title="SGHSS - Sistema de Gestão Hospitalar",
    version="0.1.0"
)

inicializar_bd() 

app.include_router(usuario_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "SGHSS API está no ar!"}