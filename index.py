#!/usr/bin/env python3
from bs4 import BeautifulSoup
import json
import sys
import xapian
import os

from nltk.corpus import stopwords #nltk para stopwords
stop_es = stopwords.words('spanish')


os.chdir('/home/felipe/Documents/IR')

# A pasta onde os documentos estão guardadas
datadir = "./data2" if len(sys.argv) < 2 else sys.argv[1]
# A pasta onde o banco de dados será guardado
dbpath = "db3" if len(sys.argv) < 3 else sys.argv[2]
doccount = 0

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
        identifier = s('docno')[0].get_text()
        title = s('title')[0].get_text()
        text = s('text')[0].get_text()

        # Imprime o documento lido
        # print("{}    {}    {}    {}".format(
        #     doccount,
        #     identifier,
        #     title[:12].replace('\n', '').replace('\t', ''),
        #     text[:80].replace('\n', '').replace('\t', ''))[:80])

        # Cria o documento e usa ele no termgenerator
        doc = xapian.Document()


        # Para busca específica no Título (Subject) ou no Texto (XText)


        # Dump do texto para display
        doc.set_data(json.dumps(
            {'id': identifier,
             'title': title,
             'text': text}))

        # O Q é um prefixo para ID
        termgenerator.set_document(doc)


        termgenerator.index_text(title, 1, 'S')
        termgenerator.index_text(text, 1, 'XT')

        # Para busca Genérica em qualquer campo
        termgenerator.index_text(title)
        termgenerator.increase_termpos()
        termgenerator.index_text(text)



        idterm = u"Q" + identifier
        doc.add_boolean_term(idterm)
        db.replace_document(idterm, doc)
    # end for
    print(doccount)
# end for
