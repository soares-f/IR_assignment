from bs4 import BeautifulSoup
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cria_db import documentos, Base

os.chdir('/home/felipe/Documents/IR')
engine = create_engine('sqlite:///dados_all.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# A pasta aonde os documentos estão guardadas
datadir = "./data2" if len(sys.argv) < 2 else sys.argv[1]
doccount = 0


# Para cada arquivo na pasta passada
for f in os.listdir(datadir):
    # Checa se é um arquivo sgml
    if not f.endswith(".sgml"):
        continue
    # end if
    # Abre o arquivo e faz parse nele
    soup = BeautifulSoup(open(os.path.join(datadir, f), encoding='iso-8859-1'), 'html.parser')
    # Para cada documento dentro do arquivo
    for s in soup('doc'):
        doccount = doccount + 1
        doc_identifier = s('docno')[0].get_text()
        doc_title = s('title')[0].get_text()
        doc_text = s('text')[0].get_text()
        doc_date = s('date')[0].get_text()
        doc_time = s('time')[0].get_text()
        doc_category = s('category')[0].get_text()
        doc_num = s('num')[0].get_text()
        doc_prioridad = s('prioridad')[0].get_text()

        new_doc = documentos(docno = doc_identifier,
                             date = doc_date,
                             time = doc_time,
                             category = doc_category,
                             num = doc_num,
                             prioridad = doc_prioridad,
                             title = doc_title,
                             text = doc_text)

        session.add(new_doc)
    print(doccount)
    session.commit()






