import schedule
import sonido
import os
from pydub.playback import play
from pydub import AudioSegment
from datetime import datetime
import escuchar_responder
import asyncio

ALARM_FILE="alarms.txt"

def formatear_hora(hora):
    try:
        hora = str(int(hora)).zfill(4)  # Asegura que sea numérico y de 4 dígitos
        hh = int(hora[:2])
        mm = int(hora[2:])

        # Validar que esté en rango válido
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            return f"{hh:02d}:{mm:02d}"
        else:
            return None
    except:
        return None

def alarm():
    try:
        audio = AudioSegment.from_mp3("listen.mp3")
        play(audio)
        sonido.set_volume(100)
    except Exception as e:
        print(f"Error al reproducir alarma: {e}")

def setAlarm(dia, hora):
    try:
        dia = int(dia)
        formHora = formatear_hora(hora)
        if not formHora:
            print("Error: hora inválida. Usá formato HHMM válido.")
            return

        if check_alarm(dia, formHora):
            print(f"Ya hay una alarma a las {formHora} el día {dia}.")
            return

        with open(ALARM_FILE, "a") as f:
            f.write(f"{dia},{formHora}\n")
        print(f"Alarma guardada para el día {dia} a las {formHora}.")
    except ValueError:
        print("Error: formato de día inválido.")

def check_alarm(dia, hora):
    if not os.path.exists(ALARM_FILE):
        return False
    with open(ALARM_FILE, "r") as f:
        for line in f:
            d, h = line.strip().split(",")
            if str(d) == str(dia) and h == hora:
                return True
    return False

def date():
    try:
        fecha = datetime.today().strftime('%d%m%Y')
        hoy_file = "hoy.txt"
        filename = f"{fecha}.txt"

        with open(hoy_file, "w") as hoy:
            if os.path.exists(filename):
                with open(filename, "r") as fechas:
                    contenido = fechas.read()
                    hoy.write(contenido)
                os.remove(filename)
    except Exception as e:
        print(f"Error al manejar archivos: {e}")

def currentDate():
    return datetime.today().strftime('%d%m%Y')

def setTasks(fecha, tarea):
    """Guarda tareas con índice. Formato de fecha: DDMMYYYY"""
    try:
        fechaPasada = datetime.strptime(fecha, "%d%m%Y")
        if fechaPasada <= datetime.today():
            print("No se puede ingresar una fecha anterior.")
            return

        filename = f"{fechaPasada.strftime('%d%m%Y')}.txt"

        # Leer índices previos
        index = 1
        if os.path.exists(filename):
            with open(filename, "r") as file:
                lines = file.readlines()
                if lines:
                    last_index = int(lines[-1].split(" - ")[0])
                    index = last_index + 1

        # Escribir tarea con índice
        with open(filename, "a") as fechaTarea:
            fechaTarea.write(f"{index} - {tarea}\n")
        
        print(f"Tarea agregada para el día {fecha}: [{index}] {tarea}")
    except ValueError:
        print("Formato de fecha inválido. Use DDMMYYYY.")
    except Exception as e:
        print(f"Error al manejar la tarea: {e}")

def deleteTask(fecha, index):
    """Elimina una tarea específica."""
    try:
        filename = f"{fecha}.txt"
        if not os.path.exists(filename):
            print("No hay tareas para esta fecha.")
            return

        with open(filename, "r") as file:
            tasks = file.readlines()

        updated_tasks = [task for task in tasks if not task.startswith(f"{index} - ")]

        if len(tasks) == len(updated_tasks):
            print(f"No se encontró una tarea con el índice {index}.")
            return

        with open(filename, "w") as file:
            for i, task in enumerate(updated_tasks, start=1):
                file.write(f"{i} - {task.split(' - ', 1)[1]}")  # Reindexando

        print(f"Tarea con índice {index} eliminada de la fecha {fecha}.")
    except Exception as e:
        print(f"Error al eliminar tarea: {e}")

def todayTasks():
    """Obtiene tareas del día desde 'hoy.txt'"""
    try:
        with open("hoy.txt", "r") as hoy:
            tareas = hoy.readlines()
            return [t.strip() for t in tareas]
    except FileNotFoundError:
        print("No hay tareas registradas para hoy.")
        return []
    except Exception as e:
        print(f"Error al leer tareas: {e}")
        return []

def menuCalendario():
    while True:
        teto = escuchar_responder.listen()
        if teto:
            match teto:
                case "poner alarma":
                    asyncio.run(escuchar_responder.speak("¿Qué día?"))
                    dia = escuchar_responder.listen()
                    asyncio.run(escuchar_responder.speak("¿Qué hora?"))
                    hora = escuchar_responder.listen()
                    setAlarm(dia, hora)
                case "añadir tarea":
                    asyncio.run(escuchar_responder.speak("¿Qué fecha? Usar formato DDMMYYYY"))
                    fecha = escuchar_responder.listen()
                    asyncio.run(escuchar_responder.speak("¿Cuál es la tarea?"))
                    tarea = escuchar_responder.listen()
                    setTasks(fecha, tarea)
                case "recordame las tareas de hoy":
                    tareas = todayTasks()
                    if tareas:
                        for tarea in tareas:
                            asyncio.run(escuchar_responder.speak(tarea))
                    else:
                        asyncio.run(escuchar_responder.speak("No hay tareas para hoy."))
                case "quitar tarea":
                    asyncio.run(escuchar_responder.speak("¿Qué fecha? Usar formato DDMMYYYY"))
                    fecha = escuchar_responder.listen()
                    asyncio.run(escuchar_responder.speak("¿Cuál es el número de tarea?"))
                    indice = escuchar_responder.listen()
                    deleteTask(fecha, indice)
                case "salir":
                    break
                case _:
                    asyncio.run(escuchar_responder.speak("No se ha entendido la orden."))

menuCalendario()