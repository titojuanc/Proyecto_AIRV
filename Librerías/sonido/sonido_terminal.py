# volumen_api.py
"""
API REST con Flask para controlar el volumen del sistema.
Usa `pactl` para interactuar con el servidor de audio de Linux (PulseAudio).
Provee endpoints para subir, bajar, silenciar, restaurar y consultar el volumen.
"""

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Estado global del volumen
volumeFactor = 50   # Volumen inicial (en %)
lastVolume = 50     # Guarda el último volumen antes de hacer mute


@app.route('/volume/up', methods=['POST'])
def volume_up():
    """
    Incrementa el volumen en un 5%, hasta un máximo de 100%.
    """
    global volumeFactor
    volumeFactor = min(volumeFactor + 5, 100)
    return apply_volume()


@app.route('/volume/down', methods=['POST'])
def volume_down():
    """
    Reduce el volumen en un 5%, hasta un mínimo de 0%.
    """
    global volumeFactor
    volumeFactor = max(volumeFactor - 5, 0)
    return apply_volume()


@app.route('/volume/set', methods=['POST'])
def set_volume():
    """
    Establece el volumen en un valor específico (0–100%).
    Requiere un JSON con la clave "volume".
    """
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
    """
    Silencia el audio (volumen a 0%).
    Guarda el último volumen para poder restaurarlo con `unmute`.
    """
    global volumeFactor, lastVolume
    lastVolume = volumeFactor
    volumeFactor = 0
    return apply_volume()


@app.route('/volume/unmute', methods=['POST'])
def unmute():
    """
    Restaura el volumen anterior al mute.
    Si ya está en 0, recupera el valor guardado en `lastVolume`.
    """
    global volumeFactor
    if volumeFactor == 0:
        volumeFactor = lastVolume
    return apply_volume()


@app.route('/volume/status', methods=['GET'])
def get_volume():
    """
    Devuelve el volumen actual en formato JSON.
    """
    return jsonify({"volume": volumeFactor})


def apply_volume():
    """
    Aplica el volumen actual en el sistema mediante `pactl`.
    Devuelve el estado en formato JSON.
    """
    try:
        os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volumeFactor}%")
        return jsonify({"volume": volumeFactor})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Ejecutar servidor Flask en modo debug
    app.run(debug=True)
