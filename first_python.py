#!/usr/bin/python3
from flask import Flask
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename
import re
import sys

first_python = Flask(__name__)

@first_python.route('/')
def index():
	return render_template('HTMLPage1.html')

@first_python.route('/osp_final', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		f=request.files['file']
		f.save('./uploads/'+secure_filename(f.filename))
		fp=open('./uploads/textfile.txt', 'r')
		lines=fp.readlines()"""lines is list of url"""
		return lines[0]
	else:
		u=request.args.get('url')
		return u
		

if __name__ == '__main__':
	first_python.run(host='127.0.0.1', port=8000, debug=True)
		
