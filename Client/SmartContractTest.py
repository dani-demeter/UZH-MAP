from web3 import Web3
import env
import sys
import json
import re

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

myContract = w3.eth.contract(
    address=env.contractAddress, abi=env.contractABI)
# regex = re.compile('[^a-zA-Z]')


def placeBounty():
    bountyType = sys.argv[2]
    bountyReq = sys.argv[3]
    bountyNumRep = int(sys.argv[4])
    bountyVal = int(sys.argv[5]) * 1000  # PWEI
    # TODO: get smart contract address & abi from server
    # if get smart contract address == saved smart contract address:
    #   use saved abi
    # else:
    #   download new abi and address
    bountyTypeSwitch = {
        "Distance": "d2s",
        "Ping": "ping",
        "ISP": "ISP"
    }
    print("Placing a bounty on:", bountyTypeSwitch[bountyType], bountyReq)
    if type(bountyReq) is str:
        bountyReq = bountyReq.replace(" ", "")
    successfullyCreatedBounty = myContract.functions.placeBounty(bountyVal, bountyNumRep, bountyType, (bountyReq).encode('utf-8')).transact(
        {'from': w3.eth.accounts[0], "value": bountyVal*bountyNumRep})
    print("Successfully created bounty:", successfullyCreatedBounty)
    sys.stdout.flush()


def addNewTestDescriptors():
    d2s = int(sys.argv[2])
    ping = int(sys.argv[3])
    isp = sys.argv[4]
    myContract.functions.addNewTestDescriptors(d2s, ping, isp).transact(
        {'from': w3.eth.accounts[0], "gas": 4000000})


def addNewMeasurement():
    mediaType = sys.argv[2]
    metricType = sys.argv[3]
    measurementValue = int(sys.argv[4])
    myContract.functions.addNewMeasurement(mediaType, metricType, measurementValue).transact(
        {'from': w3.eth.accounts[0], "gas": 4000000})
    print("Successfully added", mediaType, metricType)


def getMeasurementResults():
    addr = sys.argv[2]
    index = int(sys.argv[3])
    measurementResult = myContract.functions.getMeasurementResults(
        addr, index).call()
    print("Measurement results:", measurementResult)


def getBounty():
    addr = sys.argv[2]
    timest = int(sys.argv[3])
    bounty = myContract.functions.getBounty(addr, timest).call()
    print(bounty)


def getBountyTimestamps():
    addr = sys.argv[2]
    bountyTimestamps = myContract.functions.getAddressBountyTimestamps(
        addr).call()
    print(bountyTimestamps)


def getQualifiedBounties():
    d2s = int(sys.argv[2])
    ping = int(sys.argv[3])
    isp = (sys.argv[4].replace(" ", "")).encode('utf-8')
    qualifiedBounties = myContract.functions.getQualifiedBounties(
        d2s, ping, isp).call()
    print("Qualified bounties:", qualifiedBounties)


def filterMeasurementsByISP():
    targetISP = sys.argv[2]
    measurementsWithISP = myContract.functions.filterMeasurementsByISP(
        targetISP).call()
    print(measurementsWithISP)


def filterMeasurementsByPing():
    targetPing = int(sys.argv[2])
    measurementsWithPing = myContract.functions.filterMeasurementsByPing(
        targetPing).call()
    print(measurementsWithPing)


def filterMeasurementsByDistance():
    targetDist = int(sys.argv[2])
    measurementsWithDist = myContract.functions.filterMeasurementsByDistance(
        targetDist).call()
    print(measurementsWithDist)


def estimateCost():
    message = myContract.functions.addNewTestDescriptors(1000, 500, "Comcast Integrated Whatever").estimateGas(
        {'from': w3.eth.accounts[0]})
    print("estimated gas:", message)
    # print(json.dumps({'tag': 'log', 'message': str(message)}))


def addMeasurements(n):
    for i in range(n):
        myContract.functions.addNewTestDescriptors(1000, 500, "ATT").transact(
            {'from': w3.eth.accounts[0], "gas": 4000000})
        myContract.functions.addNewMeasurement("html", "avgLatency", 123).transact(
            {'from': w3.eth.accounts[0], "gas": 4000000})
        myContract.functions.addNewMeasurement("html", "avgJitter", 145).transact(
            {'from': w3.eth.accounts[0], "gas": 4000000})
        myContract.functions.addNewMeasurement("video", "avgLatency", 213).transact(
            {'from': w3.eth.accounts[0], "gas": 4000000})
        myContract.functions.addNewMeasurement("video", "avgJitter", 245).transact(
            {'from': w3.eth.accounts[0], "gas": 4000000})
        myContract.functions.addNewMeasurement("audio", "avgLatency", 156).transact(
            {'from': w3.eth.accounts[0], "gas": 4000000})
        myContract.functions.addNewMeasurement("audio", "avgJitter", 516).transact(
            {'from': w3.eth.accounts[0], "gas": 4000000})


def test():
    print(myContract.functions.addNewTestDescriptors(1000, 500, "ATT").estimateGas(
        {'from': w3.eth.accounts[0]}))
    # myContract.functions.addNewTestDescriptors(
    #     100, 500, "ATT").transact({'from': w3.eth.accounts[0]})
    print(myContract.functions.addNewMeasurement("html", "avgLatency", 123).estimateGas(
        {'from': w3.eth.accounts[0]}))
    print(myContract.functions.addNewMeasurement("html", "avgJitter", 145).estimateGas(
        {'from': w3.eth.accounts[0]}))
    print(myContract.functions.addNewMeasurement("video", "avgLatency", 213).estimateGas(
        {'from': w3.eth.accounts[0]}))
    print(myContract.functions.addNewMeasurement("video", "avgJitter", 245).estimateGas(
        {'from': w3.eth.accounts[0]}))
    print(myContract.functions.addNewMeasurement("audio", "avgLatency", 156).estimateGas(
        {'from': w3.eth.accounts[0]}))
    print(myContract.functions.addNewMeasurement("audio", "avgJitter", 516).estimateGas(
        {'from': w3.eth.accounts[0]}))


def finishMeasurements():
    results = json.loads(sys.argv[2])
    dist2server = int(results['descriptor']['dist2server'])
    ping = int(results['descriptor']['ping'] * 1000)
    isp = results['descriptor']['isp']
    print(json.dumps(
        {'tag': 'log', 'message': 'Starting to store results on the blockchain'}))
    myContract.functions.addNewTestDescriptors(dist2server, ping, isp).transact(
        {'from': w3.eth.accounts[0], "gas": 4000000})
    for resultType in results:
        if resultType != 'descriptor' and resultType != 'port':
            for resultName in results[resultType]:
                print(json.dumps({'tag': 'log', 'message': 'About to store: ' +
                                  resultType + ' ' + resultName + ' ' + str(results[resultType][resultName])}))
                myContract.functions.addNewMeasurement(resultType, resultName, int(float(results[resultType][resultName])*1000)).transact(
                    {'from': w3.eth.accounts[0], "gas": 4000000})
    qualifiedBounties = myContract.functions.getQualifiedBounties(
        dist2server, ping, isp.replace(" ", "").encode('utf-8')).call()
    print(json.dumps({'tag': 'log', 'message': 'You have qualified for ' +
                      str(len(qualifiedBounties[0])) + ' bounties'}))
    for ind in range(len(qualifiedBounties[0])):
        myContract.functions.claimBounty(qualifiedBounties[0][ind], int(qualifiedBounties[1][ind])).transact(
            {'from': w3.eth.accounts[0], "gas": 4000000})
        print(json.dumps({'tag': 'log', 'message': 'Collected a bounty'}))

# 0 measurements: 24931 gas
# 1 measurement: 30481
# 10 measurements: 68495
# 20 measurements: 110749
# 50 measurements: 237637
# 100 measurements: 449511

# addNewTestDescriptors cost: 96025 (ATT), 97561 (Comcast Integrated Whatever)


# print(sys.argv)
command = sys.argv[1]
commandSwitch = {
    'placeBounty': placeBounty,
    'getQualifiedBounties': getQualifiedBounties,
    'addNewTestDescriptors': addNewTestDescriptors,
    'getMeasurementResults': getMeasurementResults,
    'filterMeasurementsByISP': filterMeasurementsByISP,
    'filterMeasurementsByPing': filterMeasurementsByPing,
    'filterMeasurementsByDistance': filterMeasurementsByDistance,
    'finishMeasurements': finishMeasurements,
    'getBounty': getBounty,
    'getBountyTimestamps': getBountyTimestamps


}
commandSwitch[command]()
# addMeasurements(1)
# test()

# myContract.functions.addNewTestDescriptors(1000, 500, "ATT", []).transact(
#     {'from': w3.eth.accounts[0], "gas": 4000000})

# myContract.functions.addNewMeasurement("HTML", "jitter", 100)

# back = myContract.functions.filterMeasurementsByISP("ATT").call()
# print(back)

# back = myContract.functions.getQualifiedBounties(
#     1000, 500, ("ATT").encode('utf-8'), []).call()
# # print(back)

# res = myContract.functions.getBounty(back[0][0], back[1][0]).call()
# print(res)
