import escuchar_responder
import mensajeria
import news
import menuSonido
import calend
import blutu

# Debería quedar guardado en una memoria (archivos de texto), 
# al entrar por primera vez al sistema debería estar en False,
# luego de entrar por primera vez, que quede en True.
initial_config=False

def initial_configuration(primera_vez):
    initial_configuration.main(primera_vez)
    
def hearing():
    user_input = escuchar_responder.listen()  
    # Hacer que la función speak, al menos para esta parten no tenga error de timeout, 
    # ya que muchas veces no va a haber nadie hablando, y no sería un error.
    # También hacer que el sonido de confirmación no suene cada vez que se llama, 
    # sino cada vez que detecta su nombre.
    
    if user_input == nombreCodigo: # Debería ser una variable configurada 
                                   # en la configuración inicial
        escuchar_responder.speak("¿Que necesita?")  # O algún mensaje o sonido de acknowledge
        user_input = escuchar_responder.listen()
        if user_input:
            match user_input:
                case "mensajería":
                    mensajeria.main()
                case "música":
                    musica.main() # PENDIENTE
                case "noticias":
                    news.fiveFirstHeaders
                case "sonido":
                    menuSonido.menuSonido()
                case "calendario":
                    calend.menuCalendario()
                case "bluetooth":
                    blutu.main() # PENDIENTE
                case "configurción":
                    initial_config(True) # PENDIENTE    
                case "apagar":
                    exit(1) # y algún sonidito de apagado
                case _:
                    return
            
while True:
    if initial_config==False:
        initial_configuration(True)
        initial_config=True
    hearing()
    
