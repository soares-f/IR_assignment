#!/usr/bin/env python3
from bs4 import BeautifulSoup
import json
import sys
import xapian
import os
from nltk.corpus import stopwords # nltk para stopwords e stemming


stop_es = stopwords.words('spanish')

os.chdir('/home/felipe/Documents/IR')

dbpath = "./db3" if len( sys.argv ) < 3 else sys.argv[2]

querydir = "Consultas.txt" if len(sys.argv) < 2 else sys.argv[1]
offset = 0  # Inicia o conjunto de resultados no primeiro valor
pagesize = 100  # Número de itens a serem retornados



# Abre o banco de dados
db = xapian.Database(dbpath)

# Cria o parser das queries e coloca o stemmer pra espanhol
queryparser = xapian.QueryParser()
queryparser.set_stemmer(xapian.Stem("es"))

queryparser.set_stemming_strategy(queryparser.STEM_ALL_Z)
doccount = 0

#inclui stopwords
stopper = xapian.SimpleStopper()

for word in stop_es:
    stopper.add(word)

queryparser.set_stopper(stopper)
queryparser.set_stopper_strategy(queryparser.STOP_ALL)



# Abre o arquivo e faz parse nele
soup = BeautifulSoup(open(querydir, encoding='iso-8859-1'), 'html.parser')
# Para cada consulta dentro do arquivo
for s in soup('top'):
    doccount = doccount + 1
    query_num = s('num')[0].get_text()
    query_title = s('es-title')[0].get_text()
    query_text = s('es-desc')[0].get_text()

    # Faz parse na consulta
    query = queryparser.parse_query(query_title + '\n' + query_text)

    # Roda a busca
    enquire = xapian.Enquire(db)
    enquire.set_query(query)

    # Imprime os resultados
    matches = []
    for match in enquire.get_mset(offset, pagesize):
        fields = json.loads(match.document.get_data().decode('utf-8'))
        print("{query_no}\t{quality}\t{doc_no}\t{rank}\t{score}\t{student}".format(
            query_no=query_num,
            quality='Q0',
            doc_no=fields.get('id'),
            rank=match.rank,
            score=match.weight,
            student='pedro'))
        matches.append(fields)
    # end for

# end for
