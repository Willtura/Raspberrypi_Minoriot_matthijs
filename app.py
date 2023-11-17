#!/bin/python3
import argparse
import config

# Parse arguments before anything for faster feedback
parser = argparse.ArgumentParser()
parser.add_argument("connection", nargs='?', help="Device Connection String from Azure", 
                    default=config.IOTHUB_DEVICE_CONNECTION_STRING)
parser.add_argument("-s", "--simulated", action="store_true", default=config.SIMULATED_DATA,
                    help="Simulates temperature and humidity data from the BME280 with random values")
parser.add_argument("-t", "--time", type=int, default=config.MESSAGE_TIMESPAN,
                    help="Time in between messages sent to IoT Hub, in milliseconds (default: 2000ms)")
parser.add_argument("-n", "--no-send", action="store_true", 
                    help="Disable sending data to IoTHub, only print to console")

ARGS = parser.parse_args()

from azure.iot.device import IoTHubDeviceClient
from azure.iot.device.exceptions import ConnectionFailedError, ConnectionDroppedError, OperationTimeout, OperationCancelled, NoConnectionError
from azure.iot.device import Message
from log import console, log
from dotenv import load_dotenv
import json
import time
import sqlite3
import datetime

load_dotenv()



def send_message(device_client: IoTHubDeviceClient, message):
    telemetry = Message(json.dumps(message))
    telemetry.content_encoding = "utf-8"
    telemetry.content_type = "application/json"
    try:
        device_client.send_message(telemetry)
    except (ConnectionFailedError, ConnectionDroppedError, OperationTimeout, OperationCancelled, NoConnectionError):
        log.warning("Message failed to send, skipping")
    else:
        log.success("Message successfully sent!", message)

def main():
    if not ARGS.connection and not ARGS.no_send:  # If no argument
        log.error("IOTHUB_DEVICE_CONNECTION_STRING in config.py variable or argument not found, try supplying one as an argument or setting it in config.py")
    
    if not ARGS.no_send:
        with console.status("Connecting to IoT Hub with Connection String", spinner="arc", spinner_style="blue"):
            # Create instance of the device client using the connection string
            device_client = IoTHubDeviceClient.create_from_connection_string(ARGS.connection, connection_retry=False)

            # Connect the device client.
            device_client.connect()
        log.success("Connected to IoT Hub")

    print()  # Blank line

    try:
        while True:
            #get the data from the database
            conn = sqlite3.connect('Database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM "metingen" WHERE timestamp = (SELECT MAX(timestamp) FROM metingen) ORDER BY ID DESC LIMIT 1')
        
            data = cursor.fetchall()
            conn.close()
            #print(data)
            if data == []:
                ARGS.no_send = True
            if data[0][5] == 1:
                ARGS.no_send = True
            else:
                ARGS.no_send = False
            
            message = {
                "deviceId" : 1,
                "rasptimestamp" : data[0][4],
                "temperature": data[0][1],
                "humidity": data[0][2],
                "pressure": data[0][3]	
            }
            # Send BME280 sensor data to Azure IoTHub
            if ARGS.no_send:
                log.warning("Not sending to IoTHub", message)
            else:
                with console.status("Sending message to IoTHub...", spinner="bouncingBar"):
                    send_message(device_client, message)
                    conn = sqlite3.connect('Database.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE metingen SET datasent = 1 WHERE ID = ?", (data[0][0],))
                    conn.commit()
                    conn.close()
            # Wait for interval
            with console.status(f"Waiting {ARGS.time}ms...", spinner_style="blue"):
                time.sleep(ARGS.time / 1000)

    except KeyboardInterrupt:
        # Shut down the device client when Ctrl+C is pressed
        log.error("Shutting down", exit_after=False)
        device_client.shutdown()


if __name__ == "__main__":
    main()
