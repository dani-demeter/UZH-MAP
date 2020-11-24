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

import urllib

# IMPORT ENV VARIABLES
import env


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


def prettyPrintPacket(packet):
    print(f"Packet {packet.summary()} with time: {packet.time}")


def dumpToFile(filename, content):
    print(f'Dumping to {filename}')
    outfile = open(filename, 'wb')
    pickle.dump(content, outfile)
    outfile.close()


def scapySniff():
    print("Started sniffing")
    packets = sniff(timeout=7, filter=f'tcp and src host {env.serverIP}')
    print("Finished sniffing")
    collectPackets(packets)


def collectPackets(clientPackets):
    serverPackets = pickle.load(urllib.request.urlopen("http://" + env.serverIP + ":3000/htmlsniff"))
    dumpToFile("serverPacketsByClient", serverPackets)
    dumpToFile("clientPacketsByClient", clientPackets)
    analyzePackets(clientPackets)
    analyzePackets(serverPackets)


def analyzePackets(packets):
    for packet in packets:
        prettyPrintPacket(packet)


def loadPacketsFromFiles():  # FOR DEVELOPMENT
    serverPackets = pickle.load(open("serverPacketsByClient", 'rb'))
    clientPackets = pickle.load(open("clientPacketsByClient", 'rb'))
    for serverPacket in serverPackets:
        print(serverPacket.mysummary())
    print()
    for clientPacket in clientPackets:
        print(clientPacket.mysummary())
    print()
    # print(serverPackets[0].show())
    # print(clientPackets[0].show())
    # print(serverPackets[0][0].chksum)
    # print(clientPackets[0][0].chksum)
    # CHECK FOR MATCHES
    # for serverPacket in serverPackets:
    #     for clientPacket in clientPackets:
    #         if serverPacket[2].seq == clientPacket[2].seq:
    #             print(f"Found a packet match {serverPacket.time} {clientPacket.time}")
    # analyzePackets(clientPackets)
    # print()
    # analyzePackets(serverPackets)


def startSniff():
    thread = Thread(target=scapySniff, args=[])
    thread.start()
    print("Starting sniffing on server")
    r = requests.get("http://" + env.serverIP + ":3000/startsniff")
    time.sleep(1)
    requests.get("http://" + env.serverIP + ":3000/html")


# startSniff()
#loadPacketsFromFiles()

# main()
