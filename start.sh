#!/bin/bash

cd
mkdir OSP_Final
cd OSP_Final
mkdir templates
mkdir uploads
cd
cd OSP_FinalProject
mv first_python.py ../OSP_Final/
mv HTMLPage1.html ../OSP_Final/templates/
cd ../OSP_Final/
chmod 755 first_python.py
export FLASK_APP=first_python.py
./first_python.py