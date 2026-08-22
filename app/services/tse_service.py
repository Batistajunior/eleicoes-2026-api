from pathlib import Path
import io
import zipfile

import httpx
import pandas as pd
from fastapi import HTTPException


class TSEService:
    URL_CANDIDATOS = (
        "https://cdn.tse.jus.br/estatistica/sead/odsele/"
        "consulta_cand/consulta_cand_2026.zip"
    )

    DATA_DIR = Path("data")
    ZIP_PATH = DATA_DIR / "consulta_cand_2026.zip"

    def __init__(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

    async def baixar_candidatos(self, forcar=False):
        if self.ZIP_PATH.exists() and not forcar:
            return self.ZIP_PATH

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Referer": "https://dadosabertos.tse.jus.br/",
        }

        try:
            async with httpx.AsyncClient(
                headers=headers,
                follow_redirects=True,
                timeout=180.0,
            ) as client:
                response = await client.get(self.URL_CANDIDATOS)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail={
                        "erro": "Falha ao baixar dados do TSE",
                        "status_tse": response.status_code,
                        "url": self.URL_CANDIDATOS,
                    },
                )

            if len(response.content) < 1000:
                raise HTTPException(
                    status_code=502,
                    detail="O TSE retornou um arquivo inválido ou vazio.",
                )

            self.ZIP_PATH.write_bytes(response.content)

            return self.ZIP_PATH

        except HTTPException:
            raise

        except Exception as erro:
            raise HTTPException(
                status_code=502,
                detail=f"Erro de comunicação com o TSE: {erro}",
            )

    async def carregar_candidatos(self):
        zip_path = await self.baixar_candidatos()

        candidatos = []

        try:
            with zipfile.ZipFile(zip_path, "r") as arquivo_zip:
                arquivos_csv = [
                    nome
                    for nome in arquivo_zip.namelist()
                    if nome.lower().endswith(".csv")
                ]

                for nome_csv in arquivos_csv:
                    with arquivo_zip.open(nome_csv) as arquivo:
                        conteudo = arquivo.read()

                    df = pd.read_csv(
                        io.BytesIO(conteudo),
                        sep=";",
                        encoding="latin1",
                        dtype=str,
                        low_memory=False,
                    )

                    candidatos.append(df)

        except zipfile.BadZipFile:
            if self.ZIP_PATH.exists():
                self.ZIP_PATH.unlink()

            raise HTTPException(
                status_code=502,
                detail="O arquivo recebido do TSE não é um ZIP válido.",
            )

        if not candidatos:
            return pd.DataFrame()

        return pd.concat(
            candidatos,
            ignore_index=True,
        )


tse_service = TSEService()
