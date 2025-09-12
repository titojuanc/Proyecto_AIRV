from reconocimiento_voz import escuchar_responder
from mensajeria.mensajeria import main as mensajeria_main
from noticias import news
from sonido import menuSonido
from calendario import calend
import initial_configuration
import asyncio
from bluetooth import blutu
from musica import musica
import os

# Debería quedar guardado en una memoria (archivos de texto), 
# al entrar por primera vez al sistema debería estar en False,
# luego de entrar por primera vez, que quede en True.


def initial_configurationf(primera_vez):
    initial_configuration.main(primera_vez)
    
def hearing():
    user_input = escuchar_responder.listen()

    with open("apodo.txt", "r") as apodo:
        nombreCodigo = apodo.read().strip().lower()

    if user_input and user_input.lower() == nombreCodigo:
        aux = 0

        while aux < 5:
            aux += 1
            asyncio.run(escuchar_responder.speak("¿Qué necesita?"))

            user_input = escuchar_responder.listen()
            if not user_input:
                continue

            user_input = user_input.lower()

            if "salir" in user_input:
                asyncio.run(escuchar_responder.speak("Saliendo..."))
                break

            elif any(word in user_input for word in ["mensajería", "mensaje", "mensajes"]):
                mensajeria_main()
                asyncio.run(escuchar_responder.speak("salí"))

            elif any(word in user_input for word in ["música", "musica", "poner música", "reproducir música"]):
                musica.main()
                asyncio.run(escuchar_responder.speak("salí"))

            elif any(word in user_input for word in ["noticia", "noticias", "novedades"]):
                news.fiveFirstHeaders()
                asyncio.run(escuchar_responder.speak("salí"))

            elif any(word in user_input for word in ["sonido", "volumen", "audio"]):
                menuSonido.menuSonido()
                asyncio.run(escuchar_responder.speak("salí"))

            elif any(word in user_input for word in ["calendario", "agenda", "eventos"]):
                calend.menuCalendario()
                asyncio.run(escuchar_responder.speak("salí"))

            elif any(word in user_input for word in ["bluetooth", "blutu", "conexión bluetooth"]):
                blutu.main()
                asyncio.run(escuchar_responder.speak("salí"))

            elif any(word in user_input for word in ["configuración", "configuracion", "ajustes", "setup"]):
                initial_configuration.main(True)
                asyncio.run(escuchar_responder.speak("salí"))

            elif any(word in user_input for word in ["apagar", "apágate", "adiós", "cerrar", "terminar"]):
                asyncio.run(escuchar_responder.speak("Apagando..."))
                exit(0)

            else:
                asyncio.run(escuchar_responder.speak("No entendí eso. ¿Podés repetir?"))


def run_main_voice(initial_config):      
    while True:
        status="true"
        if initial_config==False:
            initial_configurationf(True)
            initial_config=True
        if os.path.exists("mic.txt"):
            with open ("mic.txt","r") as mic:
                status=mic.read()
        if status=="true":
            hearing()
    
