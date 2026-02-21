#!/usr/bin/python
import Adafruit_DHT
import RPi.GPIO as GPIO
import datetime
from time import sleep
import requests
from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp
import os
import socket
import struct

adrIP = ""
url = "http://192.168.1.212?"
adrMAC = "2c:f4:32:54:a2:87"
password = "123"
pin = 4 
relayPin = 17
cons_humidity = 65
delta = 0

def get_ip_by_mac(mac_address):
	# Créer un paquet ARP pour demander l'adresse IP correspondant à l'adresse MAC donnée
	arp = ARP(pdst='2c:f4:32:54:a2:87')
	ether = Ether(dst="ff:ff:ff:ff:ff:ff")
	packet = ether/arp

	# Envoyer le paquet sur le réseau local et attendre une réponse
	result = srp(packet, timeout=3, verbose=0)[0]
	print (str(result))
	# Extraire l'adresse IP de la réponse
	return result[0][1].psrc

def get_ip_address(mac_address):
	for host in socket.gethostbyname_ex(socket.gethostname())[2]:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.connect((host, 9))
			arp = struct.pack('Hs4s4s', 1, b'\x00'*6, socket.inet_aton(host), mac_address)
			s.sendall(arp)
			ip_address = s.recv(20).strip()[20:24]
			return socket.inet_ntoa(ip_address)
		except Exception as exc:
			#self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, str(exc))
			WriteFile(str(exc))

def getip(mac_address):
	print(mac_address)
	arp_result = os.popen("arp -a " + mac_address).read()
	print(arp_result)
	ip_address = arp_result.split(" ")[1]
	print(ip_address)
	return ip_address

def WriteFile(txt):
	fichier = open("data.txt", "a")
	fichier.write(txt)
	fichier.close()

#********************************************************************************   
# Permet de demander la clef pour les autres demande API
#********************************************************************************
def PostCreateToken(sort):
	try:
		token = ""
		#192.168.1.160?pass=123&turn=ON
		objects =  {"pass": password,
					"turn": sort };
		#objects.replace("'","")
		newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		x= requests.post(url, params=objects, headers=newHeaders);
		sleep(0.1)
		print('Sortie relais =' + str(x.status_code))
		#if (x.ok != sort):
			#raise Exception("La demande a provoqué une erreur !")
		return token
	except Exception as exc:
		#self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, str(exc))
		WriteFile("L'envoi de la commande pour activer le relais a échoué!")


# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT22

# Example using a Beaglebone Black with DHT sensor
# connected to pin P8_11.#pin = 'P8_11'

# Example using a Raspberry Pi with DHT sensor
# connected to GPIO23.


GPIO.setmode(GPIO.BCM)
GPIO.setup(relayPin, GPIO.OUT)

dt_old = datetime.datetime.today().replace(microsecond=0)
first = True
humidity_old = 90
rounded_temp = 50.000000
rounded_hum = 50.000000
#adrIP = get_ip_by_mac(adrMAC)
ipaddress = get_ip_address(adrMAC)
print(ipaddress)

while True:



	dt = datetime.datetime.today().replace(microsecond=0)
	if (dt_old.minute != dt.minute) or (first):

		dt_old = dt
		# Try to grab a sensor reading.  Use the read_retry method which will retry up
		# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
		humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
		sleep(0.01)
		#Affiche hum et temp
		if humidity is not None and temperature is not None:
			rounded_temp = float(format(temperature, '.4f'))
			rounded_hum = float(format(humidity, '.4f'))
			print(f'Temp={rounded_temp:.4f}°C  Humidity={rounded_hum:.4f}')            
		else:
			print('Failed to get reading. Try again!')

		#Permet de faire un hysteresis
		if rounded_hum > humidity_old:
			consigne = cons_humidity + delta
		else:
			consigne = cons_humidity - delta

		#Permet le déclenchement du relais
		if rounded_hum > consigne:
			GPIO.output(relayPin, GPIO.HIGH)
			PostCreateToken("OFF")
			sortie = "True"
		else:
			GPIO.output(relayPin, GPIO.LOW)
			PostCreateToken("ON")
			sortie = "False"

		print(f'Temp={rounded_temp}°C  Humidity={rounded_hum} Consigne={consigne} Sortie={sortie}')
		txt = str(dt) + ";" + str(rounded_temp) + ";" + str(rounded_hum) + ";" + sortie + "\n"
		WriteFile(txt)

		humidity_old = rounded_hum
		if first:
			first = False

		sleep(1)
		
		

