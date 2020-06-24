import sys
import re
import requests
import operator
import numpy
import copy
from bs4 import BeautifulSoup
from math import log
from elasticsearch import Elasticsearch

es = Elasticsearch('localhost:9200', timeout=30)

def wordFreq(url):
        try:
                res = es.get(index='word_freq', id=url)
                return res['_source']
        except:
                print('Data does not exist.')
                        
        res = requests.get(url)
        html = BeautifulSoup(res.content, 'html.parser')


        p = html.find_all('p')
        a = html.find_all('a')
        li = html.find_all('li')
        h1 = html.find_all('h1')
        h2 = html.find_all('h2')
        h3 = html.find_all('h3')
        h4 = html.find_all('h4')
        h5 = html.find_all('h5')

        contents = []
        contents.extend(p)
        contents.extend(a)
        contents.extend(li)
        contents.extend(h1)
        contents.extend(h2)
        contents.extend(h3)
        contents.extend(h4)
        contents.extend(h5)

        wordfreq = {}
        for content in contents:
                content = content.text.lower()
                content = re.sub('[^a-z]', '  ', content)
                content = content.split()

                for word in content:
                        if word in wordfreq.keys():
                                wordfreq[word] += 1
                        else:
                                wordfreq[word] = 1

        es.index(index='word_freq', id=url, body=wordfreq)
        es.indices.refresh(index='word_freq')
        
        return wordfreq

def getTF(wordfreq):
        tf = {}
        
        soc = 0.0
        for count in wordfreq.values():
                soc += count

        for word, count in wordfreq.items():
                tf[word] = count/soc

        return tf

def update():
        try:
                urf_idf = es.get(index='idf', id='idf')
                idf = urf_idf['_source']

                urf_data = es.search(index='word_freq', body={'query':{'match_all':{}}})
                data = urf_data['hits']['hits']
                for web in data:
                        tf = getTF(web['_source'])
                        tf_idf = {}
                        for word, tf_v in tf.items():
                                tf_idf[word] = tf_v * (log(urf_idf['_version']/idf[word]))
                        es.index(index='tf_idf', id=web['_id'], body=tf_idf)

                es.indices.refresh(index='tf_idf')
                
        except:
                print('An error occurred while updating...')

def getIDF(wordfreq):
        try:
                res = es.get(index='idf', id='idf')
                idf = res['_source']
        except: 
                idf = {}
        for word in wordfreq.keys():
                if word in idf.keys():
                        idf[word] += 1
                else:
                        idf[word] = 1

        es.index(index='idf', id='idf', body=idf)
        es.indices.refresh(index='idf')

        update()

        return idf

def tf_idf(url):
        try:
                res = es.get(index='tf_idf', id=url)
                return res['_source']
        except:
                print('Data does not exist.')

        get = es.get(index='word_freq', id=url)
        wordfreq = get['_source']
        tf = getTF(wordfreq)
        urf_idf = es.get(index='idf', id='idf')
        idf = urf_idf['_source']

        tf_idf = {}

        count = es.get(index='idf', id='idf')
        for word, tf_v in tf.items():
                tf_idf[word] = tf_v * (log(count['_version']/idf[word]))

        es.index(index='tf_idf', id=url, body=tf_idf)
        es.indices.refresh(index='tf_idf')
        
        return tf_idf

def cos_sim(url1, url2):
        try:
                res = es.get(index='cos_sim', id=url1)
                cos_sim = res['_source'][url2]
                return cos_sim
        except:
                print('Data does not exist.')
                
        target1 = es.get(index='word_freq', id=url1)
        target2 = es.get(index='word_freq', id=url2)
        t1 = copy.deepcopy(target1['_source'])
        t2 = copy.deepcopy(target2['_source'])
        for word in t1.keys():
                if word not in t2.keys():
                        t2[word] = 0
        for word in t2.keys():
                if word not in t1.keys():
                        t1[word] = 0
        w1 = sorted(list(t1.items()))
        w2 = sorted(list(t2.items()))
        n1 = numpy.array(list(dict(w1).values()))
        n2 = numpy.array(list(dict(w2).values()))

        dotprod = numpy.dot(n1, n2)
        cos_sim = float(dotprod / (numpy.linalg.norm(n1) * numpy.linalg.norm(n2)))

        try:
                urf_data = es.get(index='cos_sim', id=url1)
                data = urf_data['_source']
                data[url2] = cos_sim
        except: 
                data = { url2 : cos_sim }
        es.index(index='cos_sim', id=url1, body=data)
        es.indices.refresh(index='cos_sim')

        return cos_sim


def upload(url):
        wordfreq = wordFreq(url)
        getIDF(wordfreq)

        return wordfreq
