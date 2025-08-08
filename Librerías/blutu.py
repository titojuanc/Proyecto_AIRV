from bleak import BleakScanner, BleakClient
import asyncio
import escuchar_responder
import os
import subprocess
import re
async def scan():
    devices = await BleakScanner.discover()
    addresses=[]
    i=0
    client=None
    for d in devices:
        
       
        i=i+1
        print(f"Opción{i}: Name: {d.name}, Address: {d.address}")
        addresses.append(d.address)
        #"""escuchar_responder.speak(f"Opción{i}: {d.name}")"""
        
        #"""opcion=escuchar_responder.listen()
        #if i==5:
        #    break
    
    #match opcion:
     #   case "opción uno":
      #      device_adress= addresses[0]
       # case "opción dos":
        #    device_adress= addresses[1]
        #case "opción tres":
        #    device_adress= addresses[2]
        #case "opción cuatro":
         #   device_adress= addresses[3]
        #case "opción cinco":
         #   device_adress= addresses[4]
        #case _:
         #   escuchar_responder.speak(f"No entendí")
    respuesta=input("a que dispositivo desea conectarse?")
    connect(addresses[int(respuesta)-1])
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

    for mac, nombre in dispositivos:
        
       
        i=i+1
        print(f"Opción{i}: Name: {nombre}, Address: {mac}")
        addresses.append(mac)
    respuesta=input("a que dispositivo desea desconectarse?")
    disconnect(addresses[int(respuesta)-1])


dispositivos_conectados()

asyncio.run(scan())
#while True:
    #print("me corro")