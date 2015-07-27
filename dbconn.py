# -*- encoding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy.orm import sessionmaker
from alchemyext.view import RefreshMaterializedView
import conf.dbconf as dbconf

engine = create_engine(dbconf.url)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# http://stackoverflow.com/a/2587041
def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True

def refresh_materialized_view(session, model):
    """
    Atualiza os dados de uma MATERIALIZED VIEW.

    Importante: A transação atual é commitada antes de realizar a operação.
    """
    session.commit()
    engine.execute(RefreshMaterializedView(model.__table__))

def create_temp_table(model):
    model.__table__.create(bind = engine)

def yield_batches(q, id_field, batch_size=1024, id_from_row=None):
    """
    Executes a query `q` by batches of `batch_size` over `id_field`.
    If the query does not return an ORM object, provide an `id_from_row`
    function to extract the id field value from the row, e.g.
    `lambda row: row[0]` for extracting the first field from the row.
    """
    curId = 0
    if id_from_row is None:
        assert hasattr(id_field, 'key'), \
               'If function id_from_row is not provided, id_field.key needs to be defined'
        id_from_row = lambda row: getattr(row, id_field.key)
    while True:
        batch = q.filter(id_field > curId)\
                 .order_by(id_field.asc())\
                 .limit(batch_size).all()
        if len(batch) == 0:
            break
        for row in batch:
            yield row
        curId = id_from_row(batch[-1])

session = Session()
session.__class__.get_or_create = get_or_create
session.__class__.refresh_materialized_view = refresh_materialized_view
