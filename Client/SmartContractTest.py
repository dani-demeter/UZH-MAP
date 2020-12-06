from web3 import Web3
import env

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

myContract = w3.eth.contract(
    address=env.contractAddress, abi=env.contractABI)

print(myContract.functions.get_output().call())

# myContract.functions.addMeasurement(2013, 1369, "ATT", [], 1001, 11, 1001, 16, 1001, 14).transact(
#     {'from': w3.eth.accounts[0], "gas": 4000000})

# back = myContract.functions.getAllMeasurements_ISP("Comcast").call()
# print(back)
