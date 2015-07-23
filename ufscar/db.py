# -*- encoding: utf-8 -*-
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
    version = Column(BigInteger, nullable=False, default=0)
    cpf = Column(String(255), nullable=True)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(255), nullable=True)
    idioma = Column(String(255), nullable=False)
    nacionalidade_id = Column(BigInteger, nullable=False)  # FK omitida
    naturalidade_id = Column(BigInteger, nullable=True)    # FK omitida
    nome = Column(String(255), nullable=False)
    passaporte = Column(String(255), nullable=True)
    validade_visto = Column(Date, nullable=True)
    sexo = Column(ENUM('M', 'F', name='sexo'), nullable=True)
    alterado_manualmente = Column(Boolean, nullable=False, default=False)
    date_created = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, nullable=True)

    pessoa_lattes = relationship('PessoaLattes', uselist=False, backref='pessoa')

    def __repr__(self):
        return '<Pessoa(id=%r, cpf=%r, data_nascimento=%r, email=%r, nome=%r)>' % \
               (self.id, self.cpf, self.data_nascimento, self.email, self.nome)


class Vinculo(Base):
    __tablename__ = 'vinculo'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True)
    version = Column(BigInteger, nullable=False, default=0)
    fim_vinculo = Column(Date, nullable=True)  # null se o vínculo ainda estiver ativo
    inicio_vinculo = Column(Date, nullable=False)
    pais_convenio_id = Column(BigInteger, nullable=True)  # FK omitida
    pessoa_id = Column(BigInteger, ForeignKey('core.pessoa.id'), nullable=False)
    tipo_id = Column(BigInteger, ForeignKey('core.tipo_vinculo.id'), nullable=False)
    unidade_organizacional_id = Column(BigInteger, ForeignKey('core.unidade_organizacional.id'), nullable=False)
    date_created = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, nullable=True)

    pessoa = relationship('Pessoa', backref='vinculos')
    tipo = relationship('TipoVinculo')
    unidade_organizacional = relationship('UnidadeOrganizacional')

    def __repr__(self):
        return '<Vinculo(id=%r, inicio_vinculo=%r, fim_vinculo=%r, pessoa=%r, tipo=%r, unidade_organizacional=%r)>' % \
               (self.id, self.inicio_vinculo, self.fim_vinculo, self.pessoa, self.tipo, self.unidade_organizacional)


class TipoVinculo(Base):
    __tablename__ = 'tipo_vinculo'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True)
    version = Column(BigInteger, nullable=False, default=0)
    ativo = Column(Boolean, nullable=False)
    descricao = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=False)
    unidade_responsavel_id = Column(BigInteger, ForeignKey('core.unidade_organizacional.id'), nullable=True)

    unidade_responsavel = relationship('UnidadeOrganizacional')

    def __repr__(self):
        return '<TipoVinculo(id=%r, ativo=%r, nome=%r, descricao=%r, unidade_responsavel=%r)>' % \
               (self.id, self.ativo, self.nome, self.descricao, self.unidade_responsavel)


class UnidadeOrganizacional(Base):
    __tablename__ = 'unidade_organizacional'
    __table_args__ = (UniqueConstraint('sigla'),
                      {'schema': 'core'})

    id = Column(BigInteger, primary_key=True)
    version = Column(BigInteger, nullable=False, default=0)
    campus_id = Column(BigInteger, nullable=True)  # FK omitida
    email = Column(String(255), nullable=True)
    fim_funcionamento = Column(Date, nullable=True)  # null se ainda em funcionamento
    inicio_funcionamento = Column(Date, nullable=False)
    nome = Column(String(255), nullable=False)
    pai_id = Column(BigInteger, ForeignKey('core.unidade_organizacional.id'), nullable=True)
    sigla = Column(String(255), nullable=False)
    tipo_id = Column(BigInteger, ForeignKey('core.tipo_unidade_organizacional.id'), nullable=False)
    portaria_criacao = Column(String(255), nullable=True)
    codigo_siape = Column(BigInteger, nullable=True)

    filhas = relationship('UnidadeOrganizacional', backref=backref('pai', remote_side=[id]),
                          foreign_keys=[pai_id])

    tipo = relationship('TipoUnidadeOrganizacional')

    def __repr__(self):
        return '<UnidadeOrganizacional(id=%r, campus_id=%r, email=%r, inicio_funcionamento=%r, fim_funcionamento=%r, nome=%r, pai_id=%r, sigla=%r, tipo=%r)>' % \
               (self.id, self.campus_id, self.email, self.inicio_funcionamento, self.fim_funcionamento, self.nome, self.pai_id, self.sigla, self.tipo)


class TipoUnidadeOrganizacional(Base):
    __tablename__ = 'tipo_unidade_organizacional'
    __table_args__ = (UniqueConstraint('nome'),
                      {'schema': 'core'})

    id = Column(BigInteger, primary_key=True)
    version = Column(BigInteger, nullable=False, default=0)
    nome = Column(String(255), nullable=False)

    def __repr__(self):
        return '<TipoUnidadeOrganizacional(id=%r, nome=%r)>' % \
               (self.id, self.nome)
