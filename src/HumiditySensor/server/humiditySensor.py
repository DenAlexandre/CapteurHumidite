#!/usr/bin/python
import datetime
from time import sleep
import os
import socket
import struct
import requests
import utils.fileUtility as fileUtility
import subprocess
from threading import Thread

urlAPI = "http://raspberrypizero:3000"
consigne = 50
humidity_old = 90
sortie = "True"
dt_old = datetime.datetime.today().replace(microsecond=0)
first = True
humidity_old = 90
rounded_temp = 50.000000
rounded_hum = 50.000000

def get_humidity():
	url = urlAPI + "/get_humidity"

	# Faire une requête GET à l'API
	response = requests.get(url)
	print("demande de l'API Sensor")
	# Vérifier si la requête a réussi (code d'état 200)
	if response.status_code == 200:
		# Afficher la réponse JSON
		print(response.json())
		
	else:
		# Afficher un message d'erreur si la requête a échoué
		print(f"Erreur de requête : {response.status_code}")
	return response.json()


def get_config_value():
	consigne = 50
	url = urlAPI + "/get_config"
	# Faire une requête GET à l'API
	myobj = ({
			"field":"cons_hum"
			})
	# Faire une requête GET à l'API
	response = requests.get(url, json = myobj)
	# Vérifier si la requête a réussi (code d'état 200)
	if response.status_code == 200:
		# Afficher la réponse JSON
		rep = response.json()
		consigne = (rep['reponse'][0][2])
		
	else:
		# Afficher un message d'erreur si la requête a échoué
		print(f"Erreur de requête : {response.status_code}")
	return consigne

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def set_outputRelay(blnOutput):
	url = urlAPI + "/set_outputRelayPin17"

	# Faire une requête GET à l'API
	bln = str2bool(str(blnOutput))
	myobj = {'output': str(bln)}
	response = requests.post(url, json = myobj)

	# Vérifier si la requête a réussi (code d'état 200)
	if response.status_code == 200:
		# Afficher la réponse JSON
		print(response.json())
		
	else:
		# Afficher un message d'erreur si la requête a échoué
		print(f"Erreur de requête : {response.status_code}")


def add_sensor_data(datetime1, temperature1, humidity1, output1):
	url = urlAPI + "/add_sensor_data"

	# Faire une requête GET à l'API
	myobj = ({
				"datetime": datetime1,
				"temperature" : temperature1,
				"humidity" : humidity1,
				"output": output1
            })
	response = requests.post(url, json = myobj)

	# Vérifier si la requête a réussi (code d'état 200)
	if response.status_code == 200:
		# Afficher la réponse JSON
		print(response.json())
		
	else:
		# Afficher un message d'erreur si la requête a échoué
		print(f"Erreur de requête : {response.status_code}")

def StartProcess():
	try:
		command1 = './startSensorApi.sh'
		subprocess.Popen(command1, shell=True)
		print("execution de l'API Sensor")

	except Exception as exc:
		fileUtility.WriteFile("humidity.log","L'éxécution des tache a échoué !" + str(exc) + "\n")


StartProcess()
sleep(10)
first = True
while True:
	dt = datetime.datetime.today().replace(microsecond=0)
	if (dt_old.minute != dt.minute) or (first):
		dt_old = dt
		global humidity_value
		data = get_humidity()
		consigne = get_config_value()

		if 'humidity' in data:
			humidity_value = data['humidity']
		if 'temperature' in data:
			temperature_value = data['temperature']
		

		#print(f'Temp={rounded_temp}°C  Humidity={rounded_hum} Consigne={consigne} Sortie={sortie}')

		if humidity_value is not None and temperature_value is not None:
			rounded_temp = float(format(temperature_value, '.4f'))
			rounded_hum = float(format(humidity_value, '.4f'))
			print(f'Temp={rounded_temp:.4f}°C Humidity={rounded_hum:.4f}')


			#Permet le déclenchement du relais
			if rounded_hum > float(consigne):
				sortie = True
			else:
				sortie = False

			test = set_outputRelay(sortie)
			print(f'Temp={rounded_temp}°C  Humidity={rounded_hum} Consigne={consigne} Sortie={str(sortie)}')
			txt = str(dt) + ";" + str(rounded_temp) + ";" + str(rounded_hum) + ";" + str(sortie) 
			fileUtility.WriteFile("data.txt",txt)
			add_sensor_data(str(dt),rounded_temp,rounded_hum,str(sortie))


		else:
			print('Failed to get reading. Try again!')
			fileUtility.WriteFile("data.txt",txt)

	humidity_old = rounded_hum
		
	if first == True:
			first = False

	sleep(1)