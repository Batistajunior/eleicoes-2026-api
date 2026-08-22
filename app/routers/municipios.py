from typing import Optional

from fastapi import APIRouter, Query


router = APIRouter(
    prefix="/municipios",
    tags=["Municípios"],
)


@router.get("")
def listar_municipios(
    uf: Optional[str] = Query(default=None),
):
    return {
        "ano": 2026,
        "uf": uf.upper() if uf else None,
        "total": 0,
        "municipios": [],
        "dados_disponiveis": False,
        "mensagem": (
            "A base municipal ainda não foi importada "
            "para a API."
        ),
        "fonte": "Tribunal Superior Eleitoral - TSE",
    }


@router.get("/{uf}/{municipio}")
def obter_municipio(
    uf: str,
    municipio: str,
):
    return {
        "ano": 2026,
        "uf": uf.upper(),
        "municipio": municipio,
        "dados_disponiveis": False,
        "mensagem": (
            "Os dados eleitorais municipais ainda "
            "não foram importados para a API."
        ),
        "fonte": "Tribunal Superior Eleitoral - TSE",
    }
