# La variable "primera_vez" sería un booleano que indica si
# se está accediendo por primera vez, o si simplemente
# se quiere cambiar algo de la configuración. 
import asyncio
import escuchar_responder



def main(primera_vez):
    if primera_vez==True:
        apodo=input("Como querés llamar al asistente? ")
        with open("apodo.txt","w") as txt:
            txt.write(apodo)
        return
    else:
        
        return
