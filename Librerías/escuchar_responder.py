import speech_recognition as sr
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import asyncio
from sonido import confirmationSound

async def speak(answer):
    """Genera el audio TTS y lo guarda en message.mp3. También lo reproduce usar asyncio.run(speak(param))"""
    tts = edge_tts.Communicate(text=answer, voice="es-MX-DaliaNeural")
    await tts.save("message.mp3")
    
    audio = AudioSegment.from_mp3("message.mp3")
    play(audio)

def listen(device_index=None):
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=device_index) as source:
        print("Ajustando ruido ambiental, espera...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Escuchando, habla ahora...")
        confirmationSound()
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
