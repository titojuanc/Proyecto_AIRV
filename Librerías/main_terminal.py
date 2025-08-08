from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Para permitir peticiones desde HTML local
import musica_terminal as sc

app = Flask(__name__)
CORS(app)  # Habilita CORS para todos los orígenes

@app.route('/')
def home():
    return render_template("/index.html")

@app.route('/spotify')
def spotify():
    return render_template('spotify.html')

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
        ok = sc.reproducir()
        if ok:
            return jsonify({
                "status": "reanudando reproducción", 
                "accion_recibida": accion
            })
        else:
            return jsonify({
                "status": "error al reproducir",
                "accion_recibida": accion
            }), 500

    elif accion == "pausar":
        ok = sc.pausar()
        if ok:
            return jsonify({
                "status": "pausado", 
                "accion_recibida": accion
            })
        else:
            return jsonify({
                "status": "error al pausar",
                "accion_recibida": accion
            }), 500

    elif accion == "siguiente":
        ok = sc.siguiente()
        if ok:
            return jsonify({
                "status": "pasando canción", 
                "accion_recibida": accion
            })
        else:
            return jsonify({
                "status": "error al pasar canción",
                "accion_recibida": accion
            }), 500

    elif accion == "anterior":
        ok = sc.anterior()
        if ok:
            return jsonify({
                "status": "canción anterior", 
                "accion_recibida": accion
            })
        else:
            return jsonify({
                "status": "error al poner la canción anterior",
                "accion_recibida": accion
            }), 500

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
        return jsonify({"status": "acción no reconocida", "accion_recibida": accion}), 400


    return jsonify({
        "status": "ok",
        "accion_recibida": accion,
        "nombre": nombre
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
