from bs4 import BeautifulSoup
import gensim
import numpy
import json
import sys
import xapian
import os
from nltk.corpus import stopwords # nltk para stopwords e stemming
import csv
from nltk.tokenize import word_tokenize
sys.path.append('/home/felipe/Documents/IR/Code')
from reord import distcorr

sys.stdout=open("test_dist_corr.txt","w")

#carrega word2vec
model = gensim.models.KeyedVectors.load_word2vec_format('/home/felipe/Downloads/sbw_vectors.bin', binary=True) 

stop_es = stopwords.words('spanish')

stop_es_quer = stop_es
stop_es_quer.append('OR')
stop_es_quer.append('AND')

os.chdir('/home/felipe/Documents/IR')

dbpath = "./db4"

offset = 0  # Inicia o conjunto de resultados no primeiro valor
pagesize = 100  # Número de itens a serem retornados

querydir = "Consultas_new.txt"

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


# Abre o arquivo e faz parse nele
soup = BeautifulSoup(open(querydir, encoding='iso-8859-1'), 'html.parser')
# Para cada consulta dentro do arquivo
for s in soup('top'):
    doccount = doccount + 1
    query_num = s('num')[0].get_text()
    query_nova = s('quer')[0].get_text()

    # Faz parse na consulta
    query = queryparser.parse_query(query_nova)

    # Roda a busca
    enquire = xapian.Enquire(db)
    enquire.set_query(query)

    # armazena resultados
    matches = []
    xapian_scores = []
    for match in enquire.get_mset(offset, pagesize):        
        fields = json.loads(match.document.get_data().decode('utf-8'))
        xapian_scores.append(match.weight)
        matches.append(fields)
        
    # end for
    
    # gera a matriz de word2vec para a query
    # shitty code, I know
    tmp_query=word_tokenize(query_nova)
    words_query=[word for word in tmp_query if word.isalpha()]
    words_query = [word for word in words_query if word not in stop_es_quer] # arrumar melhor forma pro OR e AND
    array_tmp_query = numpy.array([]).reshape(300,0)
    for palavra in words_query:
        #print(palavra)
        #print(array_tmp_query.shape)
        try:
            tmp = model[palavra.lower()]
            array_tmp_query = numpy.column_stack((array_tmp_query,tmp))

        except:
            try:
                tmp = model[palavra[0].upper() + palavra[1:].lower()]
                array_tmp_query = numpy.column_stack((array_tmp_query,tmp))
            except:
                try:
                    tmp = model[palavra.upper()]
                    array_tmp_query = numpy.column_stack((array_tmp_query,tmp))
                except:
                    pass
    
    # itera pelos docs retornados da consulta
    
    dist_scores = []
    for match_tmp in matches:
        tmp = word_tokenize(match_tmp['text'])
        words = [word for word in tmp if word.isalpha()]
        words = [word for word in words if word not in stop_es]

        array_tmp_doc = numpy.array([]).reshape(300,0)
        for palavra in words:
            try:
                tmp = model[palavra.lower()]
                array_tmp_doc = numpy.column_stack((array_tmp_doc,tmp))

            except:
                try:
                    tmp = model[palavra[0].upper() + palavra[1:].lower()]
                    array_tmp_doc = numpy.column_stack((array_tmp_doc,tmp))
                except:
                    try:
                        tmp = model[palavra.upper()]
                        array_tmp_doc = numpy.column_stack((array_tmp_doc,tmp))
                    except:
                        pass
        dist_scores.append(distcorr(array_tmp_doc,array_tmp_query))
    
    # computa novo score
    dist_scores = numpy.array(dist_scores)
    xapian_scores = numpy.array(xapian_scores)
    score_final = (dist_scores*xapian_scores)**(1/2)
    ranking_final = numpy.argsort(-score_final)
    
    # output dos resultados
    for idx, match_id in enumerate(ranking_final.tolist()):
        print("{query_no}\t{quality}\t{doc_no}\t{rank}\t{score}\t{student}".format(
            query_no=query_num,
            quality='Q0',
            doc_no=matches[match_id].get('id'),
            rank=idx,
            score=score_final[match_id],
            student='felipe'))
        
sys.stdout.close()