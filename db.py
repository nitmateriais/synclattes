#!/usr/bin/python
# -*- encoding: utf-8 -*-

from sqlalchemy import create_engine, \
     Column, ForeignKey, UniqueConstraint, \
     BigInteger, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import JSONB
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
    id_cnpq = Column(String, nullable=False)
    seq_prod = Column(Integer, nullable=False)
    dspace_item_id = Column(BigInteger, nullable=True)
    dspace_cur_rev_id = Column(BigInteger, ForeignKey('synclattes.revision.id'), nullable=True)
    skip = Column(Boolean, nullable=False, default=False)
    frozen = Column(Boolean, nullable=False, default=False)

    revisions = relationship('Revision',
                             order_by='Revision.id',
                             backref='item',
                             foreign_keys='[Revision.item_id]')

    dspace_cur_rev = relationship('Revision', uselist=False,
                                  foreign_keys=[dspace_cur_rev_id])

    def __repr__(self):
        return '<Item(id=%d, id_cnpq="%s", seq_prod=%d, dspace_item_id=%s, skip=%s, frozen=%s)>' % \
               (self.id, self.id_cnpq, self.seq_prod, self.dspace_item_id, self.skip, self.frozen)


class Revision(Base):
    __tablename__ = 'revision'
    __table_args__ = {'schema': 'synclattes'}

    id = Column(BigInteger, primary_key=True)
    item_id = Column(BigInteger, ForeignKey('synclattes.item.id'), nullable=False)
    retrieval_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    source = Column(String, nullable=False)
    meta = Column(JSONB, nullable=True)  # null se o item foi removido
    duplicate_of_id = Column(BigInteger, ForeignKey('synclattes.revision.id'), nullable=True)

    duplicates = relationship('Revision',
                              backref=backref('duplicate_of', remote_side=[id]),
                              foreign_keys=[duplicate_of_id])

    def __repr__(self):
        return '<Revision(id=%d, item=%s, retrieval_time="%s", source="%s", meta=%s, duplicate_of_id=%s)>' % \
               (self.id, self.item, self.retrieval_time, self.source, self.meta, self.duplicate_of_id)


if __name__ == '__main__':
    # Se o script for executado diretamente, cria o schema do banco de dados
    Base.metadata.create_all(engine)
    sys.exit(0)


Session = sessionmaker(bind=engine)