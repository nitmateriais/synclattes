#!/usr/bin/python
# -*- encoding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, UniqueConstraint, Index, \
     BigInteger, Integer, String, DateTime, Date, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.orm import relationship, backref
import sys, datetime
from dbconn import *
from ufscar.db import *

class Item(Base):
    __tablename__ = 'item'
    __table_args__ = (UniqueConstraint('id_cnpq', 'seq_prod'),
                      {'schema': 'synclattes'})

    id = Column(BigInteger, primary_key=True)
    id_cnpq = Column(String, ForeignKey('synclattes.pessoa_lattes.id_cnpq'), nullable=False, index=True)
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
        return '<Item(id=%r, pessoa_lattes=%r, seq_prod=%r, dspace_item_id=%r, skip=%r, frozen=%r)>' % \
               (self.id, self.pessoa_lattes, self.seq_prod, self.dspace_item_id, self.skip, self.frozen)


class Revision(Base):
    __tablename__ = 'revision'

    id = Column(BigInteger, primary_key=True)
    item_id = Column(BigInteger, ForeignKey('synclattes.item.id'), nullable=False, index=True)
    retrieval_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    source = Column(String, nullable=False, index=True)
    meta = Column(JSONB(none_as_null=True), nullable=True)  # null se o item foi removido
    duplicate_of_id = Column(BigInteger, ForeignKey('synclattes.revision.id'), nullable=True)

    duplicates = relationship('Revision', backref=backref('duplicate_of', remote_side=[id]),
                              foreign_keys=[duplicate_of_id])

    __table_args__ = (Index('uri0_index', meta[('dc','identifier','uri',0,'value')].astext),
                      {'schema': 'synclattes'})

    def __repr__(self):
        return '<Revision(id=%r, item=%r, retrieval_time=%r, source=%r, meta=%r, duplicate_of_id=%r)>' % \
               (self.id, self.item, self.retrieval_time, self.source, self.meta, self.duplicate_of_id)


class PessoaLattes(Base):
    __tablename__ = 'pessoa_lattes'
    __table_args__ = (UniqueConstraint('pessoa_id'),
                      {'schema': 'synclattes'})

    id_cnpq = Column(String, primary_key=True, autoincrement=False)
    pessoa_id = Column(BigInteger, ForeignKey('core.pessoa.id'), nullable=False)

    def __repr__(self):
        return '<PessoaLattes(id_cnpq=%r, pessoa_id=%r)>' % \
               (self.id_cnpq, self.pessoa_id)


if __name__ == '__main__':
    # Se o script for executado diretamente, cria as tabelas
    Base.metadata.create_all(engine)
    sys.exit(0)
