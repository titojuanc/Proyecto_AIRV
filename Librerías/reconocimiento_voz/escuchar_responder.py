import speech_recognition as sr
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import asyncio
import os
import sys
from sonido import sonido_process

async def speak(answer):
    """Genera el audio TTS y lo guarda en Ejemplos/message.mp3. También lo reproduce."""
    
    folder_path = "audio"
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, "message.mp3")
    
    tts = edge_tts.Communicate(text=answer, voice="es-MX-DaliaNeural")
    await tts.save(file_path) 
    
    audio = AudioSegment.from_mp3(file_path)
    play(audio)

def listen(device_index=None):
    """ Congela el programa y devuelve un String de lo que escuchó. Si hace timeout o no escucha bien el audio, devuelve None  """
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=device_index) as source:
        print("Ajustando ruido ambiental, espera...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Escuchando, habla ahora...")
        sonido_process.confirmationSound()
        try:
            audio = recognizer.listen(source, timeout=17, phrase_time_limit=15)
            print("Procesando...")
            texto = recognizer.recognize_google(audio, language="es-ES")
            texto=texto.lower()
            print(texto)
            return texto
        except sr.WaitTimeoutError:
            print("No se detectó voz a tiempo, intenta hablar más claro o rápido.")
            asyncio.run(speak("No llegué a capturar"))
            return None
        except sr.UnknownValueError:
            print("No se entendió lo que dijiste.")
            asyncio.run(speak("No entendí"))
            return None
        except sr.RequestError as e:
            print(f"Error con el servicio de reconocimiento: {e}")
            return None

