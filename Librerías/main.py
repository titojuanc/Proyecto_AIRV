import escuchar_responder
import mensajeria
import news
import menuSonido
import calend
import initial_configuration
import asyncio
#import blutu

# Debería quedar guardado en una memoria (archivos de texto), 
# al entrar por primera vez al sistema debería estar en False,
# luego de entrar por primera vez, que quede en True.
initial_config=False

def initial_configurationf(primera_vez):
    initial_configuration.main(primera_vez)
    
def hearing():
    
    user_input = escuchar_responder.listen()  
    # Hacer que la función speak, al menos para esta parten no tenga error de timeout, 
    # ya que muchas veces no va a haber nadie hablando, y no sería un error.
    # También hacer que el sonido de confirmación no suene cada vez que se llama, 
    # sino cada vez que detecta su nombre.

    with open("apodo.txt", "r") as apodo:
        nombreCodigo=apodo.read()
    
    if user_input == nombreCodigo: # Debería ser una variable configurada 
                                   # en la configuración inicial
        aux=0
        while user_input!="salir" or aux>=5:
            aux+=1
            asyncio.run(escuchar_responder.speak("¿Que necesita?"))  # O algún mensaje o sonido de acknowledge
            user_input = escuchar_responder.listen()
            if user_input:
                match user_input:
                    case "mensajería":
                        mensajeria.main()
                        asyncio.run(escuchar_responder.speak("salí"))
                    #case "música":
                        #musica.main() # PENDIENTE
                        #asyncio.run(escuchar_responder.speak("salí"))
                    case "noticias":
                        news.fiveFirstHeaders()
                        asyncio.run(escuchar_responder.speak("salí"))
                    case "sonido":
                        menuSonido.menuSonido()
                        asyncio.run(escuchar_responder.speak("salí"))
                    case "calendario":
                        calend.menuCalendario()
                        asyncio.run(escuchar_responder.speak("salí"))
                    #case "bluetooth":
                        #blutu.main() # PENDIENTE
                        asyncio.run(escuchar_responder.speak("salí"))
                    case "configuración":
                        initial_config(True) # PENDIENTE    
                        asyncio.run(escuchar_responder.speak("salí"))
                    case "apagar":
                        exit(1) # y algún sonidito de apagado
                    case _:
                        return
            
while True:
    if initial_config==False:
        initial_configurationf(True)
        initial_config=True
    hearing()
    
