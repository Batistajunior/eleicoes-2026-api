from pathlib import Path
import sys

import pandas as pd
from sqlalchemy.exc import IntegrityError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database.database import Base, SessionLocal, engine
from app.models.candidato import Candidato


PASTA_PADRAO = Path.home() / "Downloads" / "consulta_cand_2026"


def localizar_csvs(pasta):
    arquivos = list(pasta.rglob("*.csv"))
    arquivos += list(pasta.rglob("*.CSV"))

    return sorted(set(arquivos))


def ler_csv(caminho):
    encodings = [
        "latin1",
        "cp1252",
        "utf-8-sig",
        "utf-8",
    ]

    ultimo_erro = None

    for encoding in encodings:
        try:
            return pd.read_csv(
                caminho,
                sep=";",
                encoding=encoding,
                dtype=str,
                low_memory=False,
            )
        except UnicodeDecodeError as erro:
            ultimo_erro = erro

    raise ultimo_erro


def valor(linha, coluna):
    dado = linha.get(coluna)

    if pd.isna(dado):
        return None

    dado = str(dado).strip()

    if not dado:
        return None

    return dado


def importar(pasta):
    if not pasta.exists():
        print(f"ERRO: pasta não encontrada: {pasta}")
        sys.exit(1)

    arquivos = localizar_csvs(pasta)

    if not arquivos:
        print(f"ERRO: nenhum CSV encontrado em {pasta}")
        sys.exit(1)

    print()
    print("ELEIÇÕES 2026")
    print("=" * 60)
    print(f"Pasta: {pasta}")
    print(f"Arquivos encontrados: {len(arquivos)}")
    print()

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    total_lidos = 0
    total_inseridos = 0
    total_atualizados = 0
    total_erros = 0

    try:
        for numero_arquivo, arquivo in enumerate(arquivos, 1):
            print(
                f"[{numero_arquivo}/{len(arquivos)}] "
                f"{arquivo.name}"
            )

            try:
                df = ler_csv(arquivo)
            except Exception as erro:
                print(f"  ERRO ao ler arquivo: {erro}")
                total_erros += 1
                continue

            total_lidos += len(df)

            print(f"  Registros: {len(df)}")

            for _, linha in df.iterrows():
                sq_candidato = valor(
                    linha,
                    "SQ_CANDIDATO",
                )

                if not sq_candidato:
                    continue

                existente = (
                    db.query(Candidato)
                    .filter(
                        Candidato.sq_candidato
                        == sq_candidato
                    )
                    .first()
                )

                dados = {
                    "uf": valor(linha, "SG_UF"),
                    "cargo": valor(
                        linha,
                        "DS_CARGO",
                    ),
                    "numero": valor(
                        linha,
                        "NR_CANDIDATO",
                    ),
                    "nome": valor(
                        linha,
                        "NM_CANDIDATO",
                    ),
                    "nome_urna": valor(
                        linha,
                        "NM_URNA_CANDIDATO",
                    ),
                    "numero_partido": valor(
                        linha,
                        "NR_PARTIDO",
                    ),
                    "sigla_partido": valor(
                        linha,
                        "SG_PARTIDO",
                    ),
                    "nome_partido": valor(
                        linha,
                        "NM_PARTIDO",
                    ),
                    "situacao": valor(
                        linha,
                        "DS_SITUACAO_CANDIDATURA",
                    ),
                }

                if existente:
                    for campo, dado in dados.items():
                        setattr(
                            existente,
                            campo,
                            dado,
                        )

                    total_atualizados += 1

                else:
                    candidato = Candidato(
                        sq_candidato=sq_candidato,
                        **dados,
                    )

                    db.add(candidato)
                    total_inseridos += 1

                if (
                    total_inseridos
                    + total_atualizados
                ) % 500 == 0:
                    try:
                        db.commit()
                    except IntegrityError:
                        db.rollback()
                        total_erros += 1

            db.commit()

    finally:
        db.close()

    print()
    print("=" * 60)
    print("IMPORTAÇÃO CONCLUÍDA")
    print()
    print(f"Registros lidos:      {total_lidos}")
    print(f"Inseridos:            {total_inseridos}")
    print(f"Atualizados:          {total_atualizados}")
    print(f"Erros:                {total_erros}")
    print()


if __name__ == "__main__":
    pasta = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else PASTA_PADRAO
    )

    importar(pasta)
