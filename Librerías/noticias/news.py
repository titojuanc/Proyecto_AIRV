import requests
import os
import sys

# Configuración de la ruta para importar el módulo de reconocimiento de voz
ruta_voz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'reconocimiento_voz'))
if ruta_voz not in sys.path:
    sys.path.append(ruta_voz)

from escuchar_responder import speak
from bs4 import BeautifulSoup
import asyncio


def fiveFirstHeaders():
    """
    Obtiene las 5 primeras noticias del portal BBC News.
    
    - Realiza una petición HTTP a la URL de BBC News.
    - Usa BeautifulSoup para parsear el HTML y extraer los encabezados <h2>.
    - Lee en voz alta (usando la función speak) los primeros 5 titulares,
      junto con su descripción (si existe).
    """
    URL = "https://www.bbc.com/news"
    response = requests.get(URL)

    if response.status_code == 200:
        # Parsear contenido HTML de la página
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = soup.find_all("h2", class_="sc-9d830f2a-3")

        # Anunciar fuente de noticias
        asyncio.run(speak("These are the top 5 latest news from " f"{URL}" + ":\n"))

        # Recorrer los primeros 5 titulares
        for headline in headlines[:5]:
            description = headline.find_next("p")
            asyncio.run(
                speak(
                    headline.text.strip() + ":\n"
                    + (description.text.strip() if description else "No description found.")
                    + "\n"
                )
            )
    else:
        # Si falla la petición, mostrar código de error
        print(f"Failed to fetch page, status code: {response.status_code}")
