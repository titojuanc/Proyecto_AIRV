from flask import Flask, render_template, request, redirect, url_for
import os
import sys

var = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Librerías', 'calendario'))
if var not in sys.path:
    sys.path.append(var)

import calend_logic
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index1.html')


# ------------------------------
# TASKS
# ------------------------------

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        fecha_str = request.form['fecha']
        tarea = request.form['tarea']
        try:
            fecha = datetime.strptime(fecha_str, "%d%m%Y")
            calend_logic.set_tasks(fecha, tarea)
            return redirect(url_for('index'))
        except ValueError:
            return "Fecha inválida. Use formato DDMMYYYY."
    return render_template('add_task.html')


@app.route('/today_tasks')
def today_tasks():
    tasks = calend_logic.today_tasks()
    return render_template('today_tasks.html', tasks=tasks)


@app.route('/tasks')
def date_tasks():
    fecha = request.args.get("fecha")
    tasks = calend_logic.get_tasks_for_date(fecha)
    return render_template('date_tasks.html', fecha=fecha, tasks=tasks)



# ------------------------------
# ALARMS
# ------------------------------

@app.route('/set_alarm', methods=['GET', 'POST'])
def set_alarm():
    if request.method == 'POST':
        fecha = request.form['fecha']
        hora = calend_logic.formatear_hora(request.form['hora'])
        if hora and not calend_logic.check_alarm(fecha, hora):
            calend_logic.set_alarm(fecha, hora)
            return redirect(url_for('index'))
        else:
            return "Hora inválida o alarma ya existente."
    return render_template('alarms.html')


if __name__ == '__main__':
    app.run(debug=True)
