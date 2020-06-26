#!/bin/bash

mkdir ../../Final_team1

mv ./templates ../../Final_team1
mv ./static ../../Final_team1
mv ./uploads ../../Final_team1
mv first_python.py ../../Final_team1
mv Analysis.py ../../Final_team1

cd
cd Final_team1
export FLASK_APP=first_python.py
flask run 
