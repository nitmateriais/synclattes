from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import conf.dbconf as dbconf

engine = create_engine(dbconf.url)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()