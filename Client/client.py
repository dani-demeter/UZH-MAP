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
# import pyshark
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
    getIPButton = tk.Button(window,
                            text="Retrieve IP Info", command=lambda: IPInfoLabel.configure(text=getBasicIPInfo()))
    getIPButton.place(x=0, y=0)
    IPInfoLabel = tk.Label(window, text="")
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
    distanceToServer = calculateDistance(
        ipInfo['lat'], ipInfo['lon'], 47.414259, 8.549612)

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
        print(
            f'Your average {dataType} request took {averageRequestTime/numberOfTries} ms')
        print(f'{dataType} Speed at {averageDataSpeed/numberOfTries} bytes/ms')


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


def cleanPackets(packets):  # removes all ssh files and only shows packets with load
    res = []
    for packet in packets:
        if TCP in packet:
            if Raw in packet:
                if packet.sport == 3000:
                    res.append(packet)
    return res


def startSniff(fileTypes):
    for fileType in fileTypes:
        thread = Thread(target=scapySniff, args=[fileType])
        thread.start()
        startServerSniffAndSendFile(fileType)
        thread.join()
    loadPacketsFromFiles(fileTypes)


def scapySniff(fileType):
    print(f"Started {fileType} sniffing on client")
    packets = sniff(timeout=7, filter=f'tcp and src host {env.serverIP}')
    print(f"Finished {fileType} sniffing on client")
    collectPackets(packets, fileType)


def collectPackets(clientPackets, fileType):
    serverPackets = pickle.load(urllib.request.urlopen(
        "http://" + env.serverIP + ":3000/packets"))
    serverPackets = cleanPackets(serverPackets)
    clientPackets = cleanPackets(clientPackets)
    dumpToFile("pickle/serverPackets_"+fileType, serverPackets)
    dumpToFile("pickle/clientPackets_"+fileType, clientPackets)
    # analyzePackets(serverPackets, clientPackets)


def startServerSniffAndSendFile(fileType):
    print(f"Starting {fileType} sniffing on server")
    requests.get("http://" + env.serverIP + ":3000/startsniff")
    time.sleep(1)
    requests.get("http://" + env.serverIP + ":3000/" + fileType)


def loadPacketsFromFiles(fileTypes):
    collectedPackets = {}
    for fileType in fileTypes:
        serverPackets = pickle.load(
            open("pickle/serverPackets_"+fileType, 'rb'))
        clientPackets = pickle.load(
            open("pickle/clientPackets_"+fileType, 'rb'))
        collectedPackets[fileType] = (serverPackets, clientPackets)
    extractMetrics(collectedPackets)


def extractMetrics(collectedPackets):
    metricDictionary = {}
    for fileType in collectedPackets:
        serverPackets = collectedPackets[fileType][0]
        clientPackets = collectedPackets[fileType][1]
        thisFileTypeMetrics = {}
        for serverPacket in serverPackets:
            for clientPacket in clientPackets:
                if serverPacket[Raw] == clientPacket[Raw]:
                    key = str(serverPacket[Raw])
                    if key in thisFileTypeMetrics:
                        thisFileTypeMetrics[key]['latency'].append(
                            serverPacket.time - clientPacket.time)
                    else:
                        thisFileTypeMetrics[key] = {
                            'latency': [serverPacket.time - clientPacket.time]
                        }
        metricDictionary[fileType] = thisFileTypeMetrics
    dumpToFile("pickle/metricDictionary", metricDictionary)
    analyzeMetrics(metricDictionary)


def loadMetricDictionaryFromFile():  # FOR DEVELOPMENT
    metricDictionary = pickle.load(
        open("pickle/metricDictionary", 'rb'))
    analyzeMetrics(metricDictionary)


def analyzeMetrics(metricDictionary):
    for fileType in metricDictionary:
        numPackets = 0
        totalLatency = 0
        totalLatencySq = 0
        thisFileTypeMetrics = metricDictionary[fileType]
        for matchedPacket in thisFileTypeMetrics:
            numPackets += len(thisFileTypeMetrics[matchedPacket]['latency'])
            for latency in thisFileTypeMetrics[matchedPacket]['latency']:
                totalLatency += latency
                totalLatencySq += latency * latency
        if numPackets > 1:
            print(f"Number of packets matched for {fileType} is {numPackets}")
            jitter = (totalLatencySq - (totalLatency *
                                        totalLatency / numPackets)) / (numPackets - 1)
            print(f"Your {fileType} jitter is {jitter*1000} ms")
            print(
                f"Your {fileType} average latency is {totalLatency*1000/numPackets} ms")
        else:
            print(f"Metrics could not be calculated for {fileType}")


# def checkPorts():
    # listPorts = ["80","443"]
    # for p in listPorts:
    # try
    # r = requests.get(f'http://portquiz.net:{p}')
    # except
    # failedports = []
# startSniff(["html", "video"])
# print(gmtime(getTime()))
loadPacketsFromFiles(["html", "video"])
# loadMetricDictionaryFromFile()
# doTraceroute()
# main()
