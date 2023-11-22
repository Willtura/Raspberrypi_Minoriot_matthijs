import urllib.request
import json
import os
import ssl
from datetime import datetime

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

def get_AI_prediction(aantal,Sensordata):

    data_values = [list(row) for row in Sensordata]
    for i in range(aantal):
        timestamp = data_values[i][4]
        datetime_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        date_format = datetime_object.strftime('%Y%m%d')  # Geeft '20231117'
        time_format = datetime_object.strftime('%H%M')   # Geeft '1030'
        DD_format = datetime_object.strftime('%d')
        data_values[i][5] = data_values[i][4].split(" ")
        data_values[i][4] = data_values[i][5].pop(1)
        data_values[i][5] = data_values[i][5][0][0:-1]
        data_values[i][0] = DD_format
        data_values[i][4] = time_format
        data_values[i][5] = date_format


    print(data_values)
    index1 = [0]
    data =  {
    "input_data": {
        "columns": [
        "DD",
        "T",
        "U",
        "P",
        "HH",
        "YYYYMMDD"
        ],
        #fill index [] with the amount of rows in Sensordata
        "index": index1,
        "data": data_values
    }
    }

    body = str.encode(json.dumps(data))

    url = 'https://matthijsmachinelearning-azowk.westeurope.inference.ml.azure.com/score'
    # Replace this with the primary/secondary key or AMLToken for the endpoint
    api_key = ''
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    # The azureml-model-deployment header will force the request to go to a specific deployment.
    # Remove this header to have the request observe the endpoint traffic rules
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'rain-prediction-model-1' }

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))
    return result
    