from sqlalchemy import Column, Float, Integer, String, Text

from app.database.database import Base


class CandidatoDetalhes(Base):
    __tablename__ = "candidato_detalhes"

    id = Column(Integer, primary_key=True, index=True)
    sq_candidato = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    nome_social = Column(String, nullable=True)
    email = Column(String, nullable=True)

    federacao_numero = Column(String, nullable=True)
    federacao_nome = Column(String, nullable=True)
    federacao_sigla = Column(String, nullable=True)
    federacao_composicao = Column(Text, nullable=True)

    coligacao_nome = Column(String, nullable=True)
    coligacao_composicao = Column(Text, nullable=True)

    uf_nascimento = Column(String, nullable=True)
    data_nascimento = Column(String, nullable=True)

    genero = Column(String, nullable=True)
    grau_instrucao = Column(String, nullable=True)
    estado_civil = Column(String, nullable=True)
    cor_raca = Column(String, nullable=True)
    ocupacao = Column(String, nullable=True)

    situacao_total_turno = Column(String, nullable=True)

    detalhe_situacao = Column(String, nullable=True)
    nacionalidade = Column(String, nullable=True)
    municipio_nascimento = Column(String, nullable=True)
    idade_data_posse = Column(Integer, nullable=True)

    quilombola = Column(String, nullable=True)
    etnia_indigena = Column(String, nullable=True)

    despesa_max_campanha = Column(Float, nullable=True)

    reeleicao = Column(String, nullable=True)
    declarou_bens = Column(String, nullable=True)

    protocolo_candidatura = Column(String, nullable=True)
    numero_processo = Column(String, nullable=True)

    situacao_pleito = Column(String, nullable=True)
    situacao_urna = Column(String, nullable=True)
    inserido_urna = Column(String, nullable=True)

    destinacao_votos = Column(String, nullable=True)
    situacao_total = Column(String, nullable=True)

    prestacao_contas = Column(String, nullable=True)
    substituido = Column(String, nullable=True)

    data_aceite_candidatura = Column(String, nullable=True)

    situacao_julgamento = Column(String, nullable=True)
    situacao_julgamento_pleito = Column(String, nullable=True)
    situacao_julgamento_urna = Column(String, nullable=True)

    situacao_cassacao = Column(String, nullable=True)
    situacao_cassacao_midia = Column(String, nullable=True)

    situacao_diploma = Column(String, nullable=True)


class BemCandidato(Base):
    __tablename__ = "bens_candidato"

    id = Column(Integer, primary_key=True, index=True)

    sq_candidato = Column(
        String,
        nullable=False,
        index=True,
    )

    ordem = Column(String, nullable=True)
    codigo_tipo = Column(String, nullable=True)
    tipo = Column(String, nullable=True)
    descricao = Column(Text, nullable=True)
    valor = Column(Float, nullable=True)
    data_atualizacao = Column(String, nullable=True)


class RedeSocialCandidato(Base):
    __tablename__ = "redes_sociais_candidato"

    id = Column(Integer, primary_key=True, index=True)

    sq_candidato = Column(
        String,
        nullable=False,
        index=True,
    )

    ordem = Column(String, nullable=True)
    url = Column(Text, nullable=False)
