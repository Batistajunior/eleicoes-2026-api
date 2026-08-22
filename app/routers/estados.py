from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidato import Candidato


router = APIRouter(
    prefix="/estados",
    tags=["Estados"],
)


NOMES_ESTADOS = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}


@router.get("")
def listar_estados(
    db: Session = Depends(get_db),
):
    totais = dict(
        db.query(
            Candidato.uf,
            func.count(Candidato.id),
        )
        .filter(Candidato.uf != "BR")
        .group_by(Candidato.uf)
        .all()
    )

    estados = []

    for uf, nome in NOMES_ESTADOS.items():
        estados.append(
            {
                "uf": uf,
                "nome": nome,
                "total_candidatos": int(
                    totais.get(uf, 0)
                ),
            }
        )

    return {
        "total": len(estados),
        "estados": estados,
        "fonte": "Tribunal Superior Eleitoral - TSE",
    }


@router.get("/{uf}")
def obter_estado(
    uf: str,
    db: Session = Depends(get_db),
):
    uf = uf.upper()

    total = (
        db.query(func.count(Candidato.id))
        .filter(Candidato.uf == uf)
        .scalar()
        or 0
    )

    cargos = (
        db.query(
            Candidato.cargo,
            func.count(Candidato.id),
        )
        .filter(Candidato.uf == uf)
        .group_by(Candidato.cargo)
        .order_by(Candidato.cargo)
        .all()
    )

    return {
        "uf": uf,
        "nome": NOMES_ESTADOS.get(
            uf,
            uf,
        ),
        "total_candidatos": int(total),
        "cargos": [
            {
                "cargo": cargo,
                "total": quantidade,
            }
            for cargo, quantidade in cargos
        ],
        "fonte": "Tribunal Superior Eleitoral - TSE",
    }
