import os

os.system("bluetoothctl")
os.system("power on")
os.system("agent on")
os.system("pair E0:08:71:24:51:D3")
os.system("connect E0:08:71:24:51:D3")
os.system("trust E0:08:71:24:51:D3")
os.system("agent off")
os.system("quit")