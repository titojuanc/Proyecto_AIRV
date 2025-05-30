import schedule
import sonido
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

def currentDate():
    hoy = datetime.today().strftime('%d de %B de %Y') 

def setTasks():

def todayTasks():
    
