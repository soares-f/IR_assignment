import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cria_db import documentos, Base
import re
import xapian
import json
from nltk.corpus import stopwords #nltk para stopwords
stop_es = stopwords.words('spanish')


os.chdir('/home/felipe/Documents/IR')


# ----- Xapian config -----
# A pasta onde o banco de dados será guardado
dbpath = "db4" if len(sys.argv) < 3 else sys.argv[2]

# Cria ou abre o banco de dados
db = xapian.WritableDatabase(dbpath, xapian.DB_CREATE_OR_OPEN)
# Cria o gerador de termos e coloca o stemmer pra espanhol
termgenerator = xapian.TermGenerator()
termgenerator.set_stemmer(xapian.Stem("es"))
termgenerator.set_stemming_strategy(termgenerator.STEM_ALL_Z) #gera somente termos stemmed

#inclui stopwords
stopper = xapian.SimpleStopper()
for word in stop_es:
    stopper.add(word)

termgenerator.set_stopper(stopper)
termgenerator.set_stopper_strategy(termgenerator.STOP_ALL) #remove stop em termos
# ----- end Xapian config -----


# abre BD
engine = create_engine('sqlite:///dados_all.db')

# conf sqlalchemy
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# cria query
docs = session.query(documentos).all()



doccount = 0
for documento in docs:
    doccount = doccount + 1
    #print(doccount)

    # separa assinatura da noticia (EFE)
    # ficou bem gambiarra, mas paciencia

    try:
        split_1 = re.split(r'EFE\n', documento.text)
        if len(split_1) > 2:
            texto_fim = documento.text
        else:
            texto_fim = re.split(r'\(EFE\).-', split_1[0])[1]
    except:
        texto_fim = documento.text

    # Cria o documento e usa ele no termgenerator
    doc = xapian.Document()

    # Dump do texto para display
    doc.set_data(json.dumps(
        {'id': documento.docno,
         'title': documento.title,
         'text': documento.text}))

    # O Q é um prefixo para ID
    termgenerator.set_document(doc)

    # Para busca específica no Título (Subject) ou no Texto (XText)
    termgenerator.index_text(documento.title, 1, 'S')
    termgenerator.index_text(texto_fim, 1, 'XT')

    # Para busca Genérica em qualquer campo
    termgenerator.index_text(documento.title)
    termgenerator.increase_termpos()
    termgenerator.index_text(texto_fim)

    idterm = u"Q" + documento.docno
    doc.add_boolean_term(idterm)
    db.replace_document(idterm, doc)


