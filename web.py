from flask import Flask, render_template
import sqlite3
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import time
import os
from prediction import get_AI_prediction
app = Flask(__name__)

def getHistData(numSamples):
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM metingen ORDER BY timestamp DESC LIMIT "+str(numSamples))
    data = cursor.fetchall()
    date = []
    temperature = []
    humidity = []
    pressure = []
    timestamp = []
    
    for row in reversed(data):
        date.append(row[0])
        temperature.append(row[1])
        humidity.append(row[2])
        pressure.append(row[3])
        timestamp.append(row[4])
    return date, temperature, humidity, pressure, timestamp

def getpredictionData2(numSamples):
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM metingen ORDER BY timestamp DESC LIMIT "+str(numSamples))
    data = cursor.fetchall()
    conn.close()
    return data

def generate_unique_filename():
    timestamp = int(time.time()) 
    return f"plot_{timestamp}.png"

@app.route('/')
def display_current():
    conn = sqlite3.connect('Database.db')
    cursor = conn.cursor()
    # Verbind met de SQLite-database
    # Voer een query uit om temperatuurgegevens op te halen met de meest recente tijdstempel
    cursor.execute('SELECT * FROM "metingen" WHERE timestamp = (SELECT MAX(timestamp) FROM metingen);')
    datalatest = cursor.fetchall()
    if datalatest == []:
        datalatest = [[0,0,0]]
    # Sluit de databaseverbinding
    conn.close()
    plotname = generate_unique_filename()

    for filename in os.listdir('static'):
        if filename.endswith('.png'):
            os.remove(os.path.join('static', filename))
    historicdata = getHistData(10)
    prepare_plt(historicdata, 1, 'Temperatuur', 'red', 0, 40, 'Temperatuur °C', '°C',plotname)
    prepare_plt(historicdata, 2, 'Luchtvochtigheid', 'blue', 0, 100, 'Luchtvochtigheid %', '%','1_'+plotname)
    prepare_plt(historicdata, 3, 'Luchtdruk', 'green', 900, 1100, 'Luchtdruk hPa', 'hPa','2_'+plotname)
    Rainprediction = get_AI_prediction(1,getpredictionData2(1))
    return render_template('temperatuur.html',datalatest=datalatest, plot1='1_'+plotname,plot2='2_'+plotname,plots=plotname, Rainprediction=Rainprediction)

#functie om met de variabelen een grafiek te plotten
def prepare_plt(data, datanr, label, color, ymin, ymax, title, ylabel,outputname):
    plt.figure(figsize=(5, 3))
    plt.plot(data[4], data[datanr], label=label, color=color)
    plt.xlim(min(data[4]), max(data[4]))
    plt.xlabel('tijd')
    plt.xticks(rotation=30)
    plt.xticks(size=1)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.ylim(ymin, ymax)
    plt.grid(True)
    plt.legend()
    plt.savefig('static/'+outputname)  # Opslaan van de grafiek als een afbeeldingsbestand
    plt.close()

if __name__ == '__main__':
    # run the mqttscreener in a separate thread
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True,host='0.0.0.0',port=5000)

