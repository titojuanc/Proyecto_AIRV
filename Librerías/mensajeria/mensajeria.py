import threading
import json
import os
import time
import pyautogui
import webbrowser
from datetime import datetime, timedelta
import asyncio
from reconocimiento_voz import escuchar_responder
import urllib.parse

archivo_contactos = "Librerías/mensajeria/contactos.json"

# Variable global para controlar el envío
envio_en_progreso = False

def enfocar_ventana_firefox():
    """
    Enfoca la ventana de Firefox en el sistema usando 'wmctrl'
    y espera 2 segundos para asegurar que la ventana esté activa.
    """
    os.system("wmctrl -a 'Firefox'")
    time.sleep(2)

def cargar_contactos():
    """
    Carga los contactos desde el archivo JSON.
    Si el archivo no existe o está vacío, devuelve un diccionario vacío.
    """
    if os.path.exists(archivo_contactos):
        with open(archivo_contactos, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def guardar_contactos(contactos):
    """
    Guarda los contactos en formato JSON en el archivo correspondiente.
    """
    with open(archivo_contactos, "w") as f:
        json.dump(contactos, f, indent=4)

def buscar_contacto(contactos, nombre):
    """
    Busca un contacto por nombre en el diccionario de contactos.
    Devuelve el número asociado o None si no existe.
    """
    return contactos.get(nombre)

def eliminar_contacto(contactos, nombre):
    """
    Elimina un contacto del diccionario si existe.
    Informa mediante voz si se eliminó o no se encontró.
    """
    if nombre in contactos:
        del contactos[nombre]
        guardar_contactos(contactos)
        asyncio.run(escuchar_responder.speak(f"Contacto '{nombre}' eliminado."))
    else:
        asyncio.run(escuchar_responder.speak(f"No existe el contacto '{nombre}'."))

def modificar_contacto(contactos, nombre_actual):
    """
    Permite modificar el nombre y/o número de un contacto existente,
    interactuando por voz con el usuario.
    """
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
    """
    Agrega un nuevo contacto al diccionario,
    solicitando nombre y número mediante reconocimiento de voz.
    """
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

def enviar_mensaje_whatsapp_directo(numero, mensaje):
    """
    Envía un mensaje a un número usando WhatsApp Web de forma directa,
    abriendo Firefox y simulando la pulsación de 'Enter'.
    """
    try:
        # Codificar el mensaje para URL
        mensaje_codificado = urllib.parse.quote(mensaje)
        
        # Crear URL de WhatsApp
        url = f"https://web.whatsapp.com/send?phone={numero}&text={mensaje_codificado}"
        
        # Abrir en Firefox
        webbrowser.get('firefox').open(url)
        
        # Esperar a que cargue la página
        time.sleep(15)
        
        # Enfocar la ventana
        enfocar_ventana_firefox()
        
        # Presionar Enter para enviar el mensaje
        pyautogui.press('enter')
        
        # Esperar a que se envíe
        time.sleep(5)
        
        # Cerrar la pestaña
        pyautogui.hotkey('ctrl', 'w')
        
        return True
        
    except Exception as e:
        print(f"Error en envío directo: {e}")
        return False

def enviar_mensaje(contactos, nombre, mensaje, speak_callback=None):
    """
    Envía un mensaje a un contacto usando WhatsApp Web en un hilo separado.
    Controla que no haya envíos en proceso simultáneamente.
    """
    global envio_en_progreso
    
    if envio_en_progreso:
        if speak_callback:
            asyncio.run(speak_callback("Ya hay un mensaje en proceso de envío. Espere a que termine."))
        return
        
    envio_en_progreso = True
    
    try:
        numero = buscar_contacto(contactos, nombre)
        if not numero:
            if speak_callback:
                asyncio.run(speak_callback(f"Contacto '{nombre}' no encontrado. ¿Quiere agregarlo?"))
            rta = escuchar_responder.listen()
            while rta is None:
                rta = escuchar_responder.listen()
            rta = rta.strip().lower()
            if "si" in rta or "sí" in rta:
                nuevo_contacto(contactos)
            envio_en_progreso = False
            return

        print(f"Enviando mensaje a {nombre} ({numero})")
        if speak_callback:
            asyncio.run(speak_callback(f"Enviando mensaje a {nombre}"))

        # Usar método directo sin pywhatkit
        if enviar_mensaje_whatsapp_directo(numero, mensaje):
            if speak_callback:
                asyncio.run(speak_callback("Mensaje enviado correctamente"))
        else:
            if speak_callback:
                asyncio.run(speak_callback("Error al enviar el mensaje"))
        
    except Exception as e:
        print(f"Error enviando el mensaje: {e}")
        if speak_callback:
            asyncio.run(speak_callback("Hubo un error al enviar el mensaje"))
        
    finally:
        envio_en_progreso = False

def enviar_mensaje_selenium(contactos, nombre, mensaje, speak_callback=None):
    """
    Envía un mensaje usando WhatsApp Web con Selenium,
    ofreciendo mayor control sobre la interacción que con pyautogui.
    """
    global envio_en_progreso
    
    if envio_en_progreso:
        if speak_callback:
            asyncio.run(speak_callback("Ya hay un mensaje en proceso. Espere."))
        return
        
    envio_en_progreso = True
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.firefox.options import Options
        
        numero = buscar_contacto(contactos, nombre)
        if not numero:
            if speak_callback:
                asyncio.run(speak_callback(f"Contacto '{nombre}' no encontrado"))
            envio_en_progreso = False
            return

        # Configurar Firefox para usar perfil existente (opcional)
        options = Options()
        
        driver = webdriver.Firefox(options=options)
        
        try:
            # Codificar el mensaje para URL
            mensaje_codificado = urllib.parse.quote(mensaje)
            
            # Crear la URL de WhatsApp
            url = f"https://web.whatsapp.com/send?phone={numero}&text={mensaje_codificado}"
            
            driver.get(url)
            
            # Esperar a que cargue la página y el botón de enviar esté disponible
            wait = WebDriverWait(driver, 30)
            enviar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')))
            
            # Pequeña pausa antes de enviar
            time.sleep(2)
            
            # Enviar mensaje
            enviar_btn.click()
            
            # Esperar a que se envíe
            time.sleep(5)
            
            if speak_callback:
                asyncio.run(speak_callback("Mensaje enviado correctamente"))
            
        finally:
            # Cerrar el navegador
            driver.quit()
            time.sleep(2)  # Esperar a que se cierre completamente
        
    except Exception as e:
        print(f"Error con Selenium: {e}")
        if speak_callback:
            asyncio.run(speak_callback("Error al enviar el mensaje con Selenium"))
        
    finally:
        envio_en_progreso = False

def enviar_mensaje_thread(contactos, nombre, mensaje):
    """
    Lanza el envío de un mensaje en un hilo separado
    usando el método directo sin speak.
    """
    threading.Thread(target=enviar_mensaje, args=(contactos, nombre, mensaje, None)).start()

def enviar_mensaje_selenium_thread(contactos, nombre, mensaje):
    """
    Lanza el envío de un mensaje en un hilo separado
    usando la versión con Selenium.
    """
    threading.Thread(target=enviar_mensaje_selenium, args=(contactos, nombre, mensaje, None)).start()

def main():
    """
    Función principal del programa.
    Escucha comandos por voz y permite gestionar contactos
    y enviar mensajes de WhatsApp mediante diferentes opciones.
    """
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

        elif "enviar mensaje" in opcion:
            asyncio.run(escuchar_responder.speak("¿Quién es el destinatario?"))
            nombre = escuchar_responder.listen()
            if nombre is None:
                asyncio.run(escuchar_responder.speak("No entendí el nombre"))
                continue
            nombre = nombre.strip()
            
            asyncio.run(escuchar_responder.speak("¿Cuál es el mensaje?"))
            mensaje = escuchar_responder.listen()
            if mensaje is None:
                asyncio.run(escuchar_responder.speak("No entendí el mensaje"))
                continue
            mensaje = mensaje.strip()
            
            # Hablar solo desde el hilo principal
            asyncio.run(escuchar_responder.speak(f"Enviando mensaje a {nombre}"))
            
            # Ejecutar en hilo sin speak duplicado
            threading.Thread(target=enviar_mensaje, args=(contactos, nombre, mensaje, None)).start()
            
            # O usar Selenium
            # threading.Thread(target=enviar_mensaje_selenium, args=(contactos, nombre, mensaje, None)).start()

        elif "eliminar contacto" in opcion:
            asyncio.run(escuchar_responder.speak("¿Qué contacto quiere eliminar?"))
            nombre = escuchar_responder.listen()
            if nombre is None:
                asyncio.run(escuchar_responder.speak("No entendí. Inténtelo de nuevo."))
                continue
            nombre = nombre.strip()
            eliminar_contacto(contactos, nombre)

        elif "modificar contacto" in opcion:
            asyncio.run(escuchar_responder.speak("Solo terminal"))

        elif "ayuda" in opcion or "qué puedo hacer" in opcion or "que puedo hacer" in opcion:
            asyncio.run(escuchar_responder.speak(
                "Puedes; mostrar contactos; agregar contacto; enviar mensaje; eliminar contacto; modificar contacto"))

        elif "salir" in opcion:
            asyncio.run(escuchar_responder.speak("Saliendo de mensajería"))
            break
        
        else:
            asyncio.run(escuchar_responder.speak("Opción no válida. Intenta de nuevo."))

if __name__ == "__main__":
    main()
