from web3 import Web3
import env
import sys
import json

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

myContract = w3.eth.contract(
    address=env.contractAddress, abi=env.contractABI)


def placeBounty():
    bountyType = sys.argv[2]
    bountyReq = sys.argv[3]
    bountyNumRep = int(sys.argv[4])
    bountyVal = int(sys.argv[5])*1000  # pwei -> ethers
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
    print("placing a bounty with:", bountyTypeSwitch[bountyType],
          bountyReq, bountyNumRep, bountyVal)
    successfullyCreatedBounty = myContract.functions.placeBounty(bountyVal, bountyNumRep, bountyType, (bountyReq).encode('utf-8')).transact(
        {'from': w3.eth.accounts[0], "value": bountyVal*bountyNumRep})
    print("Successfully created bounty:", successfullyCreatedBounty)
    sys.stdout.flush()


command = sys.argv[1]
commandSwitch = {
    'placeBounty': placeBounty
}
commandSwitch[command]()


# print(myContract.functions.get_output().call())

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
