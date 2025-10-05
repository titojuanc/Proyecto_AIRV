import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import psutil
import subprocess
import asyncio
import sys
import os

# Ruta para importar el módulo de reconocimiento de voz
ruta_voz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'reconocimiento_voz'))
if ruta_voz not in sys.path:
    sys.path.append(ruta_voz)
    
import escuchar_responder  # Módulo propio para escuchar comandos y responder con voz


# ------------------------------
# AUTENTICACIÓN SPOTIFY
# ------------------------------
# Se configura la conexión con la API de Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='b58173fc52b8464185eb93fe5cb77db9',
    client_secret='742e6c91ccf741588937c55b8b91f5f5',
    redirect_uri='http://127.0.0.1:3000/callback',
    scope='user-modify-playback-state user-read-playback-state playlist-read-private'
))

web_abierto = False
device_id = None  # Identificador del dispositivo activo


# ------------------------------
# FUNCIONES AUXILIARES
# ------------------------------

# Verifica si Spotify ya se está ejecutando en el sistema
def spotify_esta_corriendo():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'spotify' in proc.info['name'].lower():
            return True
    return False

# Abre la aplicación Spotify desde la terminal
def abrir_spotify():
    try:
        subprocess.Popen(['spotify'])
        print("Spotify se abrió.")
    except Exception as e:
        print(f"No se pudo abrir Spotify: {e}")

# Espera hasta que haya un dispositivo conectado a Spotify
def wait_conected_device(timeout=60):
    if not spotify_esta_corriendo():
        abrir_spotify()

    for i in range(timeout):
        devices = sp.devices().get("devices", [])
        if devices:
            device = devices[0]  # Usa el primer dispositivo disponible
            device_id = device['id']
            try:
                sp.transfer_playback(device_id=device_id, force_play=False)
                print(f"Dispositivo conectado: {device['name']}")
                return device_id
            except Exception as e:
                print(f"No se pudo transferir la reproducción: {e}")
        else:
            print(f"Esperando dispositivo... ({i+1}/{timeout})")
        time.sleep(1)

    raise Exception("No se detectó un dispositivo en el tiempo esperado.")

# Activa un dispositivo temporal reproduciendo y pausando algo rápidamente
def activar_dispositivo_temporal():
    global device_id
    device_id = wait_conected_device()
    sp.start_playback(device_id=device_id, context_uri="spotify:album:3Xiz5kq12VOzTw9Kun7m0f")
    time.sleep(1)
    sp.pause_playback(device_id=device_id)


# ------------------------------
# FUNCIONES DE BÚSQUEDA Y REPRODUCCIÓN
# ------------------------------

# Buscar y reproducir un álbum
def search_album():
    results, album_name = search("album")
    if results['albums']['items']:
        for album in results['albums']['items']:
            nombre = album.get('name') if album else None
            if nombre and nombre.lower() == album_name.lower():
                uri = album['uri']
                play("album", uri)
                return
        
        # Si no se encuentra coincidencia exacta, se reproduce la más cercana
        escuchar_responder.asyncio.run(escuchar_responder.speak("No estoy segura de que sea el álbum exacto, te reproduzco la mejor coincidencia."))
        uri = results['albums']['items'][0]['uri']
        play("album", uri)
    else:
        escuchar_responder.asyncio.run(escuchar_responder.speak("No se encontró el álbum."))

# Reproduce en Spotify un track o álbum dependiendo del tipo
def play(tipo, uri):
    global device_id
    if device_id is None:
        device_id = wait_conected_device()

    if tipo == 'track':
        sp.start_playback(device_id=device_id, uris=[uri])
    elif tipo == 'album':
        sp.start_playback(device_id=device_id, context_uri=uri)

# Buscar y reproducir una canción
def search_cancion():
    results, song = search("track")
    if results and 'tracks' in results and results['tracks']['items']:
        for track in results['tracks']['items']:
            if track['name'].lower() == song.lower():
                uri = track['uri']
                play("track", uri)
                escuchar_responder.asyncio.run(escuchar_responder.speak("No estoy segura de que sea la canción exacta, te reproduzco la mejor coincidencia."))
                return
        # Si no hay coincidencia exacta, reproducir la primera encontrada
        uri = results['tracks']['items'][0]['uri']
        play("track", uri)
    else:
        escuchar_responder.asyncio.run(escuchar_responder.speak("No se encontró la canción."))

# Función genérica para buscar álbum o canción
def search(tipo):
    pause()
    escuchar_responder.asyncio.run(escuchar_responder.speak(f"¿Qué {tipo} quiere reproducir?"))
    query = escuchar_responder.listen()

    if tipo == "album":
        search_type = "album"
    else:
        search_type = "track"
    
    results = sp.search(q=query, type=search_type, limit=5)
    return results, query


# ------------------------------
# CONTROL DE REPRODUCCIÓN
# ------------------------------

def next():
    """Pasa a la siguiente canción"""
    global device_id
    if device_id is None:
        try:
            device_id = wait_conected_device()
        except Exception as e:
            print(f"No se puede pasar a la siguiente porque no hay dispositivo activo: {e}")
            return

    try:
        playback = sp.current_playback()
        if not playback or not playback.get('is_playing'):
            print("No hay nada reproduciéndose, no se puede avanzar.")
            resume()
        sp.next_track()
        print("Pasando a la siguiente canción.")
        time.sleep(2)  
    except Exception as e:
        print(f"Error al pasar a la siguiente canción: {e}")

def previous():
    """Vuelve a la canción anterior"""
    global device_id
    if device_id is None:
        try:
            device_id = wait_conected_device()
        except Exception as e:
            print(f"No se puede retroceder porque no hay dispositivo activo: {e}")
            return

    try:
        playback = sp.current_playback()
        if not playback or not playback.get('is_playing'):
            print("No hay nada reproduciéndose, no se puede retroceder.")
            resume()
        sp.previous_track()
        print("Volviendo a la canción anterior.")
        time.sleep(2)
    except Exception as e:
        print(f"Error al volver a la canción anterior: {e}")

def pause():
    """Pausa la reproducción actual"""
    global device_id
    if device_id is None:
        try:
            device_id = wait_conected_device()
        except Exception as e:
            print(f"No se puede pausar porque no hay dispositivo activo: {e}")
            return
    try:
        playback = sp.current_playback()
        if playback is None or not playback.get('is_playing'):
            print("No hay reproducción activa, no puedo pausar.")
            return
        sp.pause_playback(device_id=device_id)
        print("Reproducción pausada.")
    except Exception as e:
        print(f"Error al pausar la reproducción: {e}")

def resume():
    """Reanuda la reproducción"""
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


# ------------------------------
# PROGRAMA PRINCIPAL
# ------------------------------

def main():
    # Mensaje de bienvenida
    asyncio.run(escuchar_responder.speak("Bienvenido a Spotify. Diga 'ayuda' para conocer los comandos. Reproducir random para empezar"))
    activar_dispositivo_temporal()
    while True:
        asyncio.run(escuchar_responder.speak("Home"))
        comando = escuchar_responder.listen()
        if not comando:
            continue

        comando = comando.lower()

        # Salir del programa
        if "salir" in comando or "terminar" in comando or "cerrar" in comando:
            asyncio.run(escuchar_responder.speak("Adiós, cerrando Spotify."))
            break

        # Control de reproducción
        elif "siguiente" in comando or "pasar canción" in comando or "próxima" in comando:
            next()
            asyncio.run(escuchar_responder.speak("Pasando a la siguiente canción."))

        elif "anterior" in comando or "volver canción" in comando or "canción anterior" in comando:
            previous()
            asyncio.run(escuchar_responder.speak("Volviendo a la canción anterior."))

        elif "pausar" in comando or "detener" in comando:
            pause()

        elif "reanudar" in comando or "continuar" in comando:
            resume()

        # Búsqueda de música
        elif "álbum" in comando or "album" in comando:
            search_album()

        elif "canción" in comando or "cancion" in comando:
            search_cancion()

        # Ayuda
        elif "ayuda" in comando:
            texto_ayuda = ("Puedes decir: siguiente, anterior, pausar, reanudar, "
                           "buscar canción, buscar álbum, o salir para terminar.")
            asyncio.run(escuchar_responder.speak(texto_ayuda))

        # Comando no entendido
        else:
            asyncio.run(escuchar_responder.speak("No entendí el comando, por favor repite."))
