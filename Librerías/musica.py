import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import psutil
import subprocess
import escuchar_responder

# Autenticación con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='b58173fc52b8464185eb93fe5cb77db9',
    client_secret='742e6c91ccf741588937c55b8b91f5f5',
    redirect_uri='http://127.0.0.1:3000/callback',
    scope='user-modify-playback-state user-read-playback-state playlist-read-private'
))

web_abierto = False
device_id = None

def spotify_esta_corriendo():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'spotify' in proc.info['name'].lower():
            return True
    return False

def abrir_spotify():
    try:
        subprocess.Popen(['spotify'])
        print("Spotify se abrió.")
    except Exception as e:
        print(f"No se pudo abrir Spotify: {e}")

def wait_conected_device(timeout=60):
    if not spotify_esta_corriendo():
        abrir_spotify()
    for _ in range(timeout):
        devices = sp.devices()
        for device in devices.get("devices", []):
            if device.get("is_active"):
                print(f"Dispositivo activo encontrado: {device['name']}")
                return device["id"]
        time.sleep(1)
    raise Exception("No se detectó un dispositivo activo en el tiempo esperado.")

def play(tipo, uri):
    global device_id
    if device_id is None:
        device_id = wait_conected_device()

    if tipo == 'playlist':
        sp.start_playback(device_id=device_id, context_uri=uri)
    elif tipo == 'track':
        sp.start_playback(device_id=device_id, uris=[uri])

def search_playlist():
    pause()
    escuchar_responder.asyncio.run(escuchar_responder.speak("¿Qué playlist quiere reproducir?"))
    playlist_name = escuchar_responder.listen()
    results = sp.search(q=playlist_name, type="playlist", limit=5)
    if results['playlists']['items']:
        for playlist in results['playlists']['items']:
            nombre = playlist.get('name') if playlist else None
            if nombre and nombre.lower() == playlist_name.lower():
                uri = playlist['uri']
                play("playlist", uri)
                return
        
        escuchar_responder.asyncio.run(escuchar_responder.speak("No estoy segura de que sea la playlist exacta, te reproduzco la mejor coincidencia."))
        uri = results['playlists']['items'][0]['uri']
        play("playlist", uri)
    else:
        escuchar_responder.asyncio.run(escuchar_responder.speak("No se encontré la playlist."))


def search_cancion():
    pause()
    escuchar_responder.asyncio.run(escuchar_responder.speak("¿Qué canción quiere reproducir?"))
    song = escuchar_responder.listen()
    results = sp.search(q=song, type="track", limit=5)
    if results['tracks']['items']:
        for track in results['tracks']['items']:
            if track['name'].lower() == song.lower():
                uri = track['uri']
                play("track", uri)
                escuchar_responder.asyncio.run(escuchar_responder.speak("No estoy segura de que sea la canción exacta, te reproduzco la mejor coincidencia."))
        uri = results['tracks']['items'][0]['uri']
        play("track", uri)
    else:
        escuchar_responder.asyncio.run(escuchar_responder.speak("No se encontré la canción."))


def pause():
    global device_id
    if device_id is None:
        try:
            device_id = wait_conected_device()
        except Exception as e:
            print(f"No se puede pausar porque no hay dispositivo activo: {e}")
            return
    try:
        sp.pause_playback(device_id=device_id)
        print("Reproducción pausada.")
    except Exception as e:
        print(f"Error al pausar la reproducción: {e}")

def resume():
    global device_id
    if device_id is None:
        try:
            device_id = wait_conected_device()
        except Exception as e:
            print(f"No se puede reanudar porque no hay dispositivo activo: {e}")
            return
    try:
        sp.start_playback(device_id=device_id)
        print("Reproducción reanudada.")
    except Exception as e:
        print(f"Error al reanudar la reproducción: {e}")

