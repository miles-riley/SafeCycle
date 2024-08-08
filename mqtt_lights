# python 3.6

import random
import time
from paho.mqtt import client as mqtt_client
import json
import time
from rpi_ws281x import *

# LED strip configuration:
LED_COUNT      = 10      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

broker = 'localhost' #INPUT BROKER NAME
port = 1883
topic = "safecycle"  #INPUT TOPIC NAME

# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'

username = '' #INPUT USERNAME
password = '' #INPUT PASSWORD

def colorWipeR(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
    
def lightsOn(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()


def colorWipeL(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels())[::-1]:
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


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
def subscribe(client: mqtt_client, strip):
    def on_message(client, userdata, msg,):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.payload.decode() == "left":
            for i in range(0,3):
                colorWipeL(strip, Color(255, 255, 255))  # Red wipe
                time.sleep(0.01)
                colorWipeL(strip, Color(0, 0, 0))
        elif msg.payload.decode() == "on":
            colorWipeR(strip, Color(0,0,0), 10)
        elif msg.payload.decode() == "stop":
            lightsOn(strip, Color(255, 0, 0))
        elif msg.payload.decode() == "right":
            for i in range(0,3):
                colorWipeR(strip, Color(255, 255, 255))  # Red wipe
                time.sleep(0.01)
                colorWipeR(strip, Color(0, 0, 0))
    client.subscribe(topic)
    client.on_message = on_message

# Define functions which animate LEDs in various ways.  
def run():
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    client = connect_mqtt()
    subscribe(client, strip)
    client.loop_forever()
                     
if __name__ == '__main__':
    run()

