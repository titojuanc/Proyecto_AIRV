import spotipy
from spotipy.oauth2 import SpotifyOAuth
import psutil
import subprocess
import time

# ------------------------------
# AUTENTICACIÓN SPOTIFY
# ------------------------------
# Conexión con la API de Spotify usando OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='b58173fc52b8464185eb93fe5cb77db9',
    client_secret='742e6c91ccf741588937c55b8b91f5f5',
    redirect_uri='http://127.0.0.1:3000/callback',
    scope='user-modify-playback-state user-read-playback-state playlist-read-private'
))

device_id = None  # Guardará el ID del dispositivo activo


# ------------------------------
# FUNCIONES AUXILIARES
# ------------------------------

def spotify_esta_corriendo():
    """Verifica si el proceso de Spotify está activo en el sistema."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'spotify' in proc.info['name'].lower():
            return True
    return False

def abrir_spotify():
    """Abre la aplicación de Spotify si no está corriendo."""
    if not spotify_esta_corriendo():
        try:
            subprocess.Popen(['spotify'])
            print("Spotify abierto.")
        except Exception as e:
            print(f"Error al abrir Spotify: {e}")

def esperar_dispositivo(timeout=60):
    """
    Espera hasta que haya un dispositivo disponible en Spotify
    y lo selecciona como reproductor.
    """
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


# ------------------------------
# REPRODUCCIÓN DIRECTA
# ------------------------------

def play_uri(uri, tipo):
    """
    Reproduce una URI en Spotify (track o álbum).
    - uri: identificador de recurso de Spotify
    - tipo: 'track' o 'album'
    """
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


# ------------------------------
# BÚSQUEDA Y REPRODUCCIÓN
# ------------------------------

def buscar_y_reproducir_album(nombre):
    """Busca un álbum por nombre y lo reproduce si se encuentra."""
    results = sp.search(q=nombre, type="album", limit=1)
    if results['albums']['items']:
        uri = results['albums']['items'][0]['uri']
        print(f"[INFO] Reproduciendo álbum: {uri}")
        play_uri(uri, "album")
        return True
    print("[ERROR] Álbum no encontrado")
    return False

def buscar_y_reproducir_cancion(nombre):
    """Busca una canción por nombre y la reproduce si existe."""
    results = sp.search(q=nombre, type="track", limit=1)
    if results['tracks']['items']:
        uri = results['tracks']['items'][0]['uri']
        play_uri(uri, "track")
        return True
    return False


# ------------------------------
# CONTROL DE REPRODUCCIÓN
# ------------------------------

def reproducir():
    """Reanuda la reproducción si hay algo pausado."""
    global device_id
    if device_id is None:
        esperar_dispositivo()
    try:
        sp.start_playback(device_id=device_id)
        return True
    except Exception as e:
        print(f"[ERROR] al reproducir: {e}")
        return False

def pausar():
    """Pausa la reproducción actual."""
    global device_id
    if device_id is None:
        esperar_dispositivo()
    try:
        sp.pause_playback(device_id=device_id)
        return True
    except Exception as e:
        print(f"[ERROR] al pausar: {e}")
        return False

def siguiente():
    """Pasa a la siguiente canción en la cola de reproducción."""
    global device_id
    if device_id is None:
        esperar_dispositivo()
    try:
        sp.next_track(device_id=device_id)
        return True
    except Exception as e:
        print(f"[ERROR] al pasar a la siguiente canción: {e}")
        return False

def anterior():
    """Retrocede a la canción anterior en la cola."""
    global device_id
    if device_id is None:
        esperar_dispositivo()
    try:
        sp.previous_track(device_id=device_id)
        return True
    except Exception as e:
        print(f"[ERROR] al volver a la canción anterior: {e}")
        return False
