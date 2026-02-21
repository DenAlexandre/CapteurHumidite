import sqlite3
from time import sleep
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def get_sensor_data(datetime1, datetime2):
    try:
        conn = sqlite3.connect("/home/pi/partage/HumiditySensor/server/bdd/datasensor.db")
        cursor = conn.cursor()
        #query="SELECT id, datetime, temperature, humidity, output FROM datasensor where datetime between Datetime(?) and Datetime(?)"
        query = "SELECT id, datetime as dt, temperature, humidity, output, CAST(strftime('%M',datetime) as integer) as min FROM datasensor where (dt > DATETIME('now','-2 day')) and min % 5 == 0"
        #cursor.execute(query, (datetime1,datetime2))
        cursor.execute(query)
        db_record = cursor.fetchall()
        conn.close()
        return 'Sucess', (db_record)
    except sqlite3.OperationalError as eoe:
        print("Erreur SQL" + str(eoe))
    except Exception as e:
        print("Erreur générale" + str(e))

        

def add_sensor_data(datetime1, temperature1, humidity1, output1):
    try:
        conn = sqlite3.connect("/home/pi/partage/HumiditySensor/server/bdd/datasensor.db")
        cursor = conn.cursor()
        query="INSERT INTO datasensor(datetime, temperature, humidity, output) VALUES(?,?,?,?)"
        cursor.execute(query, (str(datetime1),temperature1,humidity1,str(output1)))
        #cursor.execute(query, ('2023/04/11 08:09:00',24.7,45.0,'False'))
        conn.commit()
        print('add_sensor_data OK')
    except sqlite3.OperationalError as eoe:
        print('Erreur la ligne existe déjà : ' + str(eoe))
    except Exception as e:
        print("Erreur" + str(e))
        conn.rollback()
        # raise e
    finally:
        conn.close()


def get_config():
    try:
        conn = sqlite3.connect("/home/pi/partage/HumiditySensor/server/bdd/datasensor.db")
        cursor = conn.cursor()
        #query="SELECT id_config, field, value FROM config where field = '" + field1 + "';"
        query="SELECT id_config, field, value FROM config;"
        print(query)
        cursor.execute(query)
        db_record = cursor.fetchall()
        conn.close()
        return db_record
    except sqlite3.OperationalError as eoe:
        print("Erreur SQL : " + str(eoe))
    except Exception as e:
        print("Erreur générale : " + str(e))



def set_config(field1, value1):
    try:
        conn = sqlite3.connect("/home/pi/partage/HumiditySensor/server/bdd/datasensor.db")
        cursor = conn.cursor()
        query="UPDATE config SET value='"+ value1 + "' where field = '" + field1 + "';"
        cursor.execute(query)
        conn.commit()
    except sqlite3.OperationalError as eoe:
        print('Erreur la ligne existe déjà : ' + str(eoe))
    except Exception as e:
        print("Erreur" + str(e))
        conn.rollback()
        # raise e
    finally:
        conn.close()
        print('set_config OK')        