from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database.database import Base, SessionLocal, engine
from app.models.candidato_detalhes import (
    BemCandidato,
    CandidatoDetalhes,
    RedeSocialCandidato,
)


DOWNLOADS = Path.home() / "Downloads"


def texto(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if not valor or valor in {"#NULO", "#NE", "-1", "-3"}:
        return None

    return valor


def inteiro(valor):
    v = texto(valor)

    if v is None:
        return None

    try:
        return int(float(v.replace(",", ".")))
    except (ValueError, TypeError):
        return None


def dinheiro(valor):
    v = texto(valor)

    if v is None:
        return None

    try:
        # CSV brasileiro normalmente usa vírgula decimal.
        return float(
            v.replace(".", "").replace(",", ".")
        )
    except (ValueError, TypeError):
        return None


def arquivos_csv(nome_pasta):
    pasta = DOWNLOADS / nome_pasta

    return sorted(
        list(pasta.glob("*.csv"))
        + list(pasta.glob("*.CSV"))
    )


def ler(arquivo):
    for encoding in ["latin1", "cp1252", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(
                arquivo,
                sep=";",
                encoding=encoding,
                dtype=str,
                low_memory=False,
            )
        except UnicodeDecodeError:
            continue

    raise RuntimeError(
        f"Não foi possível ler {arquivo}"
    )


def importar_consulta_principal(db):
    print("\n1/4 CONSULTA PRINCIPAL")

    arquivos = arquivos_csv("consulta_cand_2026")

    for n, arquivo in enumerate(arquivos, 1):
        print(f"[{n}/{len(arquivos)}] {arquivo.name}")

        df = ler(arquivo)

        for _, r in df.iterrows():
            sq = texto(r.get("SQ_CANDIDATO"))

            if not sq:
                continue

            obj = (
                db.query(CandidatoDetalhes)
                .filter(
                    CandidatoDetalhes.sq_candidato == sq
                )
                .first()
            )

            if obj is None:
                obj = CandidatoDetalhes(
                    sq_candidato=sq
                )
                db.add(obj)

            obj.nome_social = texto(
                r.get("NM_SOCIAL_CANDIDATO")
            )
            obj.email = texto(r.get("DS_EMAIL"))

            obj.federacao_numero = texto(
                r.get("NR_FEDERACAO")
            )
            obj.federacao_nome = texto(
                r.get("NM_FEDERACAO")
            )
            obj.federacao_sigla = texto(
                r.get("SG_FEDERACAO")
            )
            obj.federacao_composicao = texto(
                r.get("DS_COMPOSICAO_FEDERACAO")
            )

            obj.coligacao_nome = texto(
                r.get("NM_COLIGACAO")
            )
            obj.coligacao_composicao = texto(
                r.get("DS_COMPOSICAO_COLIGACAO")
            )

            obj.uf_nascimento = texto(
                r.get("SG_UF_NASCIMENTO")
            )
            obj.data_nascimento = texto(
                r.get("DT_NASCIMENTO")
            )

            obj.genero = texto(r.get("DS_GENERO"))
            obj.grau_instrucao = texto(
                r.get("DS_GRAU_INSTRUCAO")
            )
            obj.estado_civil = texto(
                r.get("DS_ESTADO_CIVIL")
            )
            obj.cor_raca = texto(
                r.get("DS_COR_RACA")
            )
            obj.ocupacao = texto(
                r.get("DS_OCUPACAO")
            )

            obj.situacao_total_turno = texto(
                r.get("DS_SIT_TOT_TURNO")
            )

        db.commit()


def importar_complementar(db):
    print("\n2/4 COMPLEMENTAR")

    arquivos = arquivos_csv(
        "consulta_cand_complementar_2026"
    )

    for n, arquivo in enumerate(arquivos, 1):
        print(f"[{n}/{len(arquivos)}] {arquivo.name}")

        df = ler(arquivo)

        for _, r in df.iterrows():
            sq = texto(r.get("SQ_CANDIDATO"))

            if not sq:
                continue

            obj = (
                db.query(CandidatoDetalhes)
                .filter(
                    CandidatoDetalhes.sq_candidato == sq
                )
                .first()
            )

            if obj is None:
                obj = CandidatoDetalhes(
                    sq_candidato=sq
                )
                db.add(obj)

            obj.detalhe_situacao = texto(
                r.get("DS_DETALHE_SITUACAO_CAND")
            )
            obj.nacionalidade = texto(
                r.get("DS_NACIONALIDADE")
            )
            obj.municipio_nascimento = texto(
                r.get("NM_MUNICIPIO_NASCIMENTO")
            )
            obj.idade_data_posse = inteiro(
                r.get("NR_IDADE_DATA_POSSE")
            )

            obj.quilombola = texto(
                r.get("ST_QUILOMBOLA")
            )
            obj.etnia_indigena = texto(
                r.get("DS_ETNIA_INDIGENA")
            )

            obj.despesa_max_campanha = dinheiro(
                r.get("VR_DESPESA_MAX_CAMPANHA")
            )

            obj.reeleicao = texto(
                r.get("ST_REELEICAO")
            )
            obj.declarou_bens = texto(
                r.get("ST_DECLARAR_BENS")
            )

            obj.protocolo_candidatura = texto(
                r.get("NR_PROTOCOLO_CANDIDATURA")
            )
            obj.numero_processo = texto(
                r.get("NR_PROCESSO")
            )

            obj.situacao_pleito = texto(
                r.get("DS_SITUACAO_CANDIDATO_PLEITO")
            )
            obj.situacao_urna = texto(
                r.get("DS_SITUACAO_CANDIDATO_URNA")
            )
            obj.inserido_urna = texto(
                r.get("ST_CANDIDATO_INSERIDO_URNA")
            )

            obj.destinacao_votos = texto(
                r.get("NM_TIPO_DESTINACAO_VOTOS")
            )
            obj.situacao_total = texto(
                r.get("DS_SITUACAO_CANDIDATO_TOT")
            )

            obj.prestacao_contas = texto(
                r.get("ST_PREST_CONTAS")
            )
            obj.substituido = texto(
                r.get("ST_SUBSTITUIDO")
            )

            obj.data_aceite_candidatura = texto(
                r.get("DT_ACEITE_CANDIDATURA")
            )

            obj.situacao_julgamento = texto(
                r.get("DS_SITUACAO_JULGAMENTO")
            )
            obj.situacao_julgamento_pleito = texto(
                r.get(
                    "DS_SITUACAO_JULGAMENTO_PLEITO"
                )
            )
            obj.situacao_julgamento_urna = texto(
                r.get(
                    "DS_SITUACAO_JULGAMENTO_URNA"
                )
            )

            obj.situacao_cassacao = texto(
                r.get("DS_SITUACAO_CASSACAO")
            )
            obj.situacao_cassacao_midia = texto(
                r.get("DS_SITUACAO_CASSACAO_MIDIA")
            )

            obj.situacao_diploma = texto(
                r.get("DS_SITUACAO_DIPLOMA")
            )

        db.commit()


def importar_bens(db):
    print("\n3/4 BENS")

    db.query(BemCandidato).delete()
    db.commit()

    arquivos = arquivos_csv("bem_candidato_2026")

    total_lidos = 0
    total_importados = 0
    total_duplicados = 0

    vistos = set()

    for n, arquivo in enumerate(arquivos, 1):
        print(f"[{n}/{len(arquivos)}] {arquivo.name}")

        df = ler(arquivo)
        objetos = []

        for _, r in df.iterrows():
            sq = texto(r.get("SQ_CANDIDATO"))

            if not sq:
                continue

            total_lidos += 1

            ordem = texto(
                r.get("NR_ORDEM_BEM_CANDIDATO")
            )
            codigo_tipo = texto(
                r.get("CD_TIPO_BEM_CANDIDATO")
            )
            tipo = texto(
                r.get("DS_TIPO_BEM_CANDIDATO")
            )
            descricao = texto(
                r.get("DS_BEM_CANDIDATO")
            )
            valor = dinheiro(
                r.get("VR_BEM_CANDIDATO")
            )

            chave = (
                sq,
                ordem,
                codigo_tipo,
                descricao,
                valor,
            )

            if chave in vistos:
                total_duplicados += 1
                continue

            vistos.add(chave)

            objetos.append(
                BemCandidato(
                    sq_candidato=sq,
                    ordem=ordem,
                    codigo_tipo=codigo_tipo,
                    tipo=tipo,
                    descricao=descricao,
                    valor=valor,
                    data_atualizacao=texto(
                        r.get(
                            "DT_ULT_ATUAL_BEM_CANDIDATO"
                        )
                    ),
                )
            )

        if objetos:
            db.bulk_save_objects(objetos)
            db.commit()

        total_importados += len(objetos)

    print("Bens lidos:", total_lidos)
    print("Duplicados ignorados:", total_duplicados)
    print("Bens importados:", total_importados)

def importar_redes(db):
    print("\n4/4 REDES SOCIAIS")

    db.query(RedeSocialCandidato).delete()
    db.commit()

    arquivos = arquivos_csv(
        "rede_social_candidato_2026"
    )

    total_lidos = 0
    total_importados = 0
    total_duplicados = 0

    vistos = set()

    for n, arquivo in enumerate(arquivos, 1):
        print(f"[{n}/{len(arquivos)}] {arquivo.name}")

        df = ler(arquivo)
        objetos = []

        for _, r in df.iterrows():
            sq = texto(r.get("SQ_CANDIDATO"))
            url = texto(r.get("DS_URL"))

            if not sq or not url:
                continue

            total_lidos += 1

            # Normalização mínima para comparação.
            url_normalizada = url.strip().rstrip("/")

            chave = (
                sq,
                url_normalizada.lower(),
            )

            if chave in vistos:
                total_duplicados += 1
                continue

            vistos.add(chave)

            objetos.append(
                RedeSocialCandidato(
                    sq_candidato=sq,
                    ordem=texto(
                        r.get(
                            "NR_ORDEM_REDE_SOCIAL"
                        )
                    ),
                    url=url,
                )
            )

        if objetos:
            db.bulk_save_objects(objetos)
            db.commit()

        total_importados += len(objetos)

    print("Redes lidas:", total_lidos)
    print("Duplicadas ignoradas:", total_duplicados)
    print("Redes importadas:", total_importados)

def main():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        importar_consulta_principal(db)
        importar_complementar(db)
        importar_bens(db)
        importar_redes(db)

        print("\n" + "=" * 60)
        print("IMPORTAÇÃO CONCLUÍDA")
        print("=" * 60)

        print(
            "Detalhes:",
            db.query(CandidatoDetalhes).count(),
        )
        print(
            "Bens:",
            db.query(BemCandidato).count(),
        )
        print(
            "Redes:",
            db.query(RedeSocialCandidato).count(),
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
