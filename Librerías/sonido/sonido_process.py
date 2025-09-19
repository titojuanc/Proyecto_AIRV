from pydub.playback import play
from pydub import AudioSegment
import os

# Variables para controlar el volumen
volumeFactor = 100
lastVolume = 100  # Por defecto al volumen máximo inicial

def confirmationSound():
    """Reproducir sonido de confirmación de manera segura"""
    confirm_volume()
    folderPath="audio"
    file_path = os.path.join(folderPath, "f1.mp3")

    if not os.path.exists(file_path):
        print(f"Error: Archivo '{file_path}' no encontrado.")
        return

    try:
        audio = AudioSegment.from_mp3(file_path)
        play(audio)
    except Exception as e:
        print(f"Error al reproducir sonido: {e}")

def volumeUp():
    """Aumentar el volumen en un 5% (máx 100%)"""
    global volumeFactor
    volumeFactor = min(volumeFactor + 5, 100)
    confirm_volume()

def volumeDown():
    """Disminuir el volumen en un 5% (mín 0%)"""
    global volumeFactor
    volumeFactor = max(volumeFactor - 5, 0)
    confirm_volume()

def set_volume(newVolume):
    """Establecer el volumen de manera segura con validación"""
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
    """Aplicar el nivel de volumen al sistema"""
    global volumeFactor
    try:
        os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volumeFactor}%")
    except Exception as e:
        print(f"Error al ajustar el volumen: {e}")

def mute():
    """Silenciar el sonido, guardando el volumen anterior"""
    global volumeFactor, lastVolume
    lastVolume = volumeFactor
    volumeFactor = 0
    confirm_volume()

def unmute():
    """Restaurar el volumen si estaba previamente silenciado"""
    global volumeFactor
    if volumeFactor == 0:
        volumeFactor = lastVolume
        confirm_volume()



