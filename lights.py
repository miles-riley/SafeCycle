#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

# import keyboard
import time
from rpi_ws281x import *
# import argparseq

# LED strip configuration:
LED_COUNT      = 10      # Number of LED pixels.
LED_PIN        = 18    # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN_R        = 10    # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 255      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53



# Define functions which animate LEDs in various ways.
def colorWipeR(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        #if i > 1:
        #   strip.setPixelColor(i - 1, (0,0,0))
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
    # strip.show()
    
def lightsOn(strip, color,):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()


def colorWipeL(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels())[::-1]:
        #if i > 1:
        #   strip.setPixelColor(i - 1, (0,0,0))
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

#Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    userInput = ''
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print ('Press Ctrl-C to quit.')
#     if not args.clear:
#         print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
            userInput = input(">")
            if userInput == "e":
                for i in range(0,3):
                    colorWipeR(strip, Color(255, 255, 255))  # Red wipe
                    time.sleep(0.01)
                    colorWipeR(strip, Color(0, 0, 0))
                
            if userInput == "q":
                for i in range(0,3):
                    colorWipeL(strip, Color(255, 255, 255))  # Red wipe
                    time.sleep(0.01)
                    colorWipeL(strip, Color(0, 0, 0))
                
            if userInput == 'r':
                while True:
                    lightsOn(strip, Color(255, 255, 255))
                    time.sleep(1.0)
                    lightsOn(strip, Color(0,0,0))
                    time.sleep(1.0)
                
            if userInput == 'f':
                lightsOn(strip, Color(255, 0, 0))

    except KeyboardInterrupt:
#         if args.clear:
            colorWipeR(strip, Color(0,0,0), 10)
