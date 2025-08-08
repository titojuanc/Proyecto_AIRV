from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Para permitir peticiones desde HTML local
import musica_terminal as sc
import mensajeria_terminal as mt

app = Flask(__name__)
CORS(app)  # Habilita CORS para todos los orígenes

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/spotify')
def spotify():
    return render_template('spotify.html')

@app.route('/mensajeria')
def mensajeria():
    return render_template('mensajeria.html')

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

@app.route('/accion', methods=['POST'])
def recibir_datos():
    data = request.json
    accion = data.get('accion')
    nombre = data.get('nombre')

    # --- Spotify ---
    if accion == "buscar_cancion" and nombre:
        ok = sc.buscar_y_reproducir_cancion(nombre)
        if ok:
            return jsonify({"status": "reproduciendo canción", "nombre": nombre})
        return jsonify({"status": "no encontrado"})
    
    elif accion == "buscar_album" and nombre:
        ok = sc.buscar_y_reproducir_album(nombre)
        if ok:
            return jsonify({"status": "reproduciendo álbum", "nombre": nombre})
        return jsonify({"status": "álbum no encontrado"})

    elif accion == "reproducir":
        ok = sc.reproducir()
        if ok:
            return jsonify({"status": "reanudando reproducción", "accion_recibida": accion})
        else:
            return jsonify({"status": "error al reproducir", "accion_recibida": accion}), 500

    elif accion == "pausar":
        ok = sc.pausar()
        if ok:
            return jsonify({"status": "pausado", "accion_recibida": accion})
        else:
            return jsonify({"status": "error al pausar", "accion_recibida": accion}), 500

    elif accion == "siguiente":
        ok = sc.siguiente()
        if ok:
            return jsonify({"status": "pasando canción", "accion_recibida": accion})
        else:
            return jsonify({"status": "error al pasar canción", "accion_recibida": accion}), 500

    elif accion == "anterior":
        ok = sc.anterior()
        if ok:
            return jsonify({"status": "canción anterior", "accion_recibida": accion})
        else:
            return jsonify({"status": "error al poner la canción anterior", "accion_recibida": accion}), 500

    # --- Mensajería ---
    elif accion == "agregar contacto":
        numero = data.get("numero")
        if not nombre or not numero:
            return jsonify({"error": "Faltan datos para agregar contacto"}), 400
        ok = mt.agregar_contacto(nombre, numero)
        return jsonify({"status": "contacto agregado" if ok else "error al agregar contacto"})

    elif accion == "eliminar contacto":
        if not nombre:
            return jsonify({"error": "Falta nombre para eliminar contacto"}), 400
        ok = mt.eliminar_contacto(nombre)
        return jsonify({"status": "contacto eliminado" if ok else "contacto no encontrado"})

    elif accion == "modificar contacto":
        nuevo_nombre = data.get("nuevo_nombre")
        nuevo_numero = data.get("nuevo_numero")
        if not nombre or not nuevo_nombre or not nuevo_numero:
            return jsonify({"error": "Faltan datos para modificar contacto"}), 400
        ok = mt.modificar_contacto(nombre, nuevo_nombre, nuevo_numero)
        return jsonify({"status": "contacto modificado" if ok else "error al modificar contacto"})

    elif accion == "enviar mensaje":
        mensaje = data.get("mensaje")
        if not nombre or not mensaje:
            return jsonify({"error": "Faltan datos para enviar mensaje"}), 400
        mt.enviar_mensaje_thread(nombre, mensaje)
        return jsonify({"status": "mensaje en proceso de envío"})

    # Otras acciones opcionales
    elif accion == "noticias":
        print("[Sistema] Mostrando noticias...")

    elif accion == "microfono":
        print("[Sistema] Activando micrófono...")

    elif accion == "parlante":
        print("[Sistema] Controlando parlante...")

    else:
        print(f"[Advertencia] Acción no reconocida: {accion}")
        return jsonify({"status": "acción no reconocida", "accion_recibida": accion}), 400

    return jsonify({
        "status": "ok",
        "accion_recibida": accion,
        "nombre": nombre
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
