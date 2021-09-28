import sys
import _thread
from time import sleep

from pynput.keyboard import Key, Listener

import auth
import spotify

import Rpi.GPIO as GPIO

# establish client
# store credentials

#define callbacks

#like and add to playlist

def button_callback(channel):
    print('External button is pushed')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback)

#listen for key inputs

def show(key):
  
    print('\nYou Entered {0}'.format( key))
  
    if key == Key.enter:
        print('You Pressed Like button')

    if key == Key.esc:
        print('You Pressed Exit button')
        GPIO.cleanup()

        # Stop listener
        return False
  
# Collect all event until released
with Listener(on_press = show) as listener:   
    listener.join()