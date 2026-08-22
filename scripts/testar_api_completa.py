import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"

erros = []
avisos = []
sucessos = 0


def get(path, params=None):
    if params:
        path += "?" + urllib.parse.urlencode(params)

    url = BASE + path

    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            status = response.status
            body = response.read().decode("utf-8")

        if status != 200:
            raise RuntimeError(f"HTTP {status}")

        return json.loads(body)

    except Exception as e:
        raise RuntimeError(f"{url} -> {e}") from e


def ok(texto):
    global sucessos
    sucessos += 1
    print(f"✅ {texto}")


def erro(texto):
    erros.append(texto)
    print(f"❌ {texto}")


def aviso(texto):
    avisos.append(texto)
    print(f"⚠️  {texto}")


print()
print("=" * 70)
print("TESTE AUTOMÁTICO - ELEIÇÕES 2026 API")
print("=" * 70)

# ---------------------------------------------------------
# 1. HEALTH
# ---------------------------------------------------------

print("\n[1] HEALTH")

try:
    dados = get("/health")

    if dados.get("status") == "ok":
        ok("/health")
    else:
        erro(f"/health retornou: {dados}")

except Exception as e:
    erro(str(e))


# ---------------------------------------------------------
# 2. TOTAL DE CANDIDATOS
# ---------------------------------------------------------

print("\n[2] CANDIDATOS")

total_candidatos = 0

try:
    dados = get(
        "/candidatos",
        {
            "pagina": 1,
            "limite": 1,
        },
    )

    total_candidatos = int(dados.get("total", 0))

    if total_candidatos > 0:
        ok(f"{total_candidatos:,} candidatos encontrados")
    else:
        erro("Total de candidatos retornou zero")

except Exception as e:
    erro(str(e))


# ---------------------------------------------------------
# 3. UFs
# ---------------------------------------------------------

print("\n[3] TESTANDO UFs")

ufs = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF",
    "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
    "RO", "RR", "SC", "SP", "SE", "TO",
]

for uf in ufs:
    try:
        dados = get(
            "/candidatos",
            {
                "uf": uf,
                "pagina": 1,
                "limite": 1,
            },
        )

        total = int(dados.get("total", 0))

        if total > 0:
            ok(f"{uf}: {total} candidatos")
        else:
            aviso(f"{uf}: nenhum candidato")

    except Exception as e:
        erro(f"{uf}: {e}")


# ---------------------------------------------------------
# 4. CARGOS
# ---------------------------------------------------------

print("\n[4] TESTANDO CARGOS")

cargos = [
    ("PRESIDENTE", None),
    ("GOVERNADOR", "BA"),
    ("SENADOR", "BA"),
    ("DEPUTADO FEDERAL", "BA"),
    ("DEPUTADO ESTADUAL", "BA"),
    ("DEPUTADO DISTRITAL", "DF"),
]

for cargo, uf in cargos:
    try:
        params = {
            "cargo": cargo,
            "pagina": 1,
            "limite": 1,
        }

        if uf:
            params["uf"] = uf

        dados = get("/candidatos", params)

        total = int(dados.get("total", 0))

        descricao = cargo

        if uf:
            descricao += f" / {uf}"

        if total > 0:
            ok(f"{descricao}: {total}")
        else:
            erro(f"{descricao}: nenhum candidato")

    except Exception as e:
        erro(f"{cargo}: {e}")


# ---------------------------------------------------------
# 5. NIKOLAS - TESTE DE BUSCA
# ---------------------------------------------------------

print("\n[5] BUSCA POR NOME")

try:
    dados = get(
        "/candidatos",
        {
            "nome": "NIKOLAS",
            "pagina": 1,
            "limite": 100,
        },
    )

    candidatos = dados.get("candidatos", [])

    encontrado = any(
        "NIKOLAS" in (
            str(c.get("nome", "")) +
            " " +
            str(c.get("nome_urna", ""))
        ).upper()
        for c in candidatos
    )

    if encontrado:
        ok("Busca por NIKOLAS")
    else:
        erro("NIKOLAS não apareceu na busca")

except Exception as e:
    erro(f"Busca NIKOLAS: {e}")


# ---------------------------------------------------------
# 6. TESTE DE FICHAS
# ---------------------------------------------------------

print("\n[6] TESTANDO FICHAS DE CANDIDATOS")

amostras = []

for uf in ["BA", "MG", "SP", "RJ", "RS", "PE", "GO", "PA", "DF"]:
    try:
        dados = get(
            "/candidatos",
            {
                "uf": uf,
                "pagina": 1,
                "limite": 2,
            },
        )

        amostras.extend(dados.get("candidatos", []))

    except Exception as e:
        erro(f"Não foi possível obter amostra de {uf}: {e}")


# Presidente é nacional e pode ter UF especial no banco
try:
    dados = get(
        "/candidatos",
        {
            "cargo": "PRESIDENTE",
            "pagina": 1,
            "limite": 2,
        },
    )

    amostras.extend(dados.get("candidatos", []))

except Exception as e:
    erro(f"Não foi possível obter presidentes: {e}")


sq_testados = set()

for candidato in amostras:
    sq = str(candidato.get("sq_candidato", "")).strip()

    if not sq or sq in sq_testados:
        continue

    sq_testados.add(sq)

    nome = (
        candidato.get("nome_urna")
        or candidato.get("nome")
        or sq
    )

    try:
        ficha = get(
            f"/candidatos/sq/{urllib.parse.quote(sq)}/ficha"
        )

        if ficha:
            ok(f"Ficha: {nome}")
        else:
            erro(f"Ficha vazia: {nome}")

    except Exception as e:
        erro(f"Ficha {nome}: {e}")


# ---------------------------------------------------------
# 7. ESTATÍSTICAS
# ---------------------------------------------------------

print("\n[7] ESTATÍSTICAS")

endpoints_estatisticas = [
    "/estatisticas",
    "/estatisticas/estados",
    "/estatisticas/partidos",
    "/estatisticas/escolaridade",
    "/estatisticas/ocupacoes",
    "/estatisticas/genero",
    "/estatisticas/cor-raca",
    "/estatisticas/patrimonio",
    "/estatisticas/situacoes",
]

for endpoint in endpoints_estatisticas:
    try:
        dados = get(endpoint)

        if isinstance(dados, dict) and dados:
            ok(endpoint)
        else:
            erro(f"{endpoint}: resposta vazia")

    except Exception as e:
        erro(f"{endpoint}: {e}")


# ---------------------------------------------------------
# 8. ESTADOS
# ---------------------------------------------------------

print("\n[8] ROTAS DE ESTADOS")

try:
    dados = get("/estados")

    if dados:
        ok("/estados")
    else:
        aviso("/estados retornou vazio")

except Exception as e:
    erro(f"/estados: {e}")


for uf in ["BA", "MG", "SP", "RJ", "DF"]:
    try:
        dados = get(f"/estados/{uf}")

        if dados:
            ok(f"/estados/{uf}")
        else:
            aviso(f"/estados/{uf} vazio")

    except Exception as e:
        erro(f"/estados/{uf}: {e}")


# ---------------------------------------------------------
# 9. RESULTADOS
# ---------------------------------------------------------

print("\n[9] RESULTADOS / APURAÇÃO")

try:
    status = get("/resultados/status")

    ok("/resultados/status")

    print(
        "   Status recebido:",
        json.dumps(
            status,
            ensure_ascii=False,
        ),
    )

except Exception as e:
    erro(f"/resultados/status: {e}")


for turno in [1, 2]:
    try:
        dados = get(
            "/resultados/brasil",
            {
                "turno": turno,
            },
        )

        ok(f"/resultados/brasil?turno={turno}")

    except Exception as e:
        erro(f"Resultado Brasil turno {turno}: {e}")


# ---------------------------------------------------------
# 10. CONSISTÊNCIA DO TOTAL
# ---------------------------------------------------------

print("\n[10] CONSISTÊNCIA")

try:
    estatisticas = get("/estatisticas")

    total_estatisticas = int(
        estatisticas.get("total_candidatos", 0)
    )

    if total_estatisticas == total_candidatos:
        ok(
            "Total /candidatos == /estatisticas "
            f"({total_candidatos})"
        )
    else:
        erro(
            "Totais divergentes: "
            f"/candidatos={total_candidatos} "
            f"/estatisticas={total_estatisticas}"
        )

except Exception as e:
    erro(f"Consistência: {e}")


# ---------------------------------------------------------
# RESUMO
# ---------------------------------------------------------

print()
print("=" * 70)
print("RESUMO")
print("=" * 70)

print(f"Sucessos : {sucessos}")
print(f"Avisos   : {len(avisos)}")
print(f"Erros    : {len(erros)}")

if avisos:
    print("\nAVISOS:")

    for item in avisos:
        print(f" - {item}")

if erros:
    print("\nERROS:")

    for item in erros:
        print(f" - {item}")

    print()
    print("RESULTADO: API AINDA PRECISA DE AJUSTES")
    sys.exit(1)

print()
print("RESULTADO: TODOS OS TESTES PRINCIPAIS PASSARAM")
sys.exit(0)
