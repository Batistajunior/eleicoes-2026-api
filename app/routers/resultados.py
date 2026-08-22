from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/resultados",
    tags=["Resultados"],
)


def _resposta_sem_apuracao(
    tipo: str,
    turno: int,
    uf: Optional[str] = None,
    municipio: Optional[str] = None,
):
    return {
        "ano": 2026,
        "turno": turno,
        "tipo": tipo,
        "uf": uf,
        "municipio": municipio,
        "apuracao_disponivel": False,
        "percentual_apurado": 0.0,
        "ultima_atualizacao": None,
        "mensagem": (
            "A apuração oficial das Eleições 2026 "
            "ainda não está disponível."
        ),
        "resultados": [],
        "fonte": "Tribunal Superior Eleitoral - TSE",
    }


@router.get("")
def resultados(
    turno: int = Query(default=1, ge=1, le=2),
):
    return _resposta_sem_apuracao(
        tipo="brasil",
        turno=turno,
    )


@router.get("/brasil")
def resultados_brasil(
    turno: int = Query(default=1, ge=1, le=2),
):
    return _resposta_sem_apuracao(
        tipo="brasil",
        turno=turno,
    )


@router.get("/estados")
def resultados_estados(
    turno: int = Query(default=1, ge=1, le=2),
):
    return _resposta_sem_apuracao(
        tipo="estados",
        turno=turno,
    )


@router.get("/estado/{uf}")
def resultados_estado(
    uf: str,
    turno: int = Query(default=1, ge=1, le=2),
):
    return _resposta_sem_apuracao(
        tipo="estado",
        turno=turno,
        uf=uf.upper(),
    )


@router.get("/municipios")
def resultados_municipios(
    turno: int = Query(default=1, ge=1, le=2),
    uf: Optional[str] = Query(default=None),
):
    return _resposta_sem_apuracao(
        tipo="municipios",
        turno=turno,
        uf=uf.upper() if uf else None,
    )


@router.get("/municipio/{uf}/{municipio}")
def resultados_municipio(
    uf: str,
    municipio: str,
    turno: int = Query(default=1, ge=1, le=2),
):
    return _resposta_sem_apuracao(
        tipo="municipio",
        turno=turno,
        uf=uf.upper(),
        municipio=municipio,
    )


@router.get("/candidatos")
def resultados_candidatos(
    turno: int = Query(default=1, ge=1, le=2),
    uf: Optional[str] = Query(default=None),
    cargo: Optional[str] = Query(default=None),
):
    resposta = _resposta_sem_apuracao(
        tipo="candidatos",
        turno=turno,
        uf=uf.upper() if uf else None,
    )

    resposta["cargo"] = cargo

    return resposta


@router.get("/partidos")
def resultados_partidos(
    turno: int = Query(default=1, ge=1, le=2),
    uf: Optional[str] = Query(default=None),
):
    return _resposta_sem_apuracao(
        tipo="partidos",
        turno=turno,
        uf=uf.upper() if uf else None,
    )


@router.get("/status")
def status_apuracao():
    return {
        "ano": 2026,
        "primeiro_turno": {
            "apuracao_disponivel": False,
            "percentual_apurado": 0.0,
            "ultima_atualizacao": None,
        },
        "segundo_turno": {
            "apuracao_disponivel": False,
            "percentual_apurado": 0.0,
            "ultima_atualizacao": None,
        },
        "fonte": "Tribunal Superior Eleitoral - TSE",
    }
