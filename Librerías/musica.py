import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import webbrowser
import escuchar_responder  # Asegurate que este módulo tenga funciones async bien llamadas

# Autenticación con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='b58173fc52b8464185eb93fe5cb77db9',
    client_secret='742e6c91ccf741588937c55b8b91f5f5',
    redirect_uri='http://127.0.0.1:3000/callback',
    scope='user-modify-playback-state user-read-playback-state playlist-read-private'
))

web_abierto = False
device_id = None

def wait_conected_device(timeout=60):
    global web_abierto
    print("Esperando dispositivo activo (Spotify)...")

    if not web_abierto:
        chrome_path = "/usr/bin/google-chrome %s"
        webbrowser.get(chrome_path).open("https://open.spotify.com/")
        web_abierto = True

    for _ in range(timeout):
        devices = sp.devices()
        if devices["devices"]:
            print("¡Dispositivo encontrado!")
            return devices["devices"][0]["id"]
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
    escuchar_responder.asyncio.run(escuchar_responder.speak("¿Qué playlist quiere reproducir?"))
    playlist = escuchar_responder.listen()
    results = sp.search(q=playlist, type="playlist", limit=1)
    if results['playlists']['items']:
        uri = results['playlists']['items'][0]['uri']
        play("playlist", uri)
    else:
        print("No se encontró la playlist.")

def search_cancion():
    escuchar_responder.asyncio.run(escuchar_responder.speak("¿Qué canción quiere reproducir?"))
    song = escuchar_responder.listen()
    results = sp.search(q=song, type="track", limit=1)
    if results['tracks']['items']:
        uri = results['tracks']['items'][0]['uri']
        play("track", uri)
    else:
        print("No se encontró la canción.")

def pause():
    sp.pause_playback(device_id=device_id)

def resume():
    sp.start_playback(device_id=device_id)

# -------------------------------
# MAIN DE PRUEBA
# -------------------------------

def main():
    global device_id
    device_id = wait_conected_device()

    while True:
        print("\nOpciones:")
        print("1. Reproducir playlist")
        print("2. Reproducir canción")
        print("3. Pausar")
        print("4. Reanudar")
        print("5. Salir")

        opcion = escuchar_responder.listen()

        if opcion == "reproducir playlist":
            search_playlist()
        elif opcion == "2":
            search_cancion()
        elif opcion == "3":
            pause()
        elif opcion == "4":
            resume()
        elif opcion == "5":
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
