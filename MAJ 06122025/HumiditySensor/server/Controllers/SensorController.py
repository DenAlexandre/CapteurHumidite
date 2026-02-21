import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import const
from datetime import datetime
import Controllers.LoggerController as LoggerController
import Controllers.FileController as FileController
import requests
from random import random
from threading import Thread
from threading import Lock
from time import sleep
import os
import utils.fileUtility as fileUtility
import subprocess


class SensorController:

    def __new__(self):
        print("Creating instance SensorController")
        return super(SensorController, self).__new__(self)

    def __init__(self):
        try:
            self.loggerCtrl = LoggerController.LoggerController(self)
            self.FileCtrl = FileController.FileController(self)
            # create a shared lock
            self.lock = Lock()
            self.urlAPI = "http://raspberrypizero:3000"
            self.consigne = 50
            self.humidity_old = 90
            self.sortie = "True"
            self.mode_manual = 0
            self.dt_old = datetime.today().replace(microsecond=0)
            self.first = True
            self.humidity_old = 90
            self.rounded_temp = 50.000000
            self.rounded_hum = 50.000000
            # start a thread
            #Thread(target=task, args=(self.lock, 1, random())).start()
            print("Exiting Init Main Thread")
            
        except Exception as exc:
            self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, "SensorController - __init__ : " + str(exc))



    def get_humidity(self):
        try:
            self.lock.acquire()
            url = self.urlAPI + "/get_humidity"
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
        
        except Exception as exc:
            self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, "SensorController - get_humidity : " + str(exc))

        finally:
            self.lock.release()
            return response.json()



    def get_config_value(self):
        try:
            self.lock.acquire()
            url = self.urlAPI + "/get_config"
            # Faire une requête GET à l'API
            #myobj = ({   "field":"cons_hum"    })
            # Faire une requête GET à l'API
            #response = requests.get(url, json = myobj)
            response = requests.get(url)
            # Vérifier si la requête a réussi (code d'état 200)
            if response.status_code == 200:
                # Afficher la réponse JSON
                rep = response.json()
            else:
                # Afficher un message d'erreur si la requête a échoué
                print(f"Erreur de requête : {response.status_code}")

        except Exception as exc:
            self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, "SensorController - get_config_value : " + str(exc))
        finally:
            self.lock.release()
            return response.json()

    def str2bool(self,v):
        return v.lower() in ("yes", "true", "t", "1")


    def set_outputRelay(self,blnOutput):
        try:
            url = self.urlAPI + "/set_outputRelayPin17"

            # Faire une requête GET à l'API
            bln = self.str2bool(str(blnOutput))
            myobj = {'output': str(bln)}
            response = requests.post(url, json = myobj)

            # Vérifier si la requête a réussi (code d'état 200)
            if response.status_code == 200:
                # Afficher la réponse JSON
                print(response.json())
                
            else:
                # Afficher un message d'erreur si la requête a échoué
                print(f"Erreur de requête : {response.status_code}")
        except Exception as exc:
            self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, "SensorController - set_outputRelay : " + str(exc))
        finally:
            return response

    def add_sensor_data(self, datetime1, temperature1, humidity1, output1):
        try:
            url = self.urlAPI + "/add_sensor_data"

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
        except Exception as exc:
            self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, "SensorController - add_sensor_data : " + str(exc))
        finally:
            return response

    def StartProcess(self):
        try:
            command1 = './startSensorApi.sh'
            subprocess.Popen(command1, shell=True)
            print("execution de l'API Sensor")

        except Exception as exc:
            self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, "SensorController - StartProcess : " + str(exc))


    def run_app(self):
        try:
            print("Test sensorController")
            global humidity_value
            self.StartProcess()
            sleep(15)
            self.first = True
            while True:
                try:
                    dt = datetime.today().replace(microsecond=0)
                    #self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Info, "SensorController - run_app : " + "dt_minute:" + str(dt.minute) + "dt_old_minute:" + str(self.dt_old.minute))
                    if (self.dt_old.minute != dt.minute) or (self.first):
                        if self.first == True:
                                self.first = False
                        #self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Info, "SensorController - run_app : " + str("Demarrage de la boucle"))
                        self.dt_old = dt
                        rep_config = self.get_config_value()
                        self.consigne = rep_config['reponse'][0][2]
                        self.mode_manual = rep_config['reponse'][1][2]
                        sleep(1)
                        if (self.mode_manual == '0'):
                            data = self.get_humidity()

                            if 'humidity' in data:
                                humidity_value = data['humidity']
                            if 'temperature' in data:
                                temperature_value = data['temperature']
                            #print(f'Temp={self.rounded_temp}°C  Humidity={rounded_hum} Consigne={consigne} Sortie={sortie}')
                            if humidity_value is not None and temperature_value is not None:
                                self.rounded_temp = float(format(temperature_value, '.4f'))
                                self.rounded_hum = float(format(humidity_value, '.4f'))
                                print(f'Temp={self.rounded_temp:.4f}°C Humidity={self.rounded_hum:.4f}')
                                #Permet le déclenchement du relais
                                if self.rounded_hum > float(self.consigne):
                                    sortie = True
                                else:
                                    sortie = False
                                test = self.set_outputRelay(sortie)
                                print(f'Temp={self.rounded_temp}°C  Humidity={self.rounded_hum} Consigne={self.consigne} Sortie={str(sortie)}')
                                txt = str(dt) + ";" + str(self.rounded_temp) + ";" + str(self.rounded_hum) + ";" + str(sortie) 
                                fileUtility.WriteFile("data.txt",txt)
                                self.add_sensor_data(str(dt),self.rounded_temp,self.rounded_hum,str(sortie))
                            else:
                                print('Failed to get reading. Try again!')
                                fileUtility.WriteFile("data.txt",txt)

                            self.humidity_old = self.rounded_hum

                    sleep(1)
                except Exception as exc:
                    self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, "SensorController - run_app - while : " + str(exc))

        except Exception as exc:
            self.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, "SensorController - run_app : " + str(exc))
