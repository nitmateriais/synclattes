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

def refreshMaterializedView(model):
    engine.execute(RefreshMaterializedView(model.__table__))

session = Session()
session.__class__.get_or_create = get_or_create

