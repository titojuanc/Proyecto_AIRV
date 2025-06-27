import sonido
import escuchar_responder
import asyncio

def menuSonido():
    """Voice-controlled menu for sound settings"""
    while True:
        teto = escuchar_responder.listen()
        if teto:
            match teto:
                case "subir volumen":
                    sonido.volumeUp()
                case "bajar volumen":
                    sonido.volumeDown()
                case "mutear":
                    sonido.mute()
                case "desmutear":
                    sonido.unmute()
                case "ajustar volumen":
                    asyncio.run(escuchar_responder.speak("¿Qué nivel de volumen? (0-100)"))
                    volumen = escuchar_responder.listen()
                    sonido.set_volume(volumen)
                case "salir":
                    break
                case _:
                    asyncio.run(escuchar_responder.speak("No se ha entendido la orden."))

menuSonido()