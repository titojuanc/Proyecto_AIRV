import pywhatkit
import json
import os
import time
import pyautogui
from datetime import datetime, timedelta

archivo_contactos = "contactos.json"


def cargar_contactos():
    if os.path.exists(archivo_contactos):
        with open(archivo_contactos, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    else:
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
        print(f"Contacto '{nombre}' eliminado.")
    else:
        print(f"No existe el contacto '{nombre}'.")

def modificar_contacto(contactos, nombre_actual):
    if nombre_actual in contactos:
        nuevo_nombre = input(f"Nuevo nombre para '{nombre_actual}' (deja vacío para no cambiar): ").strip()
        nuevo_numero = input(f"Nuevo número para '{nombre_actual}' (actual: {contactos[nombre_actual]}): ").strip()

        # Si no se pone nuevo nombre, se mantiene el actual
        if nuevo_nombre == "":
            nuevo_nombre = nombre_actual

        # Si no se pone nuevo número, se mantiene el actual
        if nuevo_numero == "":
            nuevo_numero = contactos[nombre_actual]

        # Si cambió el nombre, eliminar la clave vieja y crear nueva
        if nuevo_nombre != nombre_actual:
            del contactos[nombre_actual]

        contactos[nuevo_nombre] = nuevo_numero
        guardar_contactos(contactos)
        print(f"Contacto modificado: {nuevo_nombre} -> {nuevo_numero}")
    else:
        print(f"No existe el contacto '{nombre_actual}'.")


def enviar_mensaje(contactos, nombre, mensaje):
    numero = buscar_contacto(contactos, nombre)
    if not numero:
        print(f"Contacto '{nombre}' no encontrado.")
        numero = input("Por favor ingresa el número de teléfono con código internacional (ej. +34123456789): ").strip()
        contactos[nombre] = numero
        guardar_contactos(contactos)
        print(f"Contacto '{nombre}' agregado.")

    ahora = datetime.now()
    envio = ahora + timedelta(minutes=1)  # envía en +1 minuto desde ahora
    hora_envio = envio.hour
    minuto_envio = envio.minute

    try:
        pywhatkit.sendwhatmsg(numero, mensaje, hora_envio, minuto_envio)
        print(f"Mensaje programado para {nombre} ({numero}) a las {hora_envio}:{minuto_envio}.")

        # Calcula tiempo de espera total: el tiempo hasta la hora programada + 30 segundos más
        ahora = datetime.now()
        envio = datetime(ahora.year, ahora.month, ahora.day, hora_envio, minuto_envio)
        segundos_espera = (envio - ahora).total_seconds() + 5  # 30 extra por seguridad

        if segundos_espera > 0:
            print(f"Esperando {int(segundos_espera)} segundos para cerrar la ventana...")
            time.sleep(segundos_espera)

        pyautogui.hotkey('ctrl', 'w')  # Cierra la ventana de WhatsApp Web
        print("Ventana de WhatsApp Web cerrada automáticamente.")

    except Exception as e:
        print("Error enviando el mensaje:", e)



def mostrar_menu():
    print("\n--- MENU ---")
    print("1. Mostrar contactos")
    print("2. Agregar contacto")
    print("3. Enviar mensaje ahora (+1 minuto)")
    print("5. Eliminar contacto")
    print("6. Modificar contacto")

def main():
    contactos = cargar_contactos()

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            if contactos:
                print("\nContactos guardados:")
                for nombre, numero in contactos.items():
                    print(f"- {nombre}: {numero}")
            else:
                print("No hay contactos guardados.")
        elif opcion == "2":
            nombre = input("Nombre del contacto: ").strip()
            numero = input("Número con código internacional (+...): ").strip()
            contactos[nombre] = numero
            guardar_contactos(contactos)
            print(f"Contacto '{nombre}' agregado/actualizado.")
        elif opcion == "3":
            nombre = input("Nombre del contacto: ").strip()
            mensaje = input("Mensaje a enviar: ").strip()
            enviar_mensaje(contactos, nombre, mensaje)
        elif opcion == "5":
            nombre = input("Nombre del contacto a eliminar: ").strip()
            eliminar_contacto(contactos, nombre)
        elif opcion == "6":
            nombre_actual = input("Nombre del contacto a modificar: ").strip()
            modificar_contacto(contactos, nombre_actual)

        else:
            print("Opción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    main()
