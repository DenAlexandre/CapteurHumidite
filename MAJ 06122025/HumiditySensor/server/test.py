import subprocess
import time
from time import sleep
import requests

urlAPI = "http://raspberrypizero:3000"
command1 = './startSensorApi.sh'
#subprocess.Popen(command1, shell=True)
print("execution de l'API Sensor")

datetime= "2023/04/11 08:09:00"
temperature = 28.7
humidity = 45.0
output= "False"


def set_sensorData(datetime1, temperature1, humidity1, output1):
	url = urlAPI + "/set_sensorData"

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
		print(response.json(['reponse']))
		
	else:
		# Afficher un message d'erreur si la requête a échoué
		print(f"Erreur de requête : {response.status_code}")

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

sleep(1)
while True:
	#get_config_value()
	set_sensorData(datetime,temperature,humidity,str(output))
	sleep(10)