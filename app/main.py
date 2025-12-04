from fastapi import FastAPI
from app.routes.usuario_router import router as usuario_router
from app.routes.auth_router import router as auth_router
from app.routes.paciente_router import router as paciente_router
from app.routes.profissional_router import router as profissional_router
from app.routes.consulta_router import router as consulta_router
from app.routes.agenda_router import router as agenda_router
from app.routes import prontuario_router
from app.routes import exame_router
from app.routes import admin_router
from app.database import inicializar_bd 



app = FastAPI(
    title="SGHSS - Sistema de Gestão Hospitalar",
    version="0.1.0"
)

inicializar_bd()

app.include_router(usuario_router)
app.include_router(auth_router)
app.include_router(paciente_router)
app.include_router(profissional_router)
app.include_router(consulta_router)
app.include_router(agenda_router)
app.include_router(prontuario_router.router)
app.include_router(exame_router.router)
app.include_router(admin_router.router)


@app.get("/")
def root():
    return {"message": "SGHSS API está no ar!"}
