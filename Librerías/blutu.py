from bleak import BleakScanner, BleakClient
import asyncio
import escuchar_responder

async def scan():
    devices = await BleakScanner.discover()
    addresses=[]
    i=0
    for d in devices:
        
        print(f"Name: {d.name}, Address: {d.address}")
        i=i+1
        addresses.append(d.address)
        asyncio.run(escuchar_responder.speak(f"Opción{i}: {d.name}"))
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
            asyncio.run(escuchar_responder.speak(f"No entendí"))

    asyncio.run(connect(device_adress))
async def connect(address):
    async with BleakClient(address) as client:
        if await client.is_connected():
            print(f"Connected to {address}")
asyncio.run(scan())