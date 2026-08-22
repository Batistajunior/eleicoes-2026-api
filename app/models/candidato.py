from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Candidato(Base):
    __tablename__ = "candidatos"

    id = Column(Integer, primary_key=True, index=True)

    sq_candidato = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    uf = Column(
        String(2),
        index=True,
    )

    cargo = Column(
        String,
        index=True,
    )

    numero = Column(String)

    nome = Column(
        String,
        index=True,
    )

    nome_urna = Column(
        String,
        index=True,
    )

    numero_partido = Column(String)

    sigla_partido = Column(
        String,
        index=True,
    )

    nome_partido = Column(String)

    situacao = Column(String)

    foto_url = Column(String, nullable=True)
