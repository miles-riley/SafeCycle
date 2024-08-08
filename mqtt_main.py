# python 3.6

import random
import time
from paho.mqtt import client as mqtt_client
import json

broker = 'localhost' #INPUT BROKER NAME
port = 1883
topic = "safecycle" #INPUT TOPIC NAME

# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'

username = '' #INPUT USERNAME
password = '' #INPUT PASSWORD


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(topic)
            print(f"Subscribed to topic: {topic}")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

#MANIPULATE THE FOLLOWING METHOD TO TURN THE LED ON OR OFF BASED ON THE MESSAGE RECIEVED
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.payload.decode() == "off":
            print("off")
        elif msg.payload.decode() == "on":
            print("on")
    client.subscribe(topic)
    client.on_message = on_message


def run(): 
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
