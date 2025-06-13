import threading
import pywhatkit
import json
import os
import time
import pyautogui
from datetime import datetime, timedelta
import asyncio
import escuchar_responder

archivo_contactos = "contactos.json"

def enfocar_ventana_firefox():
    os.system("wmctrl -a 'Firefox'")
    time.sleep(1)

def cargar_contactos():
    if os.path.exists(archivo_contactos):
        with open(archivo_contactos, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def guardar_contactos(contactos):
    with open(archivo_contactos, "w") as f:
        json.dump(contactos, f, indent=4)

def buscar_contacto(contactos, nombre):
    return contactos.get(nombre)

def eliminar_contacto(contactos, nombre):
    if nombre in contactos:
        del contactos[nombre]
        guardar_contactos(contactos)
        asyncio.run(escuchar_responder.speak(f"Contacto '{nombre}' eliminado."))
    else:
        asyncio.run(escuchar_responder.speak(f"No existe el contacto '{nombre}'."))

def modificar_contacto(contactos, nombre_actual):
    if nombre_actual in contactos:
        asyncio.run(escuchar_responder.speak(f"Dime un nuevo nombre para {nombre_actual}. Si no lo quiere cambiar, diga ;no quiero"))
        nuevo_nombre = escuchar_responder.listen()
        while nuevo_nombre is None:
            nuevo_nombre = escuchar_responder.listen()

        nuevo_nombre = nuevo_nombre.strip()
        if "no quiero" in nuevo_nombre:
            nuevo_nombre = nombre_actual

        asyncio.run(escuchar_responder.speak(f"El actual número es, {contactos[nombre_actual]}. Si lo quiere cambiar, diga ; quiero"))
        nuevo_numero = escuchar_responder.listen()
        while nuevo_numero is None:
            nuevo_numero = escuchar_responder.listen()

        nuevo_numero = nuevo_numero.strip()
        if "quiero" not in nuevo_numero:
            nuevo_numero = contactos[nombre_actual]

        if nuevo_nombre != nombre_actual:
            del contactos[nombre_actual]

        contactos[nuevo_nombre] = nuevo_numero
        guardar_contactos(contactos)
        print(f"Contacto modificado: {nuevo_nombre} -> {nuevo_numero}")
    else:
        print(f"No existe el contacto '{nombre_actual}'.")

def nuevo_contacto(contactos):
    asyncio.run(escuchar_responder.speak("¿Cómo quiere llamar al contacto?"))
    nombre = escuchar_responder.listen()
    while nombre is None:
        nombre = escuchar_responder.listen()
    nombre = nombre.strip()

    asyncio.run(escuchar_responder.speak("¿Cuál es el número del contacto?"))
    numero = escuchar_responder.listen()
    if numero is None:
        asyncio.run(escuchar_responder.speak("No entendí el número. Inténtelo de nuevo."))
        return

    numero = numero.strip()
    if not numero.startswith("+"):
        numero = "+" + numero

    contactos[nombre] = numero
    guardar_contactos(contactos)
    asyncio.run(escuchar_responder.speak(f"Contacto '{nombre}' agregado."))

def enviar_mensaje(contactos, nombre, mensaje):
    numero = buscar_contacto(contactos, nombre)
    if not numero:
        asyncio.run(escuchar_responder.speak(f"Contacto '{nombre}' no encontrado. ¿Quiere agregarlo?"))
        rta = escuchar_responder.listen()
        while rta is None:
            rta = escuchar_responder.listen()
        rta = rta.strip().lower()
        if "si" in rta or "sí" in rta:
            nuevo_contacto(contactos)
        else:
            return

    ahora = datetime.now()
    envio = ahora + timedelta(minutes=2)
    envio = envio.replace(second=0, microsecond=0)

    try:
        pywhatkit.sendwhatmsg(numero, mensaje, envio.hour, envio.minute)
        enfocar_ventana_firefox()
        segundos_espera = (envio - datetime.now()).total_seconds() + 5
        if segundos_espera > 0:
            time.sleep(segundos_espera)
        pyautogui.hotkey('ctrl', 'w')
    except Exception as e:
        print("Error enviando el mensaje:", e)

# Envolturas para ejecutar en hilos
def enviar_mensaje_thread(contactos, nombre, mensaje):
    threading.Thread(target=enviar_mensaje, args=(contactos, nombre, mensaje)).start()

def main():
    contactos = cargar_contactos()

    while True:
        asyncio.run(escuchar_responder.speak("Mensajería. ¿Qué quiere hacer?"))
        opcion = escuchar_responder.listen()
        while opcion is None:
            opcion = escuchar_responder.listen()

        opcion = opcion.strip().lower()

        if "mostrar contactos" in opcion:
            if contactos:
                for nombre, numero in contactos.items():
                    asyncio.run(escuchar_responder.speak(f"- {nombre}: {numero}"))
            else:
                asyncio.run(escuchar_responder.speak("No hay contactos guardados."))

        elif "agregar contacto" in opcion:
            asyncio.run(escuchar_responder.speak("Solo terminal"))
            #nuevo_contacto(contactos)

        elif "enviar mensaje" in opcion:
            asyncio.run(escuchar_responder.speak("¿Quién es el destinatario?"))
            nombre = escuchar_responder.listen().strip()
            asyncio.run(escuchar_responder.speak("¿Cuál es el mensaje?"))
            mensaje = escuchar_responder.listen().strip()
            enviar_mensaje_thread(contactos, nombre, mensaje)

        elif "eliminar contacto" in opcion:
            asyncio.run(escuchar_responder.speak("¿Qué contacto quiere eliminar?"))
            nombre = escuchar_responder.listen()
            if nombre is None:
                asyncio.run(escuchar_responder.speak("No entendí. Inténtelo de nuevo."))
                continue
            nombre = nombre.strip()
            eliminar_contacto(contactos, nombre)

        elif "modificar contacto" in opcion:
            #asyncio.run(escuchar_responder.speak("¿Que contacto quiere modificar?"))
            #nombre_actual=escuchar_responder.listen()
            #modificar_contacto(contactos, nombre_actual)
            asyncio.run(escuchar_responder.speak("Solo terminal"))

        elif "ayuda" in opcion or "qué puedo hacer" in opcion or "que puedo hacer" in opcion:
            asyncio.run(escuchar_responder.speak(
                "Puedes; mostrar contactos; agregar contacto; enviar mensaje; eliminar contacto; modificar contacto"))

        elif "salir mensajería" in opcion:
            break
        
        else:
            asyncio.run(escuchar_responder.speak("Opción no válida. Intenta de nuevo."))

if __name__ == "__main__":
    main()
