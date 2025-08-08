import schedule
import sonido
import os
from pydub.playback import play
from pydub import AudioSegment
from datetime import datetime
import escuchar_responder
import asyncio
from word2number import w2n

ALARM_FILE="alarms.txt"

def convertir_a_numero(numero_en_letras):
    """
    Convierte texto como 'uno dos tres' -> 123
    """
    numeros_es = {
        "cero": "0",
        "uno": "1",
        "una": "1",
        "dos": "2",
        "tres": "3",
        "cuatro": "4",
        "cinco": "5",
        "seis": "6",
        "siete": "7",
        "ocho": "8",
        "nueve": "9",
    }

    palabras = numero_en_letras.lower().split()
    digitos = []

    for palabra in palabras:
        if palabra.isdigit():
            digitos.append(palabra)
        elif palabra in numeros_es:
            digitos.append(numeros_es[palabra])
        else:
            print(f"Error: palabra desconocida '{palabra}'")
            return None

    numero_final = "".join(digitos)
    return int(numero_final) if numero_final else None


def limpiar_fecha_voz(fecha_str):
    """
    Convierte una entrada como '20 20 20 20' → '20202020',
    luego valida y la devuelve como formato DDMMYYYY.
    """
    # Eliminar espacios y unir
    fecha_limpia = fecha_str.replace(" ", "")
    
    # Validar que tenga exactamente 8 dígitos numéricos
    if len(fecha_limpia) != 8 or not fecha_limpia.isdigit():
        print("Error: formato de fecha inválido. Debe tener 8 dígitos (ej: 27062025).")
        return None
    
    # Validar fecha real
    try:
        datetime.strptime(fecha_limpia, "%d%m%Y")
        return fecha_limpia
    except ValueError:
        print("Error: la fecha no existe.")
        return None

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

def setAlarm(diaa, formHora):
    try:
        

        with open(ALARM_FILE, "a") as f:
            f.write(f"{diaa},{formHora}\n")
        print(f"Alarma guardada para el día {diaa} a las {formHora}.")
        asyncio.run(escuchar_responder.speak("Alarma guardada."))
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

def setTasks(fechaPasada, tarea):
    """Guarda tareas con índice. Formato de fecha: DDMMYYYY"""

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
        

def deleteTask(fecha, index, updated_tasks):
    """Elimina una tarea específica."""
    
    fechaPasada = datetime.strptime(fecha, "%d%m%Y")
    if fechaPasada<=datetime.today():
        return

    filename = f"{fecha}.txt"

    with open(filename, "w") as file:
        for i, task in enumerate(updated_tasks, start=1):
            file.write(f"{i} - {task.split(' - ', 1)[1]}")  # Reindexando

    print(f"Tarea con índice {index} eliminada de la fecha {fecha}.")

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
                    #checkeo dia
                    diaerr=True
                    while diaerr:
                        asyncio.run(escuchar_responder.speak("¿Qué día?"))
                        dia = escuchar_responder.listen()
                        if dia=="salir":
                            break
                        if limpiar_fecha_voz(dia)==None:
                            asyncio.run(escuchar_responder.speak("No se entendió lo que dijiste."))
                        else:
                            diaa = limpiar_fecha_voz(str(dia))
                            diaaa=datetime.strptime(diaa, "%d%m%Y")
                            if diaa and diaaa>=datetime.today():
                                diaerr=False
                                horaerr=True
                                while horaerr:
                                    #checkeo hora
                                    asyncio.run(escuchar_responder.speak("¿Qué hora?"))
                                    hora = escuchar_responder.listen()

                                    if hora=="salir":
                                        break
                                    if formatear_hora(hora)==None:
                                        asyncio.run(escuchar_responder.speak("No se entendió lo que dijiste."))
                                    else:

                                        formHora = formatear_hora(hora)

                                        if formHora:
                                            horaerr=False
                                            if check_alarm(diaa, formHora): #checkeo si ya existe la alarma
                                                asyncio.run(escuchar_responder.speak(f"Ya hay una alarma a las {formHora} el día {diaa}."))

                                            else:
                                                setAlarm(diaa, formHora) #pongo la alarma 
                                        
                                        else:
                                            asyncio.run(escuchar_responder.speak("Error: hora inválida. Usar formato HHMM válido. Digalo de nuevo por favor"))
                            else:
                                asyncio.run(escuchar_responder.speak("Formato de dia inválido. Digalo de nuevo por favor."))

                case "añadir tarea":

                    diaerr=True
                    while diaerr:
                        asyncio.run(escuchar_responder.speak("¿Qué fecha?"))
                        fecha = escuchar_responder.listen()
                        #checkeo para salir del loop
                        if fecha=="salir":
                            break
                        if limpiar_fecha_voz(fecha)==None:
                            asyncio.run(escuchar_responder.speak("No se entendio lo que dijiste."))
                        else:
                            fech=limpiar_fecha_voz(fecha)

                            #checkea si hay 10 tareas en el dia
                            filename = f"{fech}.txt"
                            with open(filename, "r") as file:
                                tasks = file.readlines()
                            i=0
                            for task in tasks:
                                i=i+1
                            print(i)
                            if i==9:
                                asyncio.run(escuchar_responder.speak("No se pueden tener más de 9  tareas en un día."))
                                break
                            
                            fechaPasada = datetime.strptime(fech, "%d%m%Y")

                            #checkeo que dia este bien y que no se anterior a hoy
                            if fechaPasada and fechaPasada >= datetime.today():
                                diaerr=False
                                horaerr=True
                                while horaerr:
                                    asyncio.run(escuchar_responder.speak("¿Cuál es la tarea?"))
                                    tarea = escuchar_responder.listen()

                                    if tarea=="salir":
                                        break

                                    if tarea:
                                        setTasks(fechaPasada, tarea)
                                        horaerr=False
                                    else:
                                        asyncio.run(escuchar_responder.speak("Error, no puede no haber tarea."))
                                        
                            else:
                                asyncio.run(escuchar_responder.speak("Error de formato de fecha o fecha anterior a hoy"))


                case "recordame las tareas de hoy":
                    tareas = todayTasks()
                    if tareas:
                        for tarea in tareas:
                            asyncio.run(escuchar_responder.speak(tarea))
                    else:
                        asyncio.run(escuchar_responder.speak("No hay tareas para hoy."))

                case "quitar tarea":
                    diaerr=True
                    while diaerr:
                        asyncio.run(escuchar_responder.speak("¿Qué fecha?"))
                        fecha = escuchar_responder.listen()

                        if fecha=="salir":
                            break
                        if limpiar_fecha_voz(fecha)==None:
                            asyncio.run(escuchar_responder.speak("No se entendio lo que dijiste."))
                        else:

                            fech=limpiar_fecha_voz(fecha)
                            filename = f"{fech}.txt"
                                
                            if fech and os.path.exists(filename):
                                diaerr=False
                                indexerr=True
                                while indexerr:
                                    asyncio.run(escuchar_responder.speak("¿Cuál es el número de tarea?"))
                                    index = escuchar_responder.listen()

                                    if index=="salir":
                                        break

                                    print ("INDICE "+ str(index))

                                    
                                    
                                    if index:
                                        inde=convertir_a_numero(index)
                                        print ("INDICE "+ str(inde))
                                        if inde:
                                            with open(filename, "r") as file:
                                                tasks = file.readlines()

                                            updated_tasks = [task for task in tasks if not task.startswith(f"{inde} - ")]
                                            if len(tasks) != len(updated_tasks):
                                                deleteTask(fech, inde, updated_tasks)
                                                indexerr=False
                                            else:
                                                asyncio.run(escuchar_responder.speak("Error, no existe tarea con ese indice."))

                                        else:
                                            asyncio.run(escuchar_responder.speak("Error, intente de nuevo."))
                                    else:
                                        asyncio.run(escuchar_responder.speak("Error, indice inválido o no hay tareas para ese dia."))

                            else:
                                asyncio.run(escuchar_responder.speak("Error de formato de fecha o fecha anterior a hoy"))
                    
                case "salir":
                    break
                case "ayuda":
                    asyncio.run(escuchar_responder.speak("Los comandos son: poner alarma, añadir tarea, recordame las tareas de hoy, quitar tarea, salir."))
                    asyncio.run(escuchar_responder.speak("Especificaciones:"))
                    asyncio.run(escuchar_responder.speak("Poner alarma: usar formato DDMMYYYY para el dia y usar formato HHMM para la hora y minutos."))
                    asyncio.run(escuchar_responder.speak("Añadir tarea: usar formato DDMMYYYY para el dia, no pueden haber más de 9 tareas."))
                    asyncio.run(escuchar_responder.speak("Quitar tarea: usar formato DDMMYYYY para el dia."))
                case _:
                    asyncio.run(escuchar_responder.speak("No se ha entendido la orden."))

