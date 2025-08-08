# calend.py
import os
from datetime import datetime

ALARM_FILE = "alarms.txt"


# ------------------------------
# ALARM FUNCTIONS
# ------------------------------

def formatear_hora(hora):
    """Format and validate hour as HH:MM from 'HHMM' string."""
    try:
        hora = str(int(hora)).zfill(4)  # Ensure numeric and 4 digits
        hh = int(hora[:2])
        mm = int(hora[2:])
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            return f"{hh:02d}:{mm:02d}"
    except:
        return None
    return None


def set_alarm(dia, hora_formateada):
    """Save a new alarm."""
    with open(ALARM_FILE, "a") as f:
        f.write(f"{dia},{hora_formateada}\n")


def check_alarm(dia, hora):
    """Check if an alarm exists for given date and hour."""
    if not os.path.exists(ALARM_FILE):
        return False
    with open(ALARM_FILE, "r") as f:
        for line in f:
            d, h = line.strip().split(",")
            if str(d) == str(dia) and h == hora:
                return True
    return False


# ------------------------------
# DATE & TASK FUNCTIONS
# ------------------------------

def current_date():
    """Return today's date as DDMMYYYY."""
    return datetime.today().strftime('%d%m%Y')


def set_tasks(fecha_pasada, tarea):
    """
    Save a task for a given date (datetime object).
    Each task is indexed.
    """
    filename = f"{fecha_pasada.strftime('%d%m%Y')}.txt"

    index = 1
    if os.path.exists(filename):
        with open(filename, "r") as file:
            lines = file.readlines()
            if lines:
                try:
                    last_index = int(lines[-1].split(" - ")[0])
                    index = last_index + 1
                except:
                    pass  # Ignore malformed lines

    with open(filename, "a") as fecha_tarea:
        fecha_tarea.write(f"{index} - {tarea}\n")


def delete_task(fecha, index, updated_tasks):
    """
    Overwrite the tasks file for a given date with updated list.
    Fecha is DDMMYYYY string, index is integer, updated_tasks is list[str].
    """
    filename = f"{fecha}.txt"
    with open(filename, "w") as file:
        for i, task in enumerate(updated_tasks, start=1):
            file.write(f"{i} - {task.split(' - ', 1)[1]}")


def today_tasks():
    """Return today's tasks from hoy.txt if exists."""
    try:
        with open("hoy.txt", "r") as hoy:
            tareas = hoy.readlines()
            return [t.strip() for t in tareas]
    except FileNotFoundError:
        return []


def get_tasks_for_date(fecha):
    """
    Return list of tasks for a given DDMMYYYY string.
    If no file exists, returns empty list.
    """
    filename = f"{fecha}.txt"
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as file:
        return [t.strip() for t in file.readlines()]
