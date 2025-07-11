import spotipy
from spotipy.oauth2 import SpotifyOAuth
import psutil
import subprocess
import time

# Autenticación Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='b58173fc52b8464185eb93fe5cb77db9',
    client_secret='742e6c91ccf741588937c55b8b91f5f5',
    redirect_uri='http://127.0.0.1:3000/callback',
    scope='user-modify-playback-state user-read-playback-state playlist-read-private'
))

device_id = None

def spotify_esta_corriendo():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'spotify' in proc.info['name'].lower():
            return True
    return False

def abrir_spotify():
    if not spotify_esta_corriendo():
        try:
            subprocess.Popen(['spotify'])
            print("Spotify abierto.")
        except Exception as e:
            print(f"Error al abrir Spotify: {e}")

def esperar_dispositivo(timeout=60):
    global device_id
    abrir_spotify()
    for i in range(timeout):
        devices = sp.devices().get("devices", [])
        if devices:
            device_id = devices[0]['id']
            sp.transfer_playback(device_id=device_id, force_play=False)
            print(f"Dispositivo conectado: {devices[0]['name']}")
            return device_id
        time.sleep(1)
    raise Exception("No se detectó dispositivo activo.")

def play_uri(uri, tipo):
    global device_id
    if device_id is None:
        esperar_dispositivo()

    try:
        if tipo == "track":
            sp.start_playback(device_id=device_id, uris=[uri])
        else:
            sp.start_playback(device_id=device_id, context_uri=uri)
        print(f"[INFO] Reproduciendo {tipo}: {uri}")
    except Exception as e:
        print(f"[ERROR] en play_uri: {e}")

def buscar_y_reproducir_album(nombre):
    results = sp.search(q=nombre, type="album", limit=1)
    if results['albums']['items']:
        uri = results['albums']['items'][0]['uri']
        print(f"[INFO] Reproduciendo álbum: {uri}")
        play_uri(uri, "album")
        return True
    print("[ERROR] Álbum no encontrado")
    return False


def buscar_y_reproducir_cancion(nombre):
    results = sp.search(q=nombre, type="track", limit=1)
    if results['tracks']['items']:
        uri = results['tracks']['items'][0]['uri']
        play_uri(uri, "track")
        return True
    return False

def reproducir():
    global device_id
    if device_id is None:
        esperar_dispositivo()
    sp.start_playback(device_id=device_id)

def pausar():
    global device_id
    if device_id is None:
        esperar_dispositivo()
    sp.pause_playback(device_id=device_id)

def siguiente():
    if device_id is None:
        esperar_dispositivo()
    sp.next_track()

def anterior():
    if device_id is None:
        esperar_dispositivo()
    sp.previous_track()

