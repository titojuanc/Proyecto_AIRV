from flask import Flask, request, jsonify
from flask_cors import CORS  # Para permitir peticiones desde HTML local
import musica_terminal as sc

app = Flask(__name__)
CORS(app)  # Habilita CORS para todos los orígenes

@app.route('/')
def home():
    return "Servidor Flask activo"

@app.route('/accion', methods=['POST'])
def recibir_datos():
    data = request.json
    accion = data.get('accion')
    nombre = data.get('nombre') 

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
        sc.reproducir()
        return jsonify({"status": "reanudando reproducción"})

    elif accion == "pausar":
        sc.pausar()
        return jsonify({"status": "pausado"})

    elif accion == "siguiente":
        sc.siguiente()
        return jsonify({"status": "siguiente canción"})

    elif accion == "anterior":
        sc.anterior()
        return jsonify({"status": "canción anterior"})

    elif accion == "noticias":
        print("[Sistema] Mostrando noticias...")

    elif accion == "whatsapp":
        print("[Sistema] Abriendo WhatsApp...")

    elif accion == "microfono":
        print("[Sistema] Activando micrófono...")

    elif accion == "parlante":
        print("[Sistema] Controlando parlante...")

    else:
        print(f"[Advertencia] Acción no reconocida: {accion}")

    return jsonify({
        "status": "ok",
        "accion_recibida": accion,
        "nombre": nombre
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
