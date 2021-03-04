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
import speedtest
import urllib
from ftplib import FTP
# IMPORT ENV VARIABLES
import env
import sys
from ast import literal_eval as make_tuple
import json


myIP = ""
ipInfo = {}


def main():
    # getBasicIPInfo()
    window = tk.Tk()
    window.geometry("500x500")
    startButton = tk.Button(window, text="Start measurements")
    startButton['command'] = starting
    # getIPButton = tk.Button(window,
    #                         text="Retrieve IP Info", command=lambda: IPInfoLabel.configure(text=getBasicIPInfo()))
    # getIPButton.place(x=0, y=0)
    # IPInfoLabel = tk.Label(window, text="")
    # IPInfoLabel.pack()
    startButton.pack()
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
    # print(f"My public IP address is: {myIP}")

    # GET INFO BASED ON IP
    ipInfo = requests.get(url=f"http://ip-api.com/json/{myIP}").json()
    # print(ipInfo)
    print(json.dumps(
        {'tag': 'result', 'type': 'descriptor', 'name': 'isp', 'data': ipInfo['isp']}))
    # print(f"Your ISP: {ipInfo['isp']} \n"
    #       f"Your location: {ipInfo['lat']}, {ipInfo['lon']}")
    distanceToServer = calculateDistance(
        ipInfo['lat'], ipInfo['lon'], 47.414259, 8.549612)
    print(json.dumps(
        {'tag': 'result', 'type': 'descriptor', 'name': 'dist2server', 'data': distanceToServer}))

    # UZH coordinates: (47.414259, 8.549612)
    # print(f"Distance to server is {distanceToServer} kilometers.")
    # IPInfoLabel.configure(text=f"Your ISP: {ipInfo['isp']} \n"
    #                       f"Your location: {ipInfo['lat']}, {ipInfo['lon']}")
    # return (f"Your ISP: {ipInfo['isp']} \n"
    #         f"Your location: {ipInfo['lat']}, {ipInfo['lon']}")


# def getTime():
#     return int(round(time.time() * 1000))


# def getAverageDataResponses():
#     numberOfTries = 10
#     dataTypes = ["HTML"]
#     for dataType in dataTypes:
#         averageRequestTime = 0
#         averageDataSpeed = 0
#         for i in range(numberOfTries):
#             test = requests.get(f'http://{env.serverIP}:3000/{dataType}')
#             requestTime = test.elapsed / datetime.timedelta(milliseconds=1)
#             averageRequestTime += requestTime
#             averageDataSpeed += len(test.content) / requestTime
#         print(
#             f'Your average {dataType} request took {averageRequestTime/numberOfTries} ms')
#         print(f'{dataType} Speed at {averageDataSpeed/numberOfTries} bytes/ms')


# def doTraceroute():
#     target = [env.serverIP]
#     result, unans = traceroute(target, maxttl=32)


# def prettyPrintPacket(packet):
#     print(f"Packet {packet.summary()} with time: {packet.time}")


def dumpToFile(filename, content):
    # print(f'Dumping to {filename}')
    outfile = open(filename, 'wb')
    pickle.dump(content, outfile)
    outfile.close()


def cleanPackets(packets, fileType):  # removes all ssh files and only shows packets with load
    res = []
    for packet in packets:
        if TCP in packet:
            if Raw in packet:
                if fileType == 'FTP':
                    if packet.sport != 3000 or 'ssh':
                        res.append(packet)
                else:
                    if packet.sport == 3000 or packet.sport == 80:
                        res.append(packet)
    return res


def startSniff(fileTypes, port='80', ftp='video'):
    for fileType in fileTypes:
        thread = Thread(target=scapySniff, args=[fileType])
        thread.start()
        startServerSniffAndSendFile(fileType, port, ftp)
        thread.join()
    loadPacketsFromFiles(fileTypes)


def scapySniff(fileType):
    # print(f"Started {fileType} sniffing on client")
    if fileType == 'video' or 'html':
        packets = sniff(timeout=10, filter=f'tcp and src host {env.serverIP}')
        # print(f"Finished {fileType} sniffing on client")
        collectPackets(packets, fileType)
    else:
        packets = sniff(timeout=10, filter=f'tcp and src host {env.serverIP}')
        # print(f"Finished {fileType} sniffing on client")
        collectPackets(packets, fileType)


def collectPackets(clientPackets, fileType):
    serverPackets = pickle.load(urllib.request.urlopen(
        "http://" + env.serverIP + ":3000/packets"))
    serverPackets = cleanPackets(serverPackets, fileType)
    clientPackets = cleanPackets(clientPackets, fileType)
    dumpToFile("pickle/serverPackets_"+fileType, serverPackets)
    dumpToFile("pickle/clientPackets_"+fileType, clientPackets)
    #calculateJitter(serverPackets, clientPackets)


def startServerSniffAndSendFile(fileType, port, ftp):
    if fileType == 'FTP':
        # print(f"Starting {fileType} sniffing on server")
        r = requests.get("http://" + env.serverIP + ":3000/startsniff")
        time.sleep(1)
        getFTPfile(ftp)
    elif fileType == 'html':
        # print(f"Starting {fileType} sniffing on server")
        requests.get("http://" + env.serverIP + ":3000/startsniff")
        time.sleep(1)
        for i in range(20):
            requests.get("http://" + env.serverIP +
                         ":" + port + "/" + fileType)
    else:
        # print(f"Starting {fileType} sniffing on server")
        requests.get("http://" + env.serverIP + ":3000/startsniff")
        time.sleep(1)
        requests.get("http://" + env.serverIP + ":" + port + "/" + fileType)
        requests.get("http://" + env.serverIP + ":80/" + fileType)


def getFTPfile(fileType):
    ftp = FTP(f'{env.serverIP}')
    ftp.login()
    ftp.cwd('/pub')
    if fileType == 'video':
        filename = 'preview.mp4'
        localfile = open(filename, 'wb')
        ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
        ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    elif fileType == 'html':
        filename = 'index.html'
        localfile = open(filename, 'wb')
        for i in range(20):
            ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    # delete
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
    # extractMetrics(collectedPackets)


# def extractMetrics(collectedPackets):
#     metricDictionary = {}
#     for fileType in collectedPackets:
#         serverPackets = collectedPackets[fileType][0]
#         clientPackets = collectedPackets[fileType][1]
#         thisFileTypeMetrics = {}
#         for serverPacket in serverPackets:
#             for clientPacket in clientPackets:
#                 if serverPacket[Raw] == clientPacket[Raw]:
#                     key = str(serverPacket[Raw])
#                     if key in thisFileTypeMetrics:
#                         thisFileTypeMetrics[key]['latency'].append(
#                             serverPacket.time - clientPacket.time)
#                     else:
#                         thisFileTypeMetrics[key] = {
#                             'latency': [serverPacket.time - clientPacket.time]
#                         }
#         metricDictionary[fileType] = thisFileTypeMetrics
#     dumpToFile("pickle/metricDictionary", metricDictionary)
#     analyzeMetrics(metricDictionary)


# def loadMetricDictionaryFromFile():  # FOR DEVELOPMENT
#     metricDictionary = pickle.load(
#         open("pickle/metricDictionary", 'rb'))
#     analyzeMetrics(metricDictionary)


# def analyzeMetrics(metricDictionary):
#     for fileType in metricDictionary:
#         numPackets = 0
#         totalLatency = 0
#         totalLatencySq = 0
#         thisFileTypeMetrics = metricDictionary[fileType]
#         for matchedPacket in thisFileTypeMetrics:
#             numPackets += len(thisFileTypeMetrics[matchedPacket]['latency'])
#             for latency in thisFileTypeMetrics[matchedPacket]['latency']:
#                 totalLatency += latency
#                 totalLatencySq += latency * latency
#         if numPackets > 1:
#             print(f"Number of packets matched for {fileType} is {numPackets}")
#             jitter = (totalLatencySq - (totalLatency *
#                                         totalLatency / numPackets)) / (numPackets - 1)
#             print(f"Your {fileType} jitter is {jitter*1000} ms")
#             print(
#                 f"Your {fileType} average latency is {totalLatency*1000/numPackets} ms")
#         else:
#             print(f"Metrics could not be calculated for {fileType}")


def calculatelatency():
    emptyl = []
    latencylist = []
    for i in range(20):
        time_b = time.time()
        r = requests.get("http://" + env.serverIP + ":3000/ping")
        time_a = time.time()
        latency = time_a - time_b
        latencylist.append(latency)
        factor = latency/2
        #numb = r.content.decode()
        #numb = float(numb)
        #difference = (time_b + factor) - numb
        # print(difference)
        # emptyl.append(difference)
    #averageTimeDiff = sum(emptyl) / len(emptyl)
    averagelatency = (sum(latencylist) / len(latencylist))/2
    # print(averagelatency)
    return averagelatency


def calculateJitter(serverp, clientp, latency, treshhold=0):
    thisFileTypeMetrics = {}
    lenserver = len(serverp)
    lenclient = len(clientp)
    times = serverp[lenserver-1].time - serverp[0].time
    timec = clientp[lenclient-1].time - clientp[1].time
    jitter = abs(timec-times)
    # print(timec-times)
    return jitter/latency
    # print(serverp[0][Raw])
    # print(clientp[0][Raw])

    # get latency of the first packet
    # calculate jitter
    # if jitter is higher than 30% of the latency report jitter and add to blockchain


def checkPorts(newlist=[]):
    if newlist == []:
        listports = [20, 21, 22, 23, 25, 53, 80,
                     110, 119, 123, 143, 161, 194, 443]
    else:
        listports = newlist
    failed = []
    worked = []
    for port in listports:
        try:
            r = requests.get(f'http://portquiz.net:{port}', timeout=1)
            worked.append(port)
        except:
            failed.append(port)
    # print(failed)
    return failed, worked


def loadPackets(part):
    collectedPackets = {}
    serverPackets = pickle.load(
        open("pickle/serverPackets_" + part, 'rb'))
    clientPackets = pickle.load(
        open("pickle/clientPackets_" + part, 'rb'))
    # print(len(clientPackets))
    #timediff, latency = calculateTimediff()
    # print(latency)
    return clientPackets, serverPackets


def calculatepacketloss(serverp):
    i = 1
    packetloss = 0
    for p in serverp:
        for x in range(100):
            if i+x <= len(serverp)-1:
                if p[TCP].seq == serverp[i+x][TCP].seq:
                    packetloss = packetloss + 1
                    # print("found packet duplicate")
        i = i + 1
    # print(i)
    return packetloss


def calculatethroughput(packets):
    tottime = packets[len(packets)-1].time - packets[1].time
    # print(tottime)
    total = 0
    for p in packets:
        total = total + p[IP].len
    throughput = total/(tottime*100000)
    return throughput


def speedtestdown():
    s = speedtest.Speedtest()
    return s.download()/1000000


def starting(ports2check):
    numberOfSteps = 9
    getBasicIPInfo()
    # latency
    print(json.dumps(
        {'tag': 'log', 'message': 'Starting latency calculation'}))
    print(json.dumps(
        {'tag': 'progress', 'completed': 0, 'total': numberOfSteps}))
    sys.stdout.flush()

    latency = calculatelatency()
    print(json.dumps(
        {'tag': 'progress', 'completed': 1, 'total': numberOfSteps}))
    # throughput speedtest
    print(json.dumps(
        {'tag': 'log', 'message': 'Starting speedtest'}))
    sys.stdout.flush()

    speed = speedtestdown()
    print(json.dumps(
        {'tag': 'progress', 'completed': 2, 'total': numberOfSteps}))
    # portblocking
    print(json.dumps(
        {'tag': 'log', 'message': 'Starting port blocking'}))
    sys.stdout.flush()

    failed, worked = checkPorts(ports2check)
    print(json.dumps(
        {'tag': 'progress', 'completed': 3, 'total': numberOfSteps}))
    # throughput once video
    print(json.dumps(
        {'tag': 'log', 'message': 'Starting video throughput calculation'}))

    sys.stdout.flush()
    startSniff(["video"])
    client, server = loadPackets('video')
    throughput = calculatethroughput(client)
    print(json.dumps(
        {'tag': 'progress', 'completed': 4, 'total': numberOfSteps}))
    # jitter 80 video
    print(json.dumps(
        {'tag': 'log', 'message': 'Starting video jitter calculation on port 80'}))
    sys.stdout.flush()
    lossvideo80 = calculatepacketloss(server)
    jitter = calculateJitter(server, client, latency)
    print(json.dumps(
        {'tag': 'progress', 'completed': 5, 'total': numberOfSteps}))
    # html
    print(json.dumps(
        {'tag': 'log', 'message': 'Starting html calculation'}))
    sys.stdout.flush()
    startSniff(["html"])
    client, server = loadPackets('html')
    jitterhtml = calculateJitter(server, client, latency)
    losshtml80 = calculatepacketloss(server)
    print(json.dumps(
        {'tag': 'progress', 'completed': 6, 'total': numberOfSteps}))
    # html 3000
    print(json.dumps(
        {'tag': 'log', 'message': 'Starting video calculation on port 3000'}))
    sys.stdout.flush()
    startSniff(["video"], port='3000')
    client, server = loadPackets('video')
    jittervideo3 = calculateJitter(server, client, latency)
    losshtml3000 = calculatepacketloss(server)
    print(json.dumps(
        {'tag': 'progress', 'completed': 7, 'total': numberOfSteps}))
    # ftp
    print(json.dumps(
        {'tag': 'log', 'message': 'Starting FTP video'}))
    sys.stdout.flush()
    startSniff(["FTP"], ftp='video')
    client, server = loadPackets('FTP')
    jittervideoftp = calculateJitter(server, client, latency)
    lossftp = calculatepacketloss(server)

    print(json.dumps(
        {'tag': 'log', 'message': 'Starting FTP html'}))
    print(json.dumps(
        {'tag': 'progress', 'completed': 8, 'total': numberOfSteps}))
    startSniff(["FTP"], ftp='html')
    client, server = loadPackets('FTP')
    jittervideoftp = calculateJitter(server, client, latency)
    lossftp = calculatepacketloss(server)
    print(json.dumps(
        {'tag': 'progress', 'completed': 9, 'total': numberOfSteps}))

    print(json.dumps(
        {'tag': 'result', 'type': 'port', 'name': 'failed', 'data': failed}))
    print(json.dumps(
        {'tag': 'result', 'type': 'port', 'name': 'success', 'data': worked}))

    print(json.dumps(
        {'tag': 'result', 'type': 'descriptor', 'name': 'ping', 'data': latency}))
    print(json.dumps(
        {'tag': 'result', 'type': 'generic', 'name': 'osThroughput', 'data': throughput}))
    print(json.dumps(
        {'tag': 'result', 'type': 'generic', 'name': 'speedtestThroughput', 'data': speed}))
    print(json.dumps(
        {'tag': 'result', 'type': 'video80', 'name': 'avgJitter', 'data': jitter}))
    print(json.dumps(
        {'tag': 'result', 'type': 'html80', 'name': 'avgJitter', 'data': jitterhtml}))
    print(json.dumps(
        {'tag': 'result', 'type': 'video80', 'name': 'packetLoss', 'data': lossvideo80}))
    print(json.dumps(
        {'tag': 'result', 'type': 'html80', 'name': 'packetLoss', 'data': losshtml80}))
    print(json.dumps(
        {'tag': 'result', 'type': 'video3000', 'name': 'avgJitter', 'data': jittervideo3}))
    print(json.dumps(
        {'tag': 'result', 'type': 'html3000', 'name': 'packetLoss', 'data': losshtml3000}))
    print(json.dumps(
        {'tag': 'result', 'type': 'ftp', 'name': 'avgJitter', 'data': jittervideoftp}))
    print(json.dumps(
        {'tag': 'result', 'type': 'ftp', 'name': 'packetLoss', 'data': lossftp}))
    print('exit')

    # print(f'failed ports: {failed}')
    # print(f'latency is {latency}')
    # print(f'thorughput os {throughput}')
    # print(f'speedtest throughput is {speed}')
    # print(f'jitter video 80 is {jitter}')
    # print(f'jitter html 80 is {jitterhtml}')
    # print(f'loss video 80 is {lossvideo80}')
    # print(f'loss html 80 is {losshtml80}')
    # print(f'jitter video 3000 is {jittervideo3}')

    # I think this should be html loss, based on the variable name
    # print(f'loss video 3000 is {losshtml3000}')
    # print(f'jitter ftp is {jittervideoftp}')
    # print(f'loss video ftp is {lossftp}')
    sys.stdout.flush()


# def startmain():
#     timediff, latency = calculateTimediff()

    # calculateJitter(serverPackets,clientPackets,latency)
#p = loadPackets()
# calculatepacketloss(p)
# do latency, port blocking and throughput, then do video on 80 , packetloss , then do on 3000, then do 3000 text
# once ftp
##
# startSniff(["html", "video"])
# print(gmtime(getTime()))
# loadPacketsFromFiles(["html", "video"])
# loadMetricDictionaryFromFile()
# doTraceroute()
ports2check = []
if len(sys.argv) > 0:
    # print(sys.argv)
    list(make_tuple(sys.argv[1]))
# ports2check = list(make_tuple(sys.argv[1])) if len(sys.argv) > 0 else []
ports2check = map(lambda x: int(x), ports2check)
starting(ports2check)
