# volumen_api.py

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

volumeFactor = 50 
lastVolume = 50    

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

def apply_volume():
    try:
        os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volumeFactor}%")
        return jsonify({"volume": volumeFactor})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
