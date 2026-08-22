from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine
from app.routers.candidatos import router as candidatos_router
from app.routers.resultados import router as resultados_router
from app.routers.municipios import router as municipios_router
from app.routers.estatisticas import router as estatisticas_router
from app.routers.estados import router as estados_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Eleições 2026 API",
    description=(
        "API brasileira para candidatos, resultados "
        "e estatísticas das Eleições 2026"
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(candidatos_router)
app.include_router(resultados_router)
app.include_router(municipios_router)
app.include_router(estatisticas_router)
app.include_router(estados_router)


@app.get("/")
def root():
    return {
        "app": "Eleições 2026 API",
        "status": "online",
        "ano": 2026,
        "fonte": "Tribunal Superior Eleitoral",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }
