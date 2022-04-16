from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3 as sql
import os
import csv
from sqlite3 import Error
import pandas as pd
from dash_application import create_dash_application

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///naman1.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
create_dash_application(app)


class Netflix(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Show_ID = db.Column(db.String(500),nullable =False)
    Type = db.Column(db.String(500),nullable =False)
    Title = db.Column(db.String(500),nullable =False)
    Director = db.Column(db.String(500),nullable =False)
    Cast  = db.Column(db.String(500),nullable =False)
    Country = db.Column(db.String(500),nullable =False)
    Date_Added = db.Column(db.String(500),nullable =False)
    Release_Year = db.Column(db.String(500),nullable =False)
    Rating = db.Column(db.String(500),nullable =False)
    Duration = db.Column(db.String(500),nullable =False)
    Listed_In = db.Column(db.String(500),nullable =False)
    Description = db.Column(db.String(500),nullable =False)

    def __repr__(self) -> str:
        return f"{self.Type} - {self.Title}"

@app.route('/', methods= ['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        a = request.form['Show_ID']
        b = request.form['Type']
        c = request.form['Title']
        d = request.form['Director']
        e = request.form['Cast']
        f = request.form['Country']
        g = request.form['Date_Added']
        h = request.form['Release_Year']
        i = request.form['Rating']
        j = request.form['Duration']
        k = request.form['Listed_In']
        l = request.form['Description']
        nam = Netflix(Show_ID = a, Type=b,Title = c, Director= d, Cast= e, Country=f,Date_Added = g, Release_Year=h,Rating=i,Duration= j,Listed_In = k,Description=l)
        db.session.add(nam)
        db.session.commit()
        

    allnet = Netflix.query.all()
    return render_template('index.html',allnet = allnet)
    

@app.route('/update/<int:sno>',methods = ['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        a = request.form['Show_ID']
        b = request.form['Type']
        c = request.form['Title']
        d = request.form['Director']
        e = request.form['Cast']
        f = request.form['Country']
        g = request.form['Date_Added']
        h = request.form['Release_Year']
        i = request.form['Rating']
        j = request.form['Duration']
        k = request.form['Listed_In']
        l = request.form['Description']
        naman = Netflix.query.filter_by(sno=sno).first()
        naman.Show_ID = a
        naman.Type = b
        naman.Title_ID = c
        naman.Director = d
        naman.Cast = e
        naman.Country = f
        naman.Date_Added = g
        naman.Release_Year = h
        naman.Rating = i
        naman.Duration = j
        
        naman.Listed_In = k
        naman.Description = l
        db.session.add(naman)
        db.session.commit()
        return redirect("/")

    naman = Netflix.query.filter_by(sno=sno).first()
    return render_template('update.html',naman = naman)

@app.route('/delete/<int:sno>')
def delete(sno):
    naman = Netflix.query.filter_by(sno=sno).first()
    db.session.delete(naman)
    db.session.commit()
    return redirect("/")

if __name__ =='__main__':
    app.run(debug=True, port=8000)