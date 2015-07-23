from sqlalchemy import Column, ForeignKey, UniqueConstraint, \
     BigInteger, Integer, String, DateTime, Date, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.orm import relationship, backref
from dbconn import *

class Pessoa(Base):
    __tablename__ = 'pessoa'
    __table_args__ = (UniqueConstraint('cpf'),
                      {'schema': 'core'})

    id = Column(BigInteger, primary_key=True)
    version = Column(BigInteger, nullable=False)
    cpf = Column(String(255), nullable=True)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(255), nullable=True)
    idioma = Column(String(255), nullable=False)
    nacionalidade_id = Column(BigInteger, nullable=False)
    naturalidade_id = Column(BigInteger, nullable=True)
    nome = Column(String(255), nullable=False)
    passaporte = Column(String(255), nullable=True)
    validade_visto = Column(Date, nullable=True)
    sexo = Column(ENUM('M', 'F', name='sexo'), nullable=True)
    alterado_manualmente = Column(Boolean, nullable=False, default=False)
    date_created = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, nullable=True)

    pessoa_lattes = relationship('PessoaLattes', uselist=False, backref='pessoa')

    def __repr__(self):
        return '<Pessoa(id=%s, cpf=%s, data_nascimento="%s", email="%s", nome="%s")>' % \
               (self.id, self.cpf, self.data_nascimento, self.email, self.nome)