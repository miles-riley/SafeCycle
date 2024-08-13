import random
import time
from paho.mqtt import client as mqtt_client
import json
import time
from rpi_ws281x import *
import cv2
import os
import asyncio
from picamera2 import *

# LED strip configuration:
LED_COUNT      = 10      # Number of LED pixels.
LED_PIN        = 10      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

broker = 'localhost' #INPUT BROKER NAME
port = 1883
topic = "safecycle"  #INPUT TOPIC NAME

users  = []
users.append(os.getlogin())
boxArea = 0

#This is to pull the information about what each object is called
classNames = []
classFile = "/home/safecycle/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")
    
configPath = "/home/safecycle/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/safecycle/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

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
        else:
            lightsOn(strip, Color(0, 0, 0))
             
    client.subscribe(topic)
    client.on_message = on_message
    
def publish(client,command):
    result = client.publish(topic, payload=command,qos=0,retain=False)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{command}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
        
def getObjects(img, thres, nms, client, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    
    if len(objects) == 0: 
        objects = classNames
    
    objectInfo = []
    
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects: 
                objectInfo.append([box, className])
                
                # Calculate the area of the bounding box
                x, y, w, h = box
                
                if(w >= 250 and className == 'car'):
                    publish(client, "carback")
                    
                
                if draw:
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, classNames[classId - 1].upper(), (x + 10, y + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence * 100, 2)), (x + 200, y + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
    
    return img, objectInfo

# Define functions which animate LEDs in various ways.  
async def run_video(client):
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()
    while True:
        # GET AN IMAGE from Pi camera
        img = picam2.capture_array("main")
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        img = cv2.flip(img, 0)
        
        result, objectInfo = getObjects(img,0.55,0.4, client, objects = ['car', 'bus', 'truck', 'motorcycle', 'bicycle', 'person'])
    
        cv2.imshow("Output",img)
            
        k = cv2.waitKey(1)
        if k == 27:    # Esc key to stop
            # EXIT
            picam2.stop()
            cv2.destroyAllWindows()
            break
        await asyncio.sleep(0)  # Yield control back to the event loop
    
async def run_mqtt(strip, client):
    subscribe(client, strip)
    client.loop_start()  # Use loop_start for non-blocking call
    while True:
        await asyncio.sleep(1)  # Keep the MQTT loop running in the background

async def main():
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    
    client = connect_mqtt()
    
    await asyncio.gather(
        run_mqtt(strip, client),
        run_video(client)
    )

if __name__ == '__main__':
    asyncio.run(main())