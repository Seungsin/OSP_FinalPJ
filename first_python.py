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
Analysis.es.indices.delete(index='*')

data_list = []

@first_python.route('/')
def index():
        try:
                url_list = []
                urf_data = Analysis.es.search(index='web', body={'query':{'match_all':{}}})
                data = urf_data['hits']['hits']
                for url in data:
                        url_list.append(url['_source']['URL'])
                return render_template('HTMLPage1.html', urls = url_list)
        except:
                return render_template('main.html')

@first_python.route('/osp_final', methods=['GET', 'POST'])
def upload_file():
        if request.method == 'POST':
                f=request.files['file']
                f.save('./uploads/'+secure_filename(f.filename))
                fp=open('./uploads/'+secure_filename(f.filename), 'r')
                url_list = []
                while True:
                        url = fp.readline()
                        url = url.replace("\n", "")
                        if url == "":
                                break
                        url_list.append(url)
                       
                for url in url_list:
                        flag = False
                        for data in data_list:
                                if url == data['url']: # 중복 url 존재
                                        data['status'] = 'Repeated'
                                        flag = True
                                        break
                        if flag:
                                continue

                        start = time.time()
                        wordfreq = Analysis.upload(url)
                        if wordfreq == -1: # 크롤링 실패
                                data_list.append({
                                        'url' : url,
                                        'time' : -1,
                                        'word' : -1,
                                        'status' : 'Fail' })
                                continue
                       
                        cnt = 0
                        for c in wordfreq.values():
                                cnt += c
                        end = time.time()
                        data_list.append({
                                'url' : url,
                                'time' : format(end - start, ".2f"),
                                'word' : cnt,
                                'status' : 'Success' })
               
                return render_template('Analysis_result_main.html', datas = data_list)
       
        else:
                url = request.args.get('search')
                url = url.replace("%3A", ":")
                url = url.replace("%2F", "/")

                for data in data_list:
                        if url == data['url']: # 중복 url 존재
                                data['status'] = 'Repeated'
                                return render_template('Analysis_result_main.html', datas = data_list)
               
                start = time.time()
                wordfreq = Analysis.upload(url)
                if wordfreq == -1: # 크롤링 실패
                        data_list.append({
                                'url' : url,
                                'time' : -1,
                                'word' : -1,
                                'status' : 'Fail' })
                        return render_template('Analysis_result_main.html', datas = data_list)
                       
                cnt = 0
                for c in wordfreq.values():
                        cnt += c
                end = time.time()
                proc_time = end - start

                data_list.append({
                        'url' : url,
                        'time' : format(proc_time, ".2f"),
                        'word' : cnt ,
                        'status' : 'Success' })       

                return render_template('Analysis_result_main.html', datas = data_list)
       
@first_python.route('/getKeywords', methods=['POST'])
def getKeywords():
        url = request.form['urlName']
        url = url.replace("%3A", ":")
        url = url.replace("%2F", "/")
        print(url)
        tf_idf = Analysis.tf_idf(url)
        keywords = sorted(tf_idf.items(), reverse=True, key=operator.itemgetter(1))
        Keywords = []
        for word in keywords[0:10]:
                Keywords.append((word[0], format(word[1], ".6f")))
               
        return render_template('showPopup_word.html', keywords = Keywords)

@first_python.route('/getSimilar', methods=['POST'])
def getSimilar():
        url = request.form['urlName']
        url = url.replace("%3A", ":")
        url = url.replace("%2F", "/")
        Similarity = []
        urf_data = Analysis.es.search(index='word_freq', body={'query':{'match_all':{}}})
        data = urf_data['hits']['hits']
       
        for target in data:
                if url == target['_id']:
                        continue
                Similarity.append((target['_id'], Analysis.cos_sim(url, target['_id'])))
        Similarity = sorted(Similarity, key=operator.itemgetter(1), reverse=True)
        similarity = []
        for cossim in Similarity:
                similarity.append((cossim[0], format(cossim[1], ".6f")))
        if(len(similarity) == 0): similarity.append("None")
        if(len(similarity) < 3):
                return render_template("showPopup_site.html", similars = similarity)
       
        else:
                return render_template("showPopup_site.html", similars = similarity[:3])
       
if __name__ == '__main__':
        first_python.run(host='127.0.0.1', port=5000, debug=True)
