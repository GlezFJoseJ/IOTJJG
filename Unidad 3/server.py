# python 3.6

import json
import logging
import random
import time
import datetime
from db_storage import DBStorage
import requests
from paho.mqtt import client as mqtt_client
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")

BROKER = 'ue91a21d.ala.us-east-1.emqxsl.com'
PORT = 8883
SUB_TOPIC = "monitores/#"
TOPIC = "monitores/server"
# generate client ID with pub prefix randomly
CLIENT_ID = f'python-mqtt-tls-pub-sub-{random.randint(0, 1000)}'
USERNAME = 'mqtt'
PASSWORD = 'password'

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = True


def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print("Connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
    else:
        print(f'Failed to connect, return code {rc}')


def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...",
                 reconnect_count)
    global FLAG_EXIT
    FLAG_EXIT = True


def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    
    try:
        message = msg.payload.decode()

        # decode json string to python dict
        try:
            msg_dict = json.loads(message)
        except json.decoder.JSONDecodeError:
            return

        # check if message is for me
        if msg_dict['to'] != "server":
            print("server")
            return

        # check if message has "action" key
        if "action" not in msg_dict:
            print("action")
            return

        if msg_dict["action"] == "SEND_DATA":
            # verify if message has "data" key
            if "data" not in msg_dict:
                print("no data")
                return

            # verify if data is a dict
            if not isinstance(msg_dict["data"], dict):
                print("no instance")
                return

            # verify if data has "temperature" and "humidity" keys
            if "temperature" not in msg_dict["data"] or "humidity" not in msg_dict["data"]:
                print("no values")

                return

            # TODO store data in database
            print("Storing data in database...")
            print("Temperatura", msg_dict["data"]["temperature"])
            print("Humedad", msg_dict["data"]["humidity"])
            db = DBStorage()
            db.connect()
            db.create_table()
            db.insert(msg_dict["data"]["humidity"],
                      msg_dict["data"]["temperature"])
            print("Data stored in database owo")
            db.disconnect()
            
        elif msg_dict["action"] == "GET_DATA":
            print("Getting data from server")
            db = DBStorage()
            db.connect()
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(hours=1)
            data = db.get_measurements_by_time(start_date, end_date)
            db.disconnect()
            print("Data retreived from database")

            msg_dict = {"from": "server", "to": "web","action" : "SEND_DATA", "data": data}
            out_msg = json.dumps(msg_dict)
            client.publish(msg.topic, out_msg)
        
        elif msg_dict["action"] == "GET_JOKE":
            url = "https://daddyjokes.p.rapidapi.com/random"

            headers = {
                "X-RapidAPI-Key": API_KEY,
                "X-RapidAPI-Host": "daddyjokes.p.rapidapi.com"
            }

            response = requests.get(url, headers=headers).json()


            print(response)

            data = { "joke": response["joke"] }

            msg_dict = {"from": "server", "to": "web","action" : "SEND_JOKE", "data": data}
            out_msg = json.dumps(msg_dict)
            client.publish(msg.topic, out_msg)

    except Exception as e:
        print(e)


def connect_mqtt():
    client = mqtt_client.Client(CLIENT_ID)
    client.tls_set(ca_certs='./emqxsl-ca.crt')
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=120)
    client.on_disconnect = on_disconnect
    return client


def publish(client):
    msg_count = 0
    while not FLAG_EXIT:
        msg_dict = {'msg': msg_count, 'from': 'server', 'to': 'client'}
        msg = json.dumps(msg_dict)
        if not client.is_connected():
            logging.error("publish: MQTT client is not connected!")
            time.sleep(1)
            continue
        result = client.publish(TOPIC, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            # print(f'Send `{msg}` to topic `{TOPIC}`')
            pass
        else:
            print(f'Failed to send message to topic {TOPIC}')
        msg_count += 1
        time.sleep(1)


def run():
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)
    client = connect_mqtt()
    client.loop_start()
    time.sleep(1)
    if client.is_connected():
        publish(client)
    else:
        client.loop_stop()


if __name__ == '__main__':
    run()
    while True:
        pass
