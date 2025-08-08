import requests
from escuchar_responder import speak
from bs4 import BeautifulSoup
import asyncio



def fiveFirstHeaders():
    URL = "https://www.bbc.com/news"
    response = requests.get(URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = soup.find_all("h2", class_="sc-9d830f2a-3")
        asyncio.run(speak("These are the top 5 latest news from "f"{URL}"+":\n"))
        for headline in headlines[:5]:
            description = headline.find_next("p")
            asyncio.run(speak(headline.text.strip()+":\n" + (description.text.strip() if description else "No description found.") + "\n"))
    else:
        print(f"Failed to fetch page, status code: {response.status_code}")
