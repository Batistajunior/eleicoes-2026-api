from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidato import Candidato
from app.models.candidato_detalhes import CandidatoDetalhes, BemCandidato


router = APIRouter(
    prefix="/estatisticas",
    tags=["Estatísticas"],
)


def _texto(valor):
    if valor is None or str(valor).strip() == "":
        return "Não informado"
    return str(valor).strip()


def _distribuicao_detalhes(db: Session, coluna):
    linhas = (
        db.query(
            coluna,
            func.count(CandidatoDetalhes.id).label("total"),
        )
        .group_by(coluna)
        .order_by(func.count(CandidatoDetalhes.id).desc())
        .all()
    )

    total_geral = sum(int(qtd or 0) for _, qtd in linhas)

    return [
        {
            "nome": _texto(valor),
            "total": int(qtd or 0),
            "percentual": round(
                (int(qtd or 0) / total_geral * 100)
                if total_geral
                else 0,
                2,
            ),
        }
        for valor, qtd in linhas
    ]


@router.get("")
def estatisticas_gerais(db: Session = Depends(get_db)):
    total = db.query(func.count(Candidato.id)).scalar() or 0

    por_cargo = (
        db.query(
            Candidato.cargo,
            func.count(Candidato.id),
        )
        .group_by(Candidato.cargo)
        .order_by(func.count(Candidato.id).desc())
        .all()
    )

    por_uf = (
        db.query(
            Candidato.uf,
            func.count(Candidato.id),
        )
        .group_by(Candidato.uf)
        .order_by(func.count(Candidato.id).desc())
        .all()
    )

    por_partido = (
        db.query(
            Candidato.sigla_partido,
            func.count(Candidato.id),
        )
        .group_by(Candidato.sigla_partido)
        .order_by(func.count(Candidato.id).desc())
        .all()
    )

    return {
        "ano": 2026,
        "total_candidatos": int(total),
        "por_cargo": [
            {
                "cargo": _texto(cargo),
                "total": int(quantidade),
            }
            for cargo, quantidade in por_cargo
        ],
        "por_uf": [
            {
                "uf": _texto(uf),
                "total": int(quantidade),
            }
            for uf, quantidade in por_uf
        ],
        "por_partido": [
            {
                "partido": _texto(partido),
                "total": int(quantidade),
            }
            for partido, quantidade in por_partido
        ],
        "fonte": "Tribunal Superior Eleitoral - TSE",
    }


@router.get("/estados")
def candidatos_por_estado(db: Session = Depends(get_db)):
    linhas = (
        db.query(
            Candidato.uf,
            func.count(Candidato.id).label("total"),
        )
        .group_by(Candidato.uf)
        .order_by(func.count(Candidato.id).desc())
        .all()
    )

    total_geral = sum(int(qtd or 0) for _, qtd in linhas)

    return {
        "titulo": "Candidatos por estado",
        "total": total_geral,
        "dados": [
            {
                "nome": _texto(uf),
                "total": int(qtd or 0),
                "percentual": round(
                    (int(qtd or 0) / total_geral * 100)
                    if total_geral
                    else 0,
                    2,
                ),
            }
            for uf, qtd in linhas
        ],
    }


@router.get("/partidos")
def candidatos_por_partido(db: Session = Depends(get_db)):
    linhas = (
        db.query(
            Candidato.sigla_partido,
            func.count(Candidato.id).label("total"),
        )
        .group_by(Candidato.sigla_partido)
        .order_by(func.count(Candidato.id).desc())
        .all()
    )

    total_geral = sum(int(qtd or 0) for _, qtd in linhas)

    return {
        "titulo": "Candidatos por partido",
        "total": total_geral,
        "dados": [
            {
                "nome": _texto(partido),
                "total": int(qtd or 0),
                "percentual": round(
                    (int(qtd or 0) / total_geral * 100)
                    if total_geral
                    else 0,
                    2,
                ),
            }
            for partido, qtd in linhas
        ],
    }


@router.get("/escolaridade")
def escolaridade(db: Session = Depends(get_db)):
    return {
        "titulo": "Escolaridade",
        "dados": _distribuicao_detalhes(
            db,
            CandidatoDetalhes.grau_instrucao,
        ),
    }


@router.get("/ocupacoes")
def ocupacoes(db: Session = Depends(get_db)):
    return {
        "titulo": "Ocupações",
        "dados": _distribuicao_detalhes(
            db,
            CandidatoDetalhes.ocupacao,
        ),
    }


@router.get("/genero")
def genero(db: Session = Depends(get_db)):
    return {
        "titulo": "Gênero",
        "dados": _distribuicao_detalhes(
            db,
            CandidatoDetalhes.genero,
        ),
    }


@router.get("/cor-raca")
def cor_raca(db: Session = Depends(get_db)):
    return {
        "titulo": "Cor/Raça",
        "dados": _distribuicao_detalhes(
            db,
            CandidatoDetalhes.cor_raca,
        ),
    }


@router.get("/situacoes")
def situacoes(db: Session = Depends(get_db)):
    return {
        "titulo": "Situação das candidaturas",
        "dados": _distribuicao_detalhes(
            db,
            CandidatoDetalhes.situacao_julgamento,
        ),
    }


@router.get("/patrimonio")
def patrimonio(db: Session = Depends(get_db)):
    total = (
        db.query(func.coalesce(func.sum(BemCandidato.valor), 0.0))
        .scalar()
        or 0.0
    )

    candidatos_com_bens = (
        db.query(func.count(func.distinct(BemCandidato.sq_candidato)))
        .scalar()
        or 0
    )

    quantidade_bens = (
        db.query(func.count(BemCandidato.id))
        .scalar()
        or 0
    )

    ranking = (
        db.query(
            Candidato.sq_candidato,
            Candidato.nome_urna,
            Candidato.nome,
            Candidato.uf,
            Candidato.cargo,
            Candidato.sigla_partido,
            func.sum(BemCandidato.valor).label("patrimonio"),
        )
        .join(
            BemCandidato,
            BemCandidato.sq_candidato == Candidato.sq_candidato,
        )
        .group_by(
            Candidato.sq_candidato,
            Candidato.nome_urna,
            Candidato.nome,
            Candidato.uf,
            Candidato.cargo,
            Candidato.sigla_partido,
        )
        .order_by(func.sum(BemCandidato.valor).desc())
        .limit(100)
        .all()
    )

    media = (
        float(total) / int(candidatos_com_bens)
        if candidatos_com_bens
        else 0.0
    )

    return {
        "titulo": "Patrimônio declarado",
        "patrimonio_total": float(total),
        "media_por_candidato": media,
        "candidatos_com_bens": int(candidatos_com_bens),
        "quantidade_bens": int(quantidade_bens),
        "ranking": [
            {
                "sq_candidato": sq,
                "nome": _texto(nome_urna)
                if _texto(nome_urna) != "Não informado"
                else _texto(nome),
                "uf": _texto(uf),
                "cargo": _texto(cargo),
                "partido": _texto(partido),
                "valor": float(valor or 0),
            }
            for (
                sq,
                nome_urna,
                nome,
                uf,
                cargo,
                partido,
                valor,
            ) in ranking
        ],
    }


@router.get("/uf/{uf}")
def estatisticas_uf(
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
        .order_by(func.count(Candidato.id).desc())
        .all()
    )

    partidos = (
        db.query(
            Candidato.sigla_partido,
            func.count(Candidato.id),
        )
        .filter(Candidato.uf == uf)
        .group_by(Candidato.sigla_partido)
        .order_by(func.count(Candidato.id).desc())
        .all()
    )

    return {
        "ano": 2026,
        "uf": uf,
        "total_candidatos": int(total),
        "por_cargo": [
            {
                "cargo": _texto(cargo),
                "total": int(quantidade),
            }
            for cargo, quantidade in cargos
        ],
        "por_partido": [
            {
                "partido": _texto(partido),
                "total": int(quantidade),
            }
            for partido, quantidade in partidos
        ],
        "fonte": "Tribunal Superior Eleitoral - TSE",
    }
