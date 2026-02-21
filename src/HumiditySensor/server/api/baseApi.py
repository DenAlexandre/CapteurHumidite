# api/baseApi.py
from time import sleep
import sys
import os
from flask import Flask, request, jsonify
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils.sqlUtility as sqlUtility

app = Flask(__name__)

@app.route('/get_sensor_data', methods=['GET'])
def get_sensors():
    try:
        pass
    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Gérer les erreurs de manière appropriée


@app.route('/set_sensorData', methods=['POST'])
def set_sensorData():
    try:
        data = request.get_json()
        datetimeData = (data.get('datetime'))
        temperatureData = (data.get('temperature'))
        humidityData = (data.get('humidity'))
        outputData = (data.get('output')) 
        sqlUtility.add_data(datetimeData,temperatureData,humidityData, outputData)
        return jsonify({'message':  'La data a été correctement écrite en base !'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Gérer les erreurs de manière appropriée


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002, debug=True)