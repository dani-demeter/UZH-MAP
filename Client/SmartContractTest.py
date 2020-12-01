from web3 import Web3
import env

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))


myContract = w3.eth.contract(
    address=env.contractAddress, abi=env.contractABI)

print(myContract.functions.get_output().call())

# myContract.functions.addUserInfo(2000, 1313).transact(
#     {'from': w3.eth.accounts[0], "gas": 4000000})

back = myContract.functions.getUserInfos().call()
print(back)
