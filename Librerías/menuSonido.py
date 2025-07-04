import sonido
import escuchar_responder
import asyncio

def menuSonido():
    #Voice-controlled menu for sound settings
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
                    asyncio.run(escuchar_responder.speak("¿Qué nivel de volumen? del cero al 100"))
                    volumen = escuchar_responder.listen()
                    sonido.set_volume(volumen)
                case "salir":
                    break
                case "ayuda":
                    asyncio.run(escuchar_responder.speak("Para subir el volumen decir: subir volumen. para bajar el volumen decir: bajar volumen. Para sileciar decir: mutear. Para desilenciar decir: desmutear. Para ajustar el volumen a un valor personalizado deseado decir: ajustar volumen. Para salir del modo de sonido decir: salir"))
                case _:
                    asyncio.run(escuchar_responder.speak("No se ha entendido la orden. Si precisa ayuda diga: Ayuda."))

menuSonido()