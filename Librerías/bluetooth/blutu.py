from bleak import BleakScanner, BleakClient
import asyncio
import os
import subprocess
import re
import sys

ruta_voz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'reconocimiento_voz'))
if ruta_voz not in sys.path:
    sys.path.append(ruta_voz)
    
import escuchar_responder

def looks_like_mac_with_dashes(name: str) -> bool:
    parts = name.split("-")
    return (
        len(parts) == 6
        and all(len(p) == 2 and all(c in "0123456789ABCDEFabcdef" for c in p) for p in parts)
    )
async def scan():
    devices = await BleakScanner.discover()
    addresses=[]
    i=0
    client=None
    opcion=None
    device_adress=None
    for d in devices:
    
        
        if(d.address!=d.name and d.name!=None and not looks_like_mac_with_dashes(d.name)):
            i=i+1
            print(f"Opción {i}: Name: {d.name}, Address: {d.address}")
            addresses.append(d.address)
            await escuchar_responder.speak(f"Opción {i}: {d.name}")
            if i==5:
                break
    await escuchar_responder.speak("Que opción desea conectarse")
    while opcion==None and device_adress==None:
        opcion=escuchar_responder.listen()

     
    match opcion:
        case "opción uno":
            device_adress= addresses[0]
        case "opción dos":
            device_adress= addresses[1]
        case "opción tres":
            device_adress= addresses[2]
        case "opción cuatro":
            device_adress= addresses[3]
        case "opción cinco":
            device_adress= addresses[4]
        case _:
            await escuchar_responder.speak(f"No entendí")
    if(device_adress!=None):
        connect(device_adress)
def connect(address):
    os.system(f"bluetoothctl pair {address}") 
    os.system(f"bluetoothctl connect {address}") 
    os.system(f"bluetoothctl trust {address}") 

def disconnect(address):
    os.system(f"bluetoothctl disconnect {address}") 



def dispositivos_conectados():
    addresses=[]
    i=0

    resultado = subprocess.run(
        ['bluetoothctl', 'devices', 'Connected'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    dispositivos = []

    for linea in resultado.stdout.strip().split('\n'):
        if linea:
            partes = linea.strip().split(' ', 2)
            if len(partes) >= 2:
                mac = partes[1]

                # Obtener información detallada del dispositivo
                info = subprocess.run(
                    ['bluetoothctl', 'info', mac],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Buscar el nombre del dispositivo
                nombre = "Desconocido"
                for info_line in info.stdout.splitlines():
                    if "Name:" in info_line:
                        nombre = info_line.strip().split("Name:")[1].strip()
                        break

                dispositivos.append((mac, nombre))
    if dispositivos.__len__!=0:
        respuesta=None
        for mac, nombre in dispositivos:
            
        
            i=i+1
            asyncio.run(escuchar_responder.speak(f"Opción {i}: {nombre}"))
            addresses.append(mac)
            if i==5:
                break
        asyncio.run(escuchar_responder.speak("Qué dispositivo desea desconectar?"))
        device_adress=None
        while respuesta==None and device_adress==None :
            respuesta=escuchar_responder.listen()
        match respuesta:
            case "opción uno":
                device_adress= addresses[0]
            case "opción dos":
                if addresses.__len__>=1:
                    device_adress= addresses[1]
            case "opción tres":
                if addresses.__len__>=2:
                    device_adress= addresses[2]
            case "opción cuatro":
                if addresses.__len__>=3:
                    device_adress= addresses[3]
            case "opción cinco":
                if addresses.__len__>=4:
                    device_adress= addresses[4]
            case _:
                asyncio.run(escuchar_responder.speak(f"No entendí"))
        if device_adress!=None:
            disconnect(device_adress)
        
def main():
    asyncio.run(escuchar_responder.speak("Opciones de bluetooth"))  # O algún mensaje o sonido de acknowledge
    user_input = escuchar_responder.listen()
    if user_input:
        match user_input:
            case "conectar dispositivo":
                asyncio.run(scan())
            case "desconectar dispositivo":
                dispositivos_conectados()
            case "salir":
                return
            case _:
                asyncio.run(escuchar_responder.speak("No entendí"))  # O algún mensaje o sonido de acknowledge



#while True:
    #print("me corro")
