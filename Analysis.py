#!/usr/bin/python

import sys
import re 
import requests
import operator
import numpy
from bs4 import BeautifulSoup
from math import log

WORD = {}
TF = {}
IDF = {}
TF_IDF = {}

def wordFreq(url):
        res = requests.get(url)
        html = BeautifulSoup(res.content, 'html.parser')

        contents = html.find_all('a') # 검색할 tag

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

        WORD[url] = list(wordfreq.items())
        WORD[url].sort()
        
        return wordfreq

def find_tf(url, wordfreq):
        tf = {}
        
        soc = 0.0
        for count in wordfreq.values():
                soc += count
                
        for word, count in wordfreq.items():
                tf[word] = count / soc
                        
        TF[url] = tf

def find_idf(url, wordfreq):
        for word in wordfreq.keys():
                if word in IDF.keys():
                        IDF[word] += 1
                else:
                        IDF[word] = 1


def tf_idf_update():
        for url in TF_IDF.keys():
                for word, tf in TF[url].items():
                        TF_IDF[url][word] = tf * (log(len(TF)/IDF[word]))



def tf_idf(url):
        if url in TF_IDF.keys():
                return
        wordfreq = wordFreq(url)
        find_tf(url, wordfreq)
        find_idf(url, wordfreq)
        
        tf_idf = {}
        
        for word, tf in TF[url].items():
                tf_idf[word] = tf * (log(len(TF)/IDF[word]))
                        
        TF_IDF[url] = tf_idf

        tf_idf_update()
        
def word_update():
        for wordfreq in WORD.values():
                worddict = dict(wordfreq)
                for word in IDF.keys():
                        if word not in worddict:
                                wordfreq.append((word, 0))
                wordfreq.sort()

def cos_sim(url1, url2):
        if url1 not in WORD.keys():
                print('''You must do 'tf_idf' first to 'do cos_similarity''''')
                return
        if url2 not in WORD.keys():
                print('''You must do 'tf_idf' first to 'do cos_similarity''''')
                return
        word_update()

        target1 = numpy.array(list(dict(WORD[url1]).values()))
        target2 = numpy.array(list(dict(WORD[url2]).values()))
        
        dotprod = numpy.dot(target1, target2)
        cos_sim = float(dotprod / (numpy.linalg.norm(target1) * numpy.linalg.norm(target2)))

        return cos_sim
