import os
from sqlalchemy import Column, Integer, String, Text, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

os.chdir('/home/felipe/Documents/IR')

Base = declarative_base()

#cria tabela
class documentos(Base):
    __tablename__ = 'documentos'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    docno = Column(String(30),nullable=False)
    date = Column(String(20))
    time = Column(String(10))
    category = Column(String(100))
    num = Column(Integer)
    prioridad = Column(String(20))
    title = Column(UnicodeText)
    text = Column(UnicodeText)

#cria BD sqlite
engine = create_engine('sqlite:///dados_all.db')

#commit criacao tabela
Base.metadata.create_all(engine)

