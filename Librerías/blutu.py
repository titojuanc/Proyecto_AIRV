from bleak import BleakScanner, BleakClient
import asyncio
import escuchar_responder

async def scan():
    devices = await BleakScanner.discover()
    addresses=[]
    i=0
    client=none
    for d in devices:
        
       
        i=i+1
        print(f"Opción{i}: Name: {d.name}, Address: {d.address}")
        addresses.append(d.address)
        """escuchar_responder.speak(f"Opción{i}: {d.name}")"""
        
        """opcion=escuchar_responder.listen()
        if i==5:
            break
    
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
            escuchar_responder.speak(f"No entendí")

    asyncio.run(connect(device_adress))"""
    respuesta=input("a que dispositivo desea conectarse?")
    await connect(addresses[int(respuesta)-1])
async def connect(address):
    client=BleakClient(address)
    await client.connect()
    print(f"Connected to {address}")

async def disconnect(address):
    async with BleakClient(address) as client:
        if client.connc:
            escuchar_responder.speak("Desconectando")
asyncio.run(connect("E0:08:71:24:51:D3"))
"""asyncio.run(scan())"""
while True:
    print("me corro")