from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import os
import sys
from musica import musica_terminal as sc
from mensajeria import mensajeria_terminal as mt
from calendario import calend_logic
from datetime import datetime
app = Flask(__name__)
CORS(app)

# Variables de volumen
volumeFactor = 50
lastVolume = 50

# ------------------- RUTAS HTML -------------------

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/spotify')
def spotify():
    return render_template('spotify.html')

@app.route('/mensajeria')
def mensajeria():
    return render_template('mensajeria.html')

@app.route('/sonido')
def sonido():
    return render_template('sonido.html')

@app.route('/calendario')
def calendario():
    return render_template('calendario.html')

# ------------------- VOLUMEN -------------------

def apply_volume():
    try:
        os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volumeFactor}%")
        return jsonify({"volume": volumeFactor})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/volume/up', methods=['POST'])
def volume_up():
    global volumeFactor
    volumeFactor = min(volumeFactor + 5, 100)
    return apply_volume()

@app.route('/volume/down', methods=['POST'])
def volume_down():
    global volumeFactor
    volumeFactor = max(volumeFactor - 5, 0)
    return apply_volume()

@app.route('/volume/set', methods=['POST'])
def set_volume():
    global volumeFactor
    data = request.json
    try:
        newVolume = int(data.get("volume"))
        if 0 <= newVolume <= 100:
            volumeFactor = newVolume
        else:
            return jsonify({"error": "Volumen fuera de rango (0-100)."}), 400
    except:
        return jsonify({"error": "Entrada inválida, se esperaba un número."}), 400
    return apply_volume()

@app.route('/volume/mute', methods=['POST'])
def mute():
    global volumeFactor, lastVolume
    lastVolume = volumeFactor
    volumeFactor = 0
    return apply_volume()

@app.route('/volume/unmute', methods=['POST'])
def unmute():
    global volumeFactor
    if volumeFactor == 0:
        volumeFactor = lastVolume
    return apply_volume()

@app.route('/volume/status', methods=['GET'])
def get_volume():
    return jsonify({"volume": volumeFactor})

# ------------------- CALENDARIO -------------------

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
            return redirect(url_for('calendario'))
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

# ------------------- MENSAJERÍA -------------------

@app.route("/contactos", methods=["GET"])
def listar_contactos():
    contactos = mt.cargar_contactos()
    return jsonify(contactos)

@app.route("/contactos", methods=["POST"])
def agregar_contacto_api():
    data = request.json
    nombre = data.get("nombre")
    numero = data.get("numero")
    if not nombre or not numero:
        return jsonify({"error": "Faltan datos"}), 400
    ok = mt.agregar_contacto(nombre, numero)
    return jsonify({"status": "ok" if ok else "error"})

@app.route("/contactos", methods=["DELETE"])
def eliminar_contacto_api():
    data = request.json
    nombre = data.get("nombre")
    if not nombre:
        return jsonify({"error": "Falta nombre"}), 400
    ok = mt.eliminar_contacto(nombre)
    return jsonify({"status": "ok" if ok else "no encontrado"})

@app.route("/contactos", methods=["PUT"])
def modificar_contacto_api():
    data = request.json
    nombre_actual = data.get("nombre_actual")
    nuevo_nombre = data.get("nuevo_nombre")
    nuevo_numero = data.get("nuevo_numero")
    if not nombre_actual or not nuevo_nombre or not nuevo_numero:
        return jsonify({"error": "Faltan datos"}), 400
    ok = mt.modificar_contacto(nombre_actual, nuevo_nombre, nuevo_numero)
    return jsonify({"status": "ok" if ok else "error"})

@app.route("/enviar", methods=["POST"])
def enviar_mensaje_api():
    data = request.json
    nombre = data.get("nombre")
    mensaje = data.get("mensaje")
    if not nombre or not mensaje:
        return jsonify({"error": "Faltan datos"}), 400
    mt.enviar_mensaje_thread(nombre, mensaje)
    return jsonify({"status": "mensaje en proceso de envío"})

# ------------------- ACCIONES POR VOZ U OTRAS -------------------

@app.route('/accion', methods=['POST'])
def recibir_datos():
    data = request.json
    accion = data.get('accion')
    nombre = data.get('nombre')

    # --- Spotify ---
    if accion == "buscar_cancion" and nombre:
        ok = sc.buscar_y_reproducir_cancion(nombre)
        return jsonify({"status": "reproduciendo canción" if ok else "no encontrado", "nombre": nombre})

    elif accion == "buscar_album" and nombre:
        ok = sc.buscar_y_reproducir_album(nombre)
        return jsonify({"status": "reproduciendo álbum" if ok else "álbum no encontrado", "nombre": nombre})

    elif accion == "reproducir":
        ok = sc.reproducir()
        return jsonify({"status": "reanudando reproducción" if ok else "error al reproducir"})

    elif accion == "pausar":
        ok = sc.pausar()
        return jsonify({"status": "pausado" if ok else "error al pausar"})

    elif accion == "siguiente":
        ok = sc.siguiente()
        return jsonify({"status": "pasando canción" if ok else "error al pasar canción"})

    elif accion == "anterior":
        ok = sc.anterior()
        return jsonify({"status": "canción anterior" if ok else "error al volver"})

    # --- Mensajería desde /accion ---
    elif accion == "agregar contacto":
        numero = data.get("numero")
        if not nombre or not numero:
            return jsonify({"error": "Faltan datos"}), 400
        ok = mt.agregar_contacto(nombre, numero)
        return jsonify({"status": "contacto agregado" if ok else "error al agregar contacto"})

    elif accion == "eliminar contacto":
        ok = mt.eliminar_contacto(nombre)
        return jsonify({"status": "contacto eliminado" if ok else "contacto no encontrado"})

    elif accion == "modificar contacto":
        nuevo_nombre = data.get("nuevo_nombre")
        nuevo_numero = data.get("nuevo_numero")
        if not nombre or not nuevo_nombre or not nuevo_numero:
            return jsonify({"error": "Faltan datos"}), 400
        ok = mt.modificar_contacto(nombre, nuevo_nombre, nuevo_numero)
        return jsonify({"status": "contacto modificado" if ok else "error al modificar contacto"})

    elif accion == "enviar mensaje":
        mensaje = data.get("mensaje")
        if not nombre or not mensaje:
            return jsonify({"error": "Faltan datos"}), 400
        mt.enviar_mensaje_thread(nombre, mensaje)
        return jsonify({"status": "mensaje en proceso de envío"})

    # --- Otros comandos ---
    elif accion == "noticias":
        print("[Sistema] Mostrando noticias...")
        return jsonify({"status": "noticias mostradas"})

    elif accion == "microfono":
        print("[Sistema] Activando micrófono...")
        return jsonify({"status": "micrófono activado"})

    elif accion == "sonido":
        print("[Sistema] Controlando parlante...")
        return jsonify({"status": "control de sonido activado"})

    else:
        print(f"[Advertencia] Acción no reconocida: {accion}")
        return jsonify({"status": "acción no reconocida", "accion_recibida": accion}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
