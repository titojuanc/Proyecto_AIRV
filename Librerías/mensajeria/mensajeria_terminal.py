import json
import os
import threading
from datetime import datetime, timedelta
import pywhatkit
import pyautogui
import time

archivo_contactos = "Librerías/mensajeria/contactos.json"

def cargar_contactos():
    if os.path.exists(archivo_contactos):
        with open(archivo_contactos, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def guardar_contactos(contactos):
    # Crear carpeta si no existe
    carpeta = os.path.dirname(archivo_contactos)
    os.makedirs(carpeta, exist_ok=True)

    # Guardar archivo
    with open(archivo_contactos, "w") as f:
        json.dump(contactos, f, indent=4)

def buscar_contacto(contactos, nombre):
    return contactos.get(nombre)

def agregar_contacto(nombre, numero):
    contactos = cargar_contactos()
    if not numero.startswith("+"):
        numero = "+" + numero
    contactos[nombre] = numero
    guardar_contactos(contactos)
    return True

def eliminar_contacto(nombre):
    contactos = cargar_contactos()
    if nombre in contactos:
        del contactos[nombre]
        guardar_contactos(contactos)
        return True
    return False

def modificar_contacto(nombre_actual, nuevo_nombre, nuevo_numero):
    contactos = cargar_contactos()
    if nombre_actual not in contactos:
        return False
    if not nuevo_numero.startswith("+"):
        nuevo_numero = "+" + nuevo_numero
    if nuevo_nombre != nombre_actual:
        if nuevo_nombre in contactos:
            return False  # Nuevo nombre ya existe
        del contactos[nombre_actual]
    contactos[nuevo_nombre] = nuevo_numero
    guardar_contactos(contactos)
    return True

def enfocar_firefox():
    try:
        # Intentar enfocar Firefox
        os.system('wmctrl -a "Mozilla Firefox"')
        time.sleep(2)
        
        # Alternativa: también intentar con el nombre de la pestaña
        os.system('wmctrl -a "WhatsApp Web"')
        time.sleep(1)
    except Exception as e:
        print(f"[Error] No se pudo enfocar Firefox: {e}")

# Ejemplo dentro de enviar_mensaje
def enviar_mensaje(nombre, mensaje):
    contactos = cargar_contactos()
    numero = buscar_contacto(contactos, nombre)
    if not numero:
        return False, "Contacto no encontrado"

    ahora = datetime.now()
    envio = ahora + timedelta(minutes=1)
    envio = envio.replace(second=0, microsecond=0)

    try:
        print(f"[WhatsApp] Enviando mensaje a {nombre} ({numero})")
        print(f"[WhatsApp] Programado para: {envio.strftime('%H:%M')}")
        
        pywhatkit.sendwhatmsg(numero, mensaje, envio.hour, envio.minute)
        
        # Esperar un poco antes de enfocar
        time.sleep(3)
        
        enfocar_firefox()
        
        # Esperar más tiempo para que WhatsApp Web cargue completamente
        print("[WhatsApp] Esperando carga de WhatsApp Web...")
        time.sleep(10)  # Aumentar a 10 segundos
        
        # Presionar Enter para asegurar el envío (a veces es necesario)
        pyautogui.press('enter')
        time.sleep(2)
        
        # Cerrar la pestaña
        pyautogui.hotkey('ctrl', 'w')
        
        print("[WhatsApp] Mensaje enviado exitosamente")
        return True, "Mensaje enviado"
        
    except Exception as e:
        print(f"[WhatsApp] Error: {str(e)}")
        return False, str(e)

# Hilo para enviar mensaje sin bloquear Flask
def enviar_mensaje_thread(nombre, mensaje):
    threading.Thread(target=enviar_mensaje, args=(nombre, mensaje)).start()
