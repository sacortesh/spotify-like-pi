import sys
import _thread
from time import sleep

from pynput.keyboard import Key, Listener

import auth
import spotify

# import Rpi.GPIO as GPIO

# establish client
# store credentials

#define callbacks

#like and add to playlist

def button_callback(channel):
    print('External button is pushed')

    spotify_client = spotify.Client()

    playlist_found = False
    song_is_playing = False

    current_song = spotify_client.fetch_now_playing()
    playlist_found =  spotify_client.validate_playlist()

    if current_song == '-1':
        print('No song is playing')
        
    else:
        spotify_client.send_like(current_song)
        if playlist_found:
            spotify_client.persist_song(current_song)
        pass


# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(10,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

# GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback)

#listen for key inputs

def show(key):
  
    print('\nYou Entered {0}'.format( key))
  
    if key == Key.enter:
        print('You Pressed Like button')
        button_callback(True)

    if key == Key.esc:
        print('You Pressed Exit button')
        GPIO.cleanup()

        # Stop listener
        return False
  
# Collect all event until released
with Listener(on_press = show) as listener:   
    listener.join()