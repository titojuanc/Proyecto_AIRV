import bluetooth
import asyncio
import escuchar_responder

def connect_bt():
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
    i=0
    addresses=[]
    asyncio.run(escuchar_responder.speak("Dispositivos encontrados:"))
    for addr, name in range(10):
        if not addr and not name:
            break
        else:
            i=i+1
            addresses.append(addr)
            asyncio.run(escuchar_responder.speak(f"Opción{1}: {name}"))

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



    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((device_address, 1))  # Port 1 is commonly used

    print(f"Connected to {device_address}")
    sock.send("Hello, Bluetooth!")  # Send data
    sock.close()

