import sqlite3
import paho.mqtt.client as mqtt
import json
import time
# MQTT instellingen
mqtt_broker = "127.0.0.1"
mqtt_topic = "ESPdata"
mqtt_username = "matthijs"
mqtt_password = "matthijs"

# SQLite3 database instellingen
db_file = "Database.db"

# MQTT-client initialiseren
client = mqtt.Client()
# Callback-functie voor wanneer een bericht wordt ontvangen
def on_message(client, userdata, message):
    # Hier kun je de ontvangen gegevens verwerken
    payload = message.payload.decode("utf-8")

    ## !! ZET DE PRINT FUNCTIE HIERONDER AAN ALS JE WIL ZIEN WAT JE ONTVANGT !! ##
    #print(f"Ontvangen bericht: {payload}")
    ## !! ZET DE PRINT FUNCTIE HIERBOVEN AAN ALS JE WIL ZIEN WAT JE ONTVANGT !! ##

    msg = json.loads(payload)
    msg['temperature'] = msg['temperature'][:-1]
    msg['humidity'] = msg['humidity'][:-1]
    msg['pressure'] = msg['pressure'][:-3]

    
    # SQLite3-database openen en gegevens invoegen
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO metingen (temperature,humidity,pressure) VALUES (?,?,?)" , (msg['temperature'],msg['humidity'],msg['pressure']))
    conn.commit()
    conn.close()

# Callback-functie instellen
client.on_message = on_message

# Verbinding maken met de MQTT-broker
client.connect(mqtt_broker, 1883)

# Abonneren op het MQTT-onderwerp
client.subscribe(mqtt_topic)
time.sleep(0.5)

# Oneindige lus om te wachten op berichten
client.loop_forever()

