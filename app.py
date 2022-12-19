from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import sys
import text_to_plot as tp
import shutil, os
import matplotlib
 
app = Flask(__name__)


UPLOAD_FOLDER = 'static/uploads/'
 
#delete
d = "/*Description: The dataframe “df” only contains the following columns: country, continent, year, life expectancy (lifeExp), population (pop), GDP per capita (gdpPercap), the ISO alpha, the ISO numerical*/"
p = "/*Prompt: The life expectancy in Oceania countries throughout the years.*/"
c = "df.query(\"continent == 'Oceania'\").plot(kind = 'line', x='year', y='lifeExp, c='country') <STOP>"
p2 = "/*Prompt: Gross Domestic Product per person over time in Europe/*"
c2 = "df.query(\"continent == 'Europe'\").plot(kind = 'line', x='year', y='gdpPercap) <STOP>"

qwerty = d + p + c + p2 + c2
#delete 

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = {'csv'}
 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

TP = tp.Text_to_Plot(qwerty)
data = {"Description": "", "QC": []} 

@app.route('/')
def home():
    data = {"Description": "", "QC": []} 
    shutil.copy("static/images/initial.png", "static/plot/plot.png")
    return render_template('plot.html', data=data)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.form["btn"]=="Submit":
        if 'file' not in request.files:
            shutil.copy("static/images/error.png", "static/plot/plot.png")
        file = request.files['file']
        if file.filename == '':
            shutil.copy("static/images/error.png", "static/plot/plot.png")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "df.csv"))
            try:
                description = TP.get_csv(os.path.join(app.config['UPLOAD_FOLDER'], "df.csv"))
                data["Description"] = description
                data["QC"] = []
                shutil.copy("static/images/loading.png", "static/plot/plot.png")
            except:
                shutil.copy("static/images/error.png", "static/plot/plot.png")
        else:
            shutil.copy("static/images/error.png", "static/plot/plot.png")
    elif request.form["btn"] == "Done":
        if 'prompt' not in request.form:
            shutil.copy("static/images/error.png", "static/plot/plot.png")
        prompt = request.form["prompt"]
        if prompt == "Delete memory":
            TP.delete_memory()
            data["QC"] = []
            shutil.copy("static/images/loading.png", "static/plot/plot.png")
        else:
            try:
                query, code = TP.text_to_plot(prompt, os.path.join(app.config['UPLOAD_FOLDER'], "figure.png"))
                data["QC"].append({"Query": query, "Code": code})
                shutil.copy(os.path.join(app.config['UPLOAD_FOLDER'], "figure.png"), "static/plot/plot.png")
            except:
                shutil.copy("static/images/error.png", "static/plot/plot.png")
    return render_template('plot.html', data=data)




