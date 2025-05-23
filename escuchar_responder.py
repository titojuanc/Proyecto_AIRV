import speech_recognition as sr
import edge_tts
import pygame
import asyncio

def get_working_microphone():
    mic_list = sr.Microphone.list_microphone_names()
    recognizer = sr.Recognizer()

    for i, mic_name in enumerate(mic_list):
        try:
            with sr.Microphone(device_index=i) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print(f"Micrófono válido encontrado: {mic_name} (index {i})")
                return i
        except Exception:
            pass
    print("No se encontró micrófono válido.")
    return None

async def speak(answer):
    tts = edge_tts.Communicate(text=answer, voice="es-MX-DaliaNeural")
    await tts.save("message.mp3")

    pygame.mixer.init()
    pygame.mixer.music.load("message.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

def listen(device_index):
    recognizer = sr.Recognizer()

    with sr.Microphone(device_index=device_index) as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        recognizer.pause_threshold = 1.0
        print("Escuchando...")
        audio = recognizer.listen(source, timeout=6, phrase_time_limit=2)
    try:
        text = recognizer.recognize_google(audio, language="es-MX")
        print(f"Usted dijo: {text}")
        return text
    except sr.UnknownValueError:
        asyncio.run(speak("No entendí"))
        return None
    except sr.RequestError as e:
        print(f"Error al conectar con el servicio de reconocimiento de voz: {e}")
        return None

def main():
    device_index = get_working_microphone()
    if device_index is None:
        print("No hay micrófono disponible.")
        return

    while True:
        command = listen(device_index)
        if command:
            print(f"Comando reconocido: {command}")
            asyncio.run(speak(f"Dijiste: {command}"))

if __name__ == "__main__":
    main()
