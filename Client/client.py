# pip install requests
import requests
# pip install scapy
from scapy.all import *
# from scapy.arch.windows import IFACES
from math import sin, cos, sqrt, atan2, radians
import tkinter as tk
import subprocess
import time
import datetime
import pyshark
from threading import Thread
import pickle

# IMPORT ENV VARIABLES
import env
print(env.serverIP)


myIP = ""
ipInfo = {}


def main():
    # getBasicIPInfo()
    window = tk.Tk()
    window.geometry("500x500")
    getIPButton = tk.Button(text="Retrieve IP Info", command=lambda: IPInfoLabel.configure(text=getBasicIPInfo()))
    getIPButton.pack()
    IPInfoLabel = tk.Label(text="")
    IPInfoLabel.pack()
    window.mainloop()


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
    # IPInfoLabel.configure(text=f"Your ISP: {ipInfo['isp']} \n"
    #                       f"Your location: {ipInfo['lat']}, {ipInfo['lon']}")
    return (f"Your ISP: {ipInfo['isp']} \n"
            f"Your location: {ipInfo['lat']}, {ipInfo['lon']}")


def getTime():
    return int(round(time.time() * 1000))


def getAverageDataResponses():
    numberOfTries = 10
    dataTypes = ["HTML"]
    for dataType in dataTypes:
        averageRequestTime = 0
        averageDataSpeed = 0
        for i in range(numberOfTries):
            test = requests.get(f'http://{env.serverIP}:3000/{dataType}')
            requestTime = test.elapsed / datetime.timedelta(milliseconds=1)
            averageRequestTime += requestTime
            averageDataSpeed += len(test.content) / requestTime
        print(f'Your average {dataType} request took {averageRequestTime/numberOfTries} ms')
        print(f'{dataType} Speed at {averageDataSpeed/numberOfTries} bytes/ms')


def pysharkCapture():
    capture = pyshark.LiveCapture()
    capture.display_filter = f"ip.src == {env.serverIP}"

    thread = Thread(target=getAverageDataResponses, args=[])
    thread.start()
    try:
        capture.sniff(timeout=5)  # 10 sec recording of packages
    except:
        pass
    finally:
        print(capture[0].__dict__)
        capture.clear()
        capture.close()


def doTraceroute():
    target = [env.serverIP]
    result, unans = traceroute(target, maxttl=32)


# main()
infile = open("htmlsniff", 'rb')
new_dict = pickle.load(infile)
print(new_dict)
infile.close()
