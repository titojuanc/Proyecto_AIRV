import schedule
import sonido
import os
from pydub.playback import play
from pydub import AudioSegment
from datetime import datetime

def alarm():
    audio=AudioSegment.from_mp3("listen.mp3")
    play(audio)
    sonido.set_volume(100)
    
def setAlarm(dia, hora):
    if(check_alarm(dia, hora)):
        schedule.every().dia.at(hora).do(alarm())
    else:
        print("ya hay una alarma a esa hora ese dia de la semana")

def check_alarm(day_of_week, hour):
    jobs = schedule.get_jobs()
    for job in jobs:
        scheduled_day = job.unit
        scheduled_time = job.next_run.strftime("%H:%M")
        if scheduled_day.lower() == day_of_week.lower() and scheduled_time == hour:
            return True
    return False

def date():
    fecha=datetime.today().strftime('%d%m%Y')

    hoy=open("hoy.txt","w")
    filename=f"{fecha}.txt"
    if os.path.exists(filename):
        fechas=open(filename,"r")
        contenido=fechas.read()
        hoy.write(contenido)
        fecha.close
        os.remove(filename)
    hoy.close
    
        

def currentDate():
    hoy = datetime.today().strftime('%d\%m\%Y')
    return hoy

def setTasks(fecha, tarea):
    """Stores tasks with an index in the format: INDEX - TASK. Usar formato de fecha DDMMYYYY"""
    try:
        fechaPasada = datetime.strptime(fecha, "%d%m%Y")
    except ValueError:
        print("Formato de fecha inválido. Use DDMMYYYY.")
        return
    
    if fechaPasada > datetime.today():
        filename = f"{fechaPasada.strftime('%d%m%Y')}.txt"

        # Read existing tasks to determine the next index
        index = 1
        if os.path.exists(filename):
            with open(filename, "r") as file:
                lines = file.readlines()
                if lines:
                    last_index = int(lines[-1].split(" - ")[0])  # Extract last index
                    index = last_index + 1

        # Append the task with the new index
        with open(filename, "a") as fechaTarea:
            fechaTarea.write(f"{index} - {tarea}\n")
        
        print(f"Tarea agregada para el día {fecha}: [{index}] {tarea}")
    else:
        print("No se puede ingresar una fecha anterior.")



def deleteTask(fecha, index):
    """Deletes a task from the list using the given index."""
    filename = f"{fecha}.txt"

    if not os.path.exists(filename):
        print("No hay tareas para esta fecha.")
        return
    
    # Read current tasks
    with open(filename, "r") as file:
        tasks = file.readlines()
    
    # Remove task by index
    updated_tasks = [task for task in tasks if not task.startswith(f"{index} - ")]

    if len(tasks) == len(updated_tasks):
        print(f"No se encontró una tarea con el índice {index}.")
        return
    
    # Rewrite the file with updated tasks and re-index them
    with open(filename, "w") as file:
        for i, task in enumerate(updated_tasks, start=1):
            file.write(f"{i} - {task.split(' - ', 1)[1]}")  # Update index
    
    print(f"Tarea con índice {index} eliminada de la fecha {fecha}.")




def todayTasks():
    hoy=open("hoy.txt","r")
    tareas=[]
    contenido=hoy.read()
    for i in contenido:
        if i=="\n":
            tareas.append(tarea)
        else:
            tarea+=i
            
    return tareas
    
deleteTask("07062025", 1)