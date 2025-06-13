from pydub.playback import play
from pydub import AudioSegment
import os
import escuchar_responder
import asyncio

# Volume state variables
volumeFactor = 100
lastVolume = 100  # Default to initial max volume

def confirmationSound():
    """Play confirmation sound safely"""
    confirm_volume()
    file_path = os.path.abspath("f1.mp3")

    if not os.path.exists(file_path):
        print(f"Error: Archivo '{file_path}' no encontrado.")
        return

    try:
        audio = AudioSegment.from_mp3(file_path)
        play(audio)
    except Exception as e:
        print(f"Error al reproducir sonido: {e}")

def volumeUp():
    """Increase volume by 5% (max 100%)"""
    global volumeFactor
    volumeFactor = min(volumeFactor + 5, 100)
    confirm_volume()

def volumeDown():
    """Decrease volume by 5% (min 0%)"""
    global volumeFactor
    volumeFactor = max(volumeFactor - 5, 0)
    confirm_volume()

def set_volume(newVolume):
    """Set volume safely with validation"""
    global volumeFactor
    try:
        newVolume = int(newVolume)
        if 0 <= newVolume <= 100:
            volumeFactor = newVolume
        else:
            print("Error: volumen fuera de rango (0-100).")
    except ValueError:
        print("Error: entrada no válida, ingrese un número.")
    
    confirm_volume()

def confirm_volume():
    """Apply volume level to system"""
    global volumeFactor
    try:
        os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volumeFactor}%")
    except Exception as e:
        print(f"Error al ajustar el volumen: {e}")

def mute():
    """Mute sound, saving previous volume"""
    global volumeFactor, lastVolume
    lastVolume = volumeFactor
    volumeFactor = 0
    confirm_volume()

def unmute():
    """Restore volume if previously muted"""
    global volumeFactor
    if volumeFactor == 0:
        volumeFactor = lastVolume
        confirm_volume()

def menuSonido():
    """Voice-controlled menu for sound settings"""
    teto = escuchar_responder.listen()
    if teto:
        match teto:
            case "subir volumen":
                volumeUp()
            case "bajar volumen":
                volumeDown()
            case "mutear":
                mute()
            case "desmutear":
                unmute()
            case "ajustar volumen":
                asyncio.run(escuchar_responder.speak("¿Qué nivel de volumen? (0-100)"))
                volumen = escuchar_responder.listen()
                set_volume(volumen)
            case _:
                asyncio.run(escuchar_responder.speak("No se ha entendido la orden."))

