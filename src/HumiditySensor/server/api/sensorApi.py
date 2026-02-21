# api/sensorApi.py
import time
from time import sleep
import requests
from flask import Flask, request, jsonify
import Adafruit_DHT as AdaFruit
import RPi.GPIO as GPIO
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils.fileUtility as fileUtility
import utils.sqlUtility as sqlUtility
from flask_cors import CORS

# ****************************************************************
# Constantes
# ****************************************************************
sensorPin = 4
url = "http://192.168.1.212?"
password = "123"
relayPin = 17
cons_humidity = 40
rounded_temp = 50.000000
rounded_hum = 50.000000

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = AdaFruit.DHT22
app = Flask(__name__)
# Active CORS pour toutes les routes de l'application
CORS(app)

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensorPin,  GPIO.IN)
GPIO.setup(relayPin, GPIO.OUT)


#********************************************************************************
# Définition des fonctions
#********************************************************************************
def PostCreateToken(sort):
	try:
		token = ""
		objects =  {"pass": password,
					"turn": sort };
		newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		x= requests.post(url, params=objects, headers=newHeaders);
		sleep(0.1)
		print('Sortie relais =' + sort + ' - code = ' + str(x.status_code))
		return token
	except Exception as exc:
		fileUtility.WriteFile("outputApi.log","L'envoi de la commande pour activer le relais a échoué!")


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


#********************************************************************************
# Définition des routes I/O
#********************************************************************************
@app.route('/reboot', methods=['POST'])
def reboot():
    try:
        os.system("sudo reboot")
    except Exception as e:
        fileUtility.WriteFile("sensorAPI.log","Le Reboot a échoué! " +  str(e))


     
#********************************************************************************
# Définition des routes I/O
#********************************************************************************
@app.route('/get_humidity', methods=['GET'])
def get_humidity():
    try:
        humidity, temperature = AdaFruit.read_retry(sensor, sensorPin)
        time.sleep(0.01)
        #Affiche hum et temp
        if humidity is not None and temperature is not None:
            rounded_temp = float(format(temperature, '.4f'))
            rounded_hum = float(format(humidity, '.4f'))
            print(f'Temp={rounded_temp:.4f}°C  Humidity={rounded_hum:.4f}')
        else:
            print('Failed to get reading. Try again!')

        return jsonify({
            'temperature': (rounded_temp),
            'humidity': (rounded_hum),
            })
    except Exception as e:
        fileUtility.WriteFile("sensorAPI.log","La demande des données a échoué!")
        return jsonify({'error': str(e)}), 400  # Gérer les erreurs de manière appropriée


@app.route('/set_outputRelayPin17', methods=['POST'])
def set_outputRelayPin17():
	try:
		data = request.get_json()  # Récupérer les données JSON du corps de la requête
		outputBln = (data.get('output'))  # Accéder à param1 dans les données JSON
		#outputBln = str2bool(request.args.get('output'))  # Récupérer le paramètre 'output' de l'URL
		print('outputBln  =' + str(outputBln))
		if str2bool(str(outputBln)) == True:
			GPIO.output(relayPin, GPIO.HIGH)
			time.sleep(0.01)
			PostCreateToken("OFF")
		else:
			GPIO.output(relayPin, GPIO.LOW)
			time.sleep(0.01)
			PostCreateToken("ON")
		return jsonify({'message':  'La sortie 17 est passé à l'' état ' + str(outputBln)})
	except Exception as e:
		fileUtility.WriteFile("sensorAPI.log","L'envoi de la commande pour activer le relais a échoué!")
		return jsonify({'error': str(e)}), 400  # Gérer les erreurs de manière appropriée


#********************************************************************************
# Définition des routes SQLLite
#********************************************************************************
@app.route('/get_config', methods=['GET'])
def get_config():
    try:
        data = request.get_json()
        #field = (data.get('field'))
        #print(field)
        rep = sqlUtility.get_config()
        return jsonify({'reponse': rep})
    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Gérer les erreurs de manière appropriée


@app.route('/set_config', methods=['POST'])
def set_config():
    try:
        data = request.get_json()
        field = (data.get('field'))
        value = (data.get('value'))
        sqlUtility.set_config(field,value)
        return jsonify({'message':  'La data a été correctement écrite en base !'})
    except Exception as e:
        fileUtility.WriteFile("sensorAPI.log","L'envoi de la commande pour activer le relais a échoué!")
        return jsonify({'error': str(e)}), 400  # Gérer les erreurs de manière appropriée




@app.route('/get_sensors_data', methods=['POST'])
def get_sensors_data():
    try:
        data = request.get_json()
        datetime1 = (data.get('datetime_start'))
        datetime2 = (data.get('datetime_end'))
        # rep = sqlUtility.get_data('2023-12-11 00:00:00','2023-12-11 10:00:00')
        rep = sqlUtility.get_sensor_data(datetime1,datetime2)
        return jsonify({'reponse': rep})

    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Gérer les erreurs de manière appropriée


@app.route('/add_sensor_data', methods=['POST'])
def add_sensor_data():
    try:
        data = request.get_json()
        datetimeData = (data.get('datetime'))
        temperatureData = (data.get('temperature'))
        humidityData = (data.get('humidity'))
        outputData = (data.get('output')) 
        sqlUtility.add_sensor_data(datetimeData,temperatureData,humidityData, outputData)
        return jsonify({'message':  'La data a été correctement écrite en base !'})
    except Exception as e:
        fileUtility.WriteFile("sensorAPI.log","L'envoi de la commande pour activer le relais a échoué!")
        return jsonify({'error': str(e)}), 400  # Gérer les erreurs de manière appropriée


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)