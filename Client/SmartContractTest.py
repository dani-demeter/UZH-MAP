from web3 import Web3
import env

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

myContract = w3.eth.contract(
    address=env.contractAddress, abi=env.contractABI)

# print(myContract.functions.get_output().call())

# myContract.functions.addNewTestDescriptors(1000, 500, "ATT", []).transact(
#     {'from': w3.eth.accounts[0], "gas": 4000000})

# myContract.functions.addNewMeasurement("HTML", "jitter", 100)

# back = myContract.functions.filterMeasurementsByISP("ATT").call()
# print(back)

# myContract.functions.placeBounty(2, 3, "ISP", ("ATT").encode('utf-8')).transact(
#     {'from': w3.eth.accounts[0], "value": 6})

back = myContract.functions.getQualifiedBounties(
    1000, 500, ("ATT").encode('utf-8'), []).call()
# print(back)

res = myContract.functions.getBounty(back[0][0], back[1][0]).call()
print(res)
