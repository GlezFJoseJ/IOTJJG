import requests
from db_storage import DBStorage
import flask
import flask_cors
import threading
import time
import datetime

# URL del servidor
url = "http://192.168.185.110"

actual_luminosity = 0

# Función para obtener la luminosidad
def save_luminosity():
    global actual_luminosity 
    # Se obtiene la respuesta del servidor
    response = requests.get(url + "/luminosity")

    luminosity = response.text

    print("Luminosity: " + luminosity)

    actual_luminosity = luminosity 

    db = DBStorage()
    db.connect()
    db.insert(luminosity)
    db.disconnect()

def update_luminity():
    global actual_luminosity 
    # Se obtiene la respuesta del servidor
    response = requests.get(url + "/luminosity")

    luminosity = response.text

    print("Luminosity: " + luminosity)

    actual_luminosity = luminosity 
    
def timer_save():
    while True:
        save_luminosity()
        time.sleep(30)

def timer_update():
    while True:
        update_luminity()
        time.sleep(1)

# Iniciar el servidor
app = flask.Flask(__name__)

# Configurar CORS para permitir acceso por otros dominios a todas las rutas

cors = flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

# Ruta para retornar la luminosidad
@app.route('/luminosity', methods=['GET'])
def get_luminosity():
    global actual_luminosity
    return {'luminity': actual_luminosity}

# Ruta para obtener la luminosidad de la ultima hora
@app.route('/luminosity_last_hour', methods=['GET'])
def get_luminosity_last_hour():
    db = DBStorage()
    db.connect()
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(hours=1)
    luminosity = db.get_measurements_by_time(start_date, end_date)
    print(luminosity)
    db.disconnect()
    return luminosity

if __name__ == '__main__':
    # Obtner la luminosidad cada 3 segundos
    t = threading.Thread(target=timer_save)
    t2 = threading.Thread(target=timer_update)
    t.start()
    t2.start()
    # Iniciar el servidor
    app.run(host='0.0.0.0', port=5000)

