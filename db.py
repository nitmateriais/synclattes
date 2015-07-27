#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sqlalchemy
from sqlalchemy import Column, ForeignKey, UniqueConstraint, Index, \
     BigInteger, Integer, String, DateTime, Date, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.orm import relationship, backref
from sqlalchemy import func
import sys, datetime
from alchemyext.view import view
from dbconn import *
from ufscar.db import *

class Item(Base):
    id = Column(BigInteger, primary_key=True)
    id_cnpq = Column(String, ForeignKey('synclattes.pessoa_lattes.id_cnpq'), nullable=False, index=True)
    seq_prod = Column(Integer, nullable=False)
    dspace_item_id = Column(BigInteger, nullable=True)
    dspace_cur_rev_id = Column(BigInteger, ForeignKey('synclattes.revision.id'), nullable=True)
    nofetch = Column(Boolean, nullable=False, default=False)  # não recuperar do CV Lattes para o banco
    nosync = Column(Boolean, nullable=False, default=False)   # não sincronizar do banco com o DSpace

    __tablename__ = 'item'
    __table_args__ = (UniqueConstraint(id_cnpq, seq_prod),
                      {'schema': 'synclattes'})

    pessoa_lattes = relationship('PessoaLattes', order_by=id,
                                 backref='items', foreign_keys=[id_cnpq])

    revisions = relationship('Revision', order_by='Revision.id',
                             backref='item', foreign_keys='[Revision.item_id]')

    dspace_cur_rev = relationship('Revision', uselist=False,
                                  foreign_keys=[dspace_cur_rev_id])

    def __repr__(self):
        return '<Item(id=%r, pessoa_lattes=%r, seq_prod=%r, dspace_item_id=%r, nofetch=%r, nosync=%r)>' % \
               (self.id, self.pessoa_lattes, self.seq_prod, self.dspace_item_id, self.nofetch, self.nosync)


class Revision(Base):
    id = Column(BigInteger, primary_key=True)
    item_id = Column(BigInteger, ForeignKey('synclattes.item.id'), nullable=False, index=True)
    retrieval_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    source = Column(String, nullable=False, index=True)
    meta = Column(JSONB(none_as_null=True), nullable=True)  # null se o item foi removido
    duplicate_of_id = Column(BigInteger, ForeignKey('synclattes.revision.id'), nullable=True)

    __tablename__ = 'revision'
    __table_args__ = (Index('ix_synclattes_item_id_rev_id', item_id.asc(), id.desc()),
                      {'schema': 'synclattes'})

    duplicates = relationship('Revision', backref=backref('duplicate_of', remote_side=[id]),
                              foreign_keys=[duplicate_of_id])

    def __repr__(self):
        return '<Revision(id=%r, item=%r, retrieval_time=%r, source=%r, meta=%r, duplicate_of_id=%r)>' % \
               (self.id, self.item, self.retrieval_time, self.source, self.meta, self.duplicate_of_id)


class LastRevision(Base):
    __rev = Revision.__table__
    __table__ = view('last_revision', Base.metadata,
                     sqlalchemy.select([__rev.c.id,
                                        __rev.c.item_id,
                                        __rev.c.retrieval_time,
                                        __rev.c.source,
                                        __rev.c.meta,
                                        __rev.c.duplicate_of_id])\
                               .distinct(__rev.c.item_id)\
                               .select_from(__rev)\
                               .order_by(__rev.c.item_id.asc(), __rev.c.id.desc()),
                     schema='synclattes',
                     prefixes=['MATERIALIZED'])

    __indexes__ = [Index('ix_synclattes_last_revision_id',
                         __table__.c.id),
                   Index('ix_synclattes_last_revision_item_id',
                         __table__.c.item_id),
                   Index('ix_synclattes_last_revision_duplicate_of',
                         __table__.c.duplicate_of_id),
                   Index('ix_synclattes_last_revision_uri0',
                         func.lower(__table__.c.meta[('dc','identifier','uri',0,'value')].astext))]

    item = relationship('Item', uselist=False, backref=backref('last_revision', uselist=False),
                        foreign_keys=[__table__.c.item_id])

    editable = relationship('Revision', uselist=False, backref='last_revision',
                            foreign_keys=[__table__.c.id],
                            primaryjoin=__table__.c.id == Revision.id)

    duplicates = relationship('LastRevision', backref=backref('duplicate_of',
                                                              remote_side=[__table__.c.id]),
                              foreign_keys=[__table__.c.duplicate_of_id])

    def __repr__(self):
        return '<LastRevision(id=%r, item=%r, retrieval_time=%r, source=%r, meta=%r, duplicate_of_id=%r)>' % \
               (self.id, self.item, self.retrieval_time, self.source, self.meta, self.duplicate_of_id)


class PessoaLattes(Base):
    id_cnpq = Column(String, primary_key=True, autoincrement=False)
    pessoa_id = Column(BigInteger, ForeignKey('core.pessoa.id'), nullable=False)

    __tablename__ = 'pessoa_lattes'
    __table_args__ = (UniqueConstraint(pessoa_id),
                      {'schema': 'synclattes'})

    def __repr__(self):
        return '<PessoaLattes(id_cnpq=%r, pessoa_id=%r)>' % \
               (self.id_cnpq, self.pessoa_id)

class RevNormTitle(Base):
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    title = Column(String, nullable=False)

    __tablename__ = 'revision_normalized_title'
    __table_args__ = (Index('ix_temp_rev_norm_title', title),
                      {'prefixes': ['TEMPORARY']})

    def __repr__(self):
        return '<RevNormTitle(id=%r, title=%r)>' % \
               (self.id, self.title)

if __name__ == '__main__':
    # Se o script for executado diretamente, cria as tabelas
    Base.metadata.create_all(engine)

