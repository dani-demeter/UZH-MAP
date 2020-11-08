# pip install requests
import requests
# pip install scapy
# from scapy.all import *
# from scapy.arch.windows import IFACES
from math import sin, cos, sqrt, atan2, radians
import tkinter as tk

myIP = ""
ipInfo = {}


def calculateDistance(lat1, lon1, lat2, lon2):
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def getBasicIPInfo():
    # GET MY IP
    myIP = requests.get('https://api.ipify.org').text
    print(f"My public IP address is: {myIP}")

    # GET INFO BASED ON IP
    ipInfo = requests.get(url=f"http://ip-api.com/json/{myIP}").json()
    # print(ipInfo)
    print(f"Your ISP: {ipInfo['isp']} \n"
          f"Your location: {ipInfo['lat']}, {ipInfo['lon']}")
    distanceToServer = calculateDistance(ipInfo['lat'], ipInfo['lon'], 47.414259, 8.549612)

    # UZH coordinates: (47.414259, 8.549612)
    print(f"Distance to server is {distanceToServer} kilometers.")
    IPInfoLabel.configure(text=f"Your ISP: {ipInfo['isp']} \n"
                          f"Your location: {ipInfo['lat']}, {ipInfo['lon']}")


# getBasicIPInfo()
window = tk.Tk()
window.geometry("500x500")
getIPButton = tk.Button(text="Retrieve IP Info", command=getBasicIPInfo)
getIPButton.pack()
IPInfoLabel = tk.Label(text="")
IPInfoLabel.pack()
window.mainloop()
