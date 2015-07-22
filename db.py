#!/usr/bin/python
# -*- encoding: utf-8 -*-

from sqlalchemy import create_engine, \
     Column, ForeignKey, UniqueConstraint, \
     BigInteger, Integer, String, DateTime, Date, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
import sys, datetime
import dbconf

engine = create_engine(dbconf.url)
Base = declarative_base()


class Item(Base):
    __tablename__ = 'item'
    __table_args__ = (UniqueConstraint('id_cnpq', 'seq_prod'),
                      {'schema': 'synclattes'})

    id = Column(BigInteger, primary_key=True)
    id_cnpq = Column(BigInteger, ForeignKey('synclattes.pessoa_lattes.id_cnpq'), nullable=False)
    seq_prod = Column(Integer, nullable=False)
    dspace_item_id = Column(BigInteger, nullable=True)
    dspace_cur_rev_id = Column(BigInteger, ForeignKey('synclattes.revision.id'), nullable=True)
    skip = Column(Boolean, nullable=False, default=False)
    frozen = Column(Boolean, nullable=False, default=False)

    pessoa_lattes = relationship('PessoaLattes', order_by=id,
                                 backref='items', foreign_keys=[id_cnpq])

    revisions = relationship('Revision', order_by='Revision.id',
                             backref='item', foreign_keys='[Revision.item_id]')

    dspace_cur_rev = relationship('Revision', uselist=False,
                                  foreign_keys=[dspace_cur_rev_id])

    def __repr__(self):
        return '<Item(id=%s, id_cnpq=%s, seq_prod=%s, dspace_item_id=%s, skip=%s, frozen=%s)>' % \
               (self.id, self.id_cnpq, self.seq_prod, self.dspace_item_id, self.skip, self.frozen)


class Revision(Base):
    __tablename__ = 'revision'
    __table_args__ = {'schema': 'synclattes'}

    id = Column(BigInteger, primary_key=True)
    item_id = Column(BigInteger, ForeignKey('synclattes.item.id'), nullable=False)
    retrieval_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    source = Column(String, nullable=False)
    meta = Column(JSONB, nullable=True)  # null se o item foi removido
    duplicate_of_id = Column(BigInteger, ForeignKey('synclattes.revision.id'), nullable=True)

    duplicates = relationship('Revision', backref=backref('duplicate_of', remote_side=[id]),
                              foreign_keys=[duplicate_of_id])

    def __repr__(self):
        return '<Revision(id=%s, item=%s, retrieval_time="%s", source="%s", meta=%s, duplicate_of_id=%s)>' % \
               (self.id, self.item, self.retrieval_time, self.source, self.meta, self.duplicate_of_id)


class PessoaLattes(Base):
    __tablename__ = 'pessoa_lattes'
    __table_args__ = {'schema': 'synclattes'}

    id_cnpq = Column(BigInteger, primary_key=True, autoincrement=False)
    pessoa_id = Column(BigInteger, ForeignKey('core.pessoa.id'), nullable=False)

    def __repr__(self):
        return '<PessoaLattes(id_cnpq=%s, pessoa_id=%s)>' % \
               (self.id_cnpq, self.pessoa_id)


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


if __name__ == '__main__':
    # Se o script for executado diretamente, cria o schema do banco de dados
    Base.metadata.create_all(engine)
    sys.exit(0)


Session = sessionmaker(bind=engine)