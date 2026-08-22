from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidato import Candidato


router = APIRouter(
    prefix="/candidatos",
    tags=["Candidatos"],
)


@router.get("")
def listar_candidatos(
    uf: Optional[str] = Query(default=None),
    cargo: Optional[str] = Query(default=None),
    partido: Optional[str] = Query(default=None),
    nome: Optional[str] = Query(default=None),
    limite: int = Query(default=100, ge=1, le=1000),
    pagina: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    query = db.query(Candidato)

    if uf:
        query = query.filter(
            Candidato.uf == uf.upper()
        )

    if cargo:
        query = query.filter(
            Candidato.cargo == cargo.upper()
        )

    if partido:
        query = query.filter(
            Candidato.sigla_partido.ilike(
                f"%{partido}%"
            )
        )

    if nome:
        termo = nome.strip()

        query = query.filter(
            or_(
                Candidato.nome.ilike(f"%{termo}%"),
                Candidato.nome_urna.ilike(f"%{termo}%"),
                Candidato.numero.ilike(f"%{termo}%"),
                Candidato.sigla_partido.ilike(f"%{termo}%"),
                Candidato.nome_partido.ilike(f"%{termo}%"),
            )
        )

    total = query.count()

    offset = (pagina - 1) * limite

    candidatos = (
        query
        .order_by(Candidato.nome_urna)
        .offset(offset)
        .limit(limite)
        .all()
    )

    return {
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "candidatos": [
            {
                "id": candidato.id,
                "sq_candidato": candidato.sq_candidato,
                "uf": candidato.uf,
                "cargo": candidato.cargo,
                "numero": candidato.numero,
                "nome": candidato.nome,
                "nome_urna": candidato.nome_urna,
                "numero_partido": candidato.numero_partido,
                "sigla_partido": candidato.sigla_partido,
                "nome_partido": candidato.nome_partido,
                "situacao": candidato.situacao,
                "foto_url": candidato.foto_url,
            }
            for candidato in candidatos
        ],
    }


@router.get("/{candidato_id}")
def obter_candidato(
    candidato_id: int,
    db: Session = Depends(get_db),
):
    candidato = (
        db.query(Candidato)
        .filter(Candidato.id == candidato_id)
        .first()
    )

    if not candidato:
        return {
            "erro": "Candidato não encontrado"
        }

    return {
        "id": candidato.id,
        "sq_candidato": candidato.sq_candidato,
        "uf": candidato.uf,
        "cargo": candidato.cargo,
        "numero": candidato.numero,
        "nome": candidato.nome,
        "nome_urna": candidato.nome_urna,
        "numero_partido": candidato.numero_partido,
        "sigla_partido": candidato.sigla_partido,
        "nome_partido": candidato.nome_partido,
        "situacao": candidato.situacao,
        "foto_url": candidato.foto_url,
    }


@router.get("/sq/{sq_candidato}/ficha")
def obter_ficha_candidato(
    sq_candidato: str,
    db: Session = Depends(get_db),
):
    from sqlalchemy import func

    from app.models.candidato_detalhes import (
        BemCandidato,
        CandidatoDetalhes,
        RedeSocialCandidato,
    )

    candidato = (
        db.query(Candidato)
        .filter(
            Candidato.sq_candidato == sq_candidato
        )
        .first()
    )

    if not candidato:
        return {
            "erro": "Candidato não encontrado"
        }

    detalhes = (
        db.query(CandidatoDetalhes)
        .filter(
            CandidatoDetalhes.sq_candidato
            == sq_candidato
        )
        .first()
    )

    bens = (
        db.query(BemCandidato)
        .filter(
            BemCandidato.sq_candidato
            == sq_candidato
        )
        .order_by(BemCandidato.id)
        .all()
    )

    redes = (
        db.query(RedeSocialCandidato)
        .filter(
            RedeSocialCandidato.sq_candidato
            == sq_candidato
        )
        .order_by(RedeSocialCandidato.id)
        .all()
    )

    patrimonio_total = (
        db.query(
            func.coalesce(
                func.sum(BemCandidato.valor),
                0,
            )
        )
        .filter(
            BemCandidato.sq_candidato
            == sq_candidato
        )
        .scalar()
    )

    def plataforma(url):
        if not url:
            return "Site"

        u = url.lower()

        if "instagram.com" in u:
            return "Instagram"

        if "facebook.com" in u or "fb.com" in u:
            return "Facebook"

        if "twitter.com" in u or "x.com" in u:
            return "X / Twitter"

        if "youtube.com" in u or "youtu.be" in u:
            return "YouTube"

        if "tiktok.com" in u:
            return "TikTok"

        if "threads.net" in u:
            return "Threads"

        if "linkedin.com" in u:
            return "LinkedIn"

        if "whatsapp" in u or "wa.me" in u:
            return "WhatsApp"

        if "telegram" in u or "t.me" in u:
            return "Telegram"

        return "Site"

    perfil = None
    candidatura = None

    if detalhes:
        perfil = {
            "nome_social":
                detalhes.nome_social,

            "data_nascimento":
                detalhes.data_nascimento,

            "idade_data_posse":
                detalhes.idade_data_posse,

            "municipio_nascimento":
                detalhes.municipio_nascimento,

            "uf_nascimento":
                detalhes.uf_nascimento,

            "nacionalidade":
                detalhes.nacionalidade,

            "genero":
                detalhes.genero,

            "cor_raca":
                detalhes.cor_raca,

            "estado_civil":
                detalhes.estado_civil,

            "escolaridade":
                detalhes.grau_instrucao,

            "ocupacao":
                detalhes.ocupacao,

            "quilombola":
                detalhes.quilombola,

            "etnia_indigena":
                detalhes.etnia_indigena,
        }

        candidatura = {
            "detalhe_situacao":
                detalhes.detalhe_situacao,

            "reeleicao":
                detalhes.reeleicao,

            "declarou_bens":
                detalhes.declarou_bens,

            "protocolo":
                detalhes.protocolo_candidatura,

            "numero_processo":
                detalhes.numero_processo,

            "situacao_pleito":
                detalhes.situacao_pleito,

            "situacao_urna":
                detalhes.situacao_urna,

            "inserido_urna":
                detalhes.inserido_urna,

            "destinacao_votos":
                detalhes.destinacao_votos,

            "situacao_total":
                detalhes.situacao_total,

            "situacao_total_turno":
                detalhes.situacao_total_turno,

            "prestacao_contas":
                detalhes.prestacao_contas,

            "substituido":
                detalhes.substituido,

            "data_aceite":
                detalhes.data_aceite_candidatura,

            "situacao_julgamento":
                detalhes.situacao_julgamento,

            "situacao_julgamento_pleito":
                detalhes.situacao_julgamento_pleito,

            "situacao_julgamento_urna":
                detalhes.situacao_julgamento_urna,

            "situacao_cassacao":
                detalhes.situacao_cassacao,

            "situacao_cassacao_midia":
                detalhes.situacao_cassacao_midia,

            "situacao_diploma":
                detalhes.situacao_diploma,

            "limite_despesa_campanha":
                detalhes.despesa_max_campanha,
        }

    return {
        "candidato": {
            "id":
                candidato.id,

            "sq_candidato":
                candidato.sq_candidato,

            "nome":
                candidato.nome,

            "nome_urna":
                candidato.nome_urna,

            "numero":
                candidato.numero,

            "cargo":
                candidato.cargo,

            "uf":
                candidato.uf,

            "situacao":
                candidato.situacao,

            "foto_url":
                candidato.foto_url,

            "partido": {
                "numero":
                    candidato.numero_partido,

                "sigla":
                    candidato.sigla_partido,

                "nome":
                    candidato.nome_partido,
            },

            "federacao": {
                "numero":
                    detalhes.federacao_numero
                    if detalhes else None,

                "sigla":
                    detalhes.federacao_sigla
                    if detalhes else None,

                "nome":
                    detalhes.federacao_nome
                    if detalhes else None,

                "composicao":
                    detalhes.federacao_composicao
                    if detalhes else None,
            },

            "coligacao": {
                "nome":
                    detalhes.coligacao_nome
                    if detalhes else None,

                "composicao":
                    detalhes.coligacao_composicao
                    if detalhes else None,
            },
        },

        "perfil": perfil,

        "candidatura": candidatura,

        "patrimonio": {
            "declarou_bens":
                detalhes.declarou_bens
                if detalhes else None,

            "quantidade_bens":
                len(bens),

            "total_declarado":
                float(patrimonio_total or 0),

            "bens": [
                {
                    "ordem":
                        bem.ordem,

                    "codigo_tipo":
                        bem.codigo_tipo,

                    "tipo":
                        bem.tipo,

                    "descricao":
                        bem.descricao,

                    "valor":
                        bem.valor,

                    "data_atualizacao":
                        bem.data_atualizacao,
                }
                for bem in bens
            ],
        },

        "redes_sociais": [
            {
                "plataforma":
                    plataforma(rede.url),

                "url":
                    rede.url,
            }
            for rede in redes
        ],

        "fontes": {
            "dados_candidato":
                "Tribunal Superior Eleitoral - TSE",

            "dados_complementares":
                "Tribunal Superior Eleitoral - TSE",

            "patrimonio":
                "Bens declarados pelo candidato à Justiça Eleitoral",

            "redes_sociais":
                "Redes sociais declaradas à Justiça Eleitoral",
        },
    }
