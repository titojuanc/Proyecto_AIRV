from pydub.playback import play
from pydub import AudioSegment
import os
volumeFactor=100
lastVolume=0


def confirmationSound():
    confirm_volume()
    audio=AudioSegment.from_mp3("f1.mp3")
    play(audio)

def volumeUp():
    """sube el volumen en 5"""
    global volumeFactor
    volumeFactor+=5
    confirm_volume()
    
def set_volume(newVolume):
    global volumeFactor
    volumeFactor=newVolume
    confirm_volume()



def volumeDown():
    """baja el volumen en 5"""
    global volumeFactor
    volumeFactor-=5
    confirm_volume()


def confirm_volume():
    global volumeFactor
    if(volumeFactor>100):
        volumeFactor=100
        print("nuh uh")
    elif(volumeFactor<0):
        print("nuh uh")
        volumeFactor=0
    os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volumeFactor}%")


def mute():
    global volumeFactor
    global lastVolume
    lastVolume=volumeFactor
    volumeFactor=0
    

def unmute():
    global volumeFactor
    if volumeFactor==0:
        volumeFactor=lastVolume

