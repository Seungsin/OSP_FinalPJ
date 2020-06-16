#!/usr/bin/python3
from flask import Flask
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename
import sys
import re
import requests
import operator
import time
import Analysis # 웹사이트 분석 함수

first_python = Flask(__name__)

@first_python.route('/')
def index():
        return render_template('HTMLPage1.html')

@first_python.route('/osp_final', methods=['GET', 'POST'])
def upload_file():
        if request.method == 'POST':
                f=request.files['file']
                f.save('./uploads/'+secure_filename(f.filename))
                fp=open('./uploads/'+secure_filename(f.filename), 'r')
                url_list = []
                while True:
                        url = fp.readline()
                        if url == "":
                                break
                        url_list.append(url) 
                for url in url_list:
                        Analysis.tf_idf(url)

                return render_template('HTMLPage1.html', urls = url_list)
        
        else:
                u = request.args.get('url')
                u = u.replace("%3A", ":")
                u = u.replace("%2F", "/")
                Analysis.tf_idf(u)

                url_list = []
                urf_data = Analysis.es.search(index='web', body={'query':{'match_all':{}}})
                data = urf_data['hits']['hits']
                for url in data:
                        url_list.append(url['_source']['URL'])
                
                return render_template('HTMLPage1.html', urls = url_list)
        
@first_python.route('/getKeywords', methods=['GET'])
def getKeywords():
        url = request.args.get('url')
        url = url.replace("%3A", ":")
        url = url.replace("%2F", "/")
        start = time.time()
        tf_idf = Analysis.es.get(index='web', id=url)
        
        Keywords = sorted(tf_idf['_source']['TF-IDF'].items(), reverse=True, key=operator.itemgetter(1))
        end = time.time()
        
        return render_template('Keywords.html', keywords = Keywords[0:10], proc_time = end-start)

@first_python.route('/getSimilar', methods=['GET'])
def getSimilar():
        url = request.args.get('url')
        url = url.replace("%3A", ":")
        url = url.replace("%2F", "/")

        similarity = []
        urf_data = Analysis.es.search(index='web', body={'query':{'match_all':{}}})
        data = urf_data['hits']['hits']
        
        start = time.time()
        for target in data:
                if url == target['_source']['URL']:
                        continue
                similarity.append((target['_source']['URL'], Analysis.cos_sim(url, target['_source']['URL'])))
        similarity = sorted(similarity, key=operator.itemgetter(1), reverse=True)
        end = time.time()
        
        if(len(similarity) < 3):
                return render_template("Similar.html", similars = similarity, proc_time = end-start)
        
        else:
                return render_template("Similar.html", similars = similarity[:3], proc_time = end-start)
        
if __name__ == '__main__':
        first_python.run(host='127.0.0.1', port=8000, debug=True)
