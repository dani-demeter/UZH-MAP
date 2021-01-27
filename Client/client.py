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
from ftplib import FTP
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


def cleanPackets(packets,fileType):  # removes all ssh files and only shows packets with load
    res = []
    for packet in packets:
        if TCP in packet:
            if Raw in packet:
                if fileType == 'FTP':
                    if packet.sport != 3000 or 'ssh':
                        res.append(packet)
                else:
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
    if fileType == 'video' or 'html':
        packets = sniff(timeout=15, filter=f'tcp and src host {env.serverIP}')
        print(f"Finished {fileType} sniffing on client")
        collectPackets(packets, fileType)
    else:
        packets = sniff(timeout=15, filter=f'tcp src host {env.serverIP}')
        print(f"Finished {fileType} sniffing on client")
        collectPackets(packets, fileType)


def collectPackets(clientPackets, fileType):
    serverPackets = pickle.load(urllib.request.urlopen(
        "http://" + env.serverIP + ":3000/packets"))   
    serverPackets = cleanPackets(serverPackets,fileType)
    clientPackets = cleanPackets(clientPackets,fileType)
    dumpToFile("pickle/serverPackets_"+fileType, serverPackets)
    dumpToFile("pickle/clientPackets_"+fileType, clientPackets)
    calculateJitter(serverPackets, clientPackets)


def startServerSniffAndSendFile(fileType):
    if fileType == 'FTP':
        print(f"Starting {fileType} sniffing on server")
        r = requests.get("http://" + env.serverIP + ":3000/startsniff")
        time.sleep(1)
        getFTPfile()
    else:
        print(f"Starting {fileType} sniffing on server")
        requests.get("http://" + env.serverIP + ":3000/startsniff")
        time.sleep(1)
        requests.get("http://" + env.serverIP + ":3000/" + fileType)

def getFTPfile():
    ftp = FTP(f'{env.serverIP}')
    ftp.login()
    ftp.cwd('/pub')
    filename = 'preview.mp4'
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)

    ftp.quit()
    localfile.close()

def loadPacketsFromFiles(fileTypes):
    collectedPackets = {}
    for fileType in fileTypes:
        serverPackets = pickle.load(
            open("pickle/serverPackets_"+fileType, 'rb'))
        clientPackets = pickle.load(
            open("pickle/clientPackets_"+fileType, 'rb'))
        collectedPackets[fileType] = (serverPackets, clientPackets)
    #extractMetrics(collectedPackets)


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
            jitter = (totalLatencySq - (totalLatency *
                                        totalLatency / numPackets)) / (numPackets - 1)
            print(f"Your {fileType} jitter is {jitter*1000} ms")
            print(
                f"Your {fileType} average latency is {totalLatency*1000/numPackets} ms")
        else:
            print(f"Metrics could not be calculated for {fileType}")
            
def calculateTimediff():
    emptyl = []
    latencylist = []
    for i in range(20):
        time_b = time.time()
        r= requests.get("http://" + env.serverIP + ":3000/ping")
        time_a = time.time()
        latency = time_a - time_b
        latencylist.append(latency)
        factor = latency/2
        numb = r.content.decode()
        numb = float(numb)
        difference = (time_b + factor) - numb
        print(difference)
        emptyl.append(difference)
    averageTimeDiff = sum(emptyl) / len(emptyl)
    averagelatency = (sum(latencylist) / len(latencylist))/2
    print(average)
    return averageTimeDiff, averagelatency
    
    
def calculateJitter(serverp,clientp,latency,treshhold = 0):
    thisFileTypeMetrics = {}
    lenserver = len(serverp)
    lenclient = len(clientp)
    times = serverp[lenserver-1].time - serverp[0].time
    timec = clientp[lenclient-1].time - clientp[1].time
    print(timec-times)
    print(serverp[0][Raw])
    print(clientp[0][Raw])
        # get latency of the first packet
        # calculate jitter
        # if jitter is higher than 30% of the latency report jitter and add to blockchain
        
def checkPorts():
    listports = [20,21,22,23,25,53,80,110,119,123,143,161,194,443]
    failed = []
    worked = []
    for port in listports:
        try:
            r = requests.get(f'http://portquiz.net:{port}',timeout= 1)
            worked.append(port)
        except:
            failed.append(port)
    print(failed)
    return failed,worked
    
    
def loadPackets():
    collectedPackets = {}
    serverPackets = pickle.load(
        open("pickle/serverPackets_video", 'rb'))
    clientPackets = pickle.load(
        open("pickle/clientPackets_video", 'rb'))
    print(len(clientPackets))
    #timediff, latency = calculateTimediff()
    #print(latency)
    return serverPackets
    
    
def calculatepacketloss(serverp):
    i = 0
    packetloss = 0
    for p in serverp:
        for x in range(len(serverp)-(i+1)):
            if p[TCP].seq == serverp[i+1][TCP].seq:
                packetloss = packetloss + 1
                print("found packet duplicate")
            
        i = i + 1
    print(i)
    return packetloss
         
def startmain():
    timediff, latency = calculateTimediff()
    #calculateJitter(serverPackets,clientPackets,latency)
p = loadPackets()
calculatepacketloss(p)
#### do latency, port blocking and throughput, then do video on 80 , packetloss , then do on 3000, then do 3000 text
## once ftp
## 
# startSniff(["html", "video"])
# print(gmtime(getTime()))
# loadPacketsFromFiles()
# loadMetricDictionaryFromFile()
# doTraceroute()
#main()
