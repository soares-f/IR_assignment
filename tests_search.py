#!/usr/bin/env python3
from bs4 import BeautifulSoup
import json
import sys
import xapian
import os
from nltk.corpus import stopwords # nltk para stopwords e stemming
import csv

stop_es = stopwords.words('spanish')

os.chdir('/home/felipe/Documents/IR')

dbpath = "./db4" if len( sys.argv ) < 3 else sys.argv[2]

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


query_title = 'Conferencia de la Mujer en Pekín'
query_text = 'Las posiciones controvertidas adoptadas por algunos delegados hicieron que la Conferencia mundial de la Mujer en Pekín se expusiese al fracaso.'

# Faz parse na consulta
query = queryparser.parse_query(query_title + '\n' + query_text)

# Roda a busca
enquire = xapian.Enquire(db)
enquire.set_query(query)

matches = []
for match in enquire.get_mset(offset, pagesize):
    fields = json.loads(match.document.get_data().decode('utf-8'))
    matches.append(fields)

myfile = open('testeb.csv', 'w')
wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
wr.writerow(matches)
myfile.close()