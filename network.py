import network

station = network.WLAN(network.STA_IF)
station.active(True)

with open("networks.txt", "r") as networks:
    for net in networks.read().split("\n"):
        if not station.isconnected():
            print(f"Attempting connection to {net.split()[0]}")
            station.connect(net.split()[0], net.split()[1])
        else:
            print("Network found")

