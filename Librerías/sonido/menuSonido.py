from sonido import sonido_process
import os
import sys
ruta_voz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'reconocimiento_voz'))
if ruta_voz not in sys.path:
    sys.path.append(ruta_voz)
from reconocimiento_voz import escuchar_responder
import asyncio

def menuSonido():
    asyncio.run(escuchar_responder.speak("Estamos en sonido"))
    #Voice-controlled menu for sound settings
    while True:
        teto = escuchar_responder.listen()
        if teto:
            match teto:
                case "subir volumen":
                    sonido_process.volumeUp()
                case "bajar volumen":
                    sonido_process.volumeDown()
                case "mutear":
                    sonido_process.mute()
                case "desmutear":
                    sonido_process.unmute()
                case "ajustar volumen":
                    asyncio.run(escuchar_responder.speak("¿Qué nivel de volumen? del cero al 100"))
                    volumen = escuchar_responder.listen()
                    sonido_process.set_volume(volumen)
                case "salir":
                    break
                case "ayuda":
                    asyncio.run(escuchar_responder.speak("Para subir el volumen decir: subir volumen. para bajar el volumen decir: bajar volumen. Para sileciar decir: mutear. Para desilenciar decir: desmutear. Para ajustar el volumen a un valor personalizado deseado decir: ajustar volumen. Para salir del modo de sonido decir: salir"))
                case _:
                    asyncio.run(escuchar_responder.speak("No se ha entendido la orden. Si precisa ayuda diga: Ayuda."))

