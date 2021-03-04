# Installation

### Libraries
- [Scapy](https://scapy.readthedocs.io/en/latest/installation.html)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)
- [Pickle](https://docs.python.org/3/library/pickle.html)
- [Speedtest](https://github.com/sivel/speedtest-cli)
- [Web3](https://web3py.readthedocs.io/en/stable/quickstart.html)

### Environment
- There must be an env.py file in the Client subfolder. This file must have three variables declared, with these names: serverIP, contractABI, and contractAddress. 

### To Run
1) Deploy the smart contract to the blockchain. Recommended: [Remix](https://remix.ethereum.org/) and [Ganache](https://www.trufflesuite.com/ganache). The ABI can be found under the Compile tab in the Remix IDE. Once deployed, the contact's new address (and the ABI if necessary) must be updated in the Client/env.py file.
2) The scripts must be interacted with from a terminal window with administrator privileges. This is to ensure that the measurement process has sufficient privileges.
3) The GUI allows for two use cases:
   1) To place bounties
   2) To take a new measurement, collect the NN metrics, commit these to the SC, check for any qualified bounties, and collect them
4)  Other interactions with the SC must be done through the command line. Possible commands:
    1) python Client/SmartContractTest.py getBountyTimestamps $address
        - Get a list of timestamps the $address has placed bounties at
    2) python Client/SmartContractTest.py getBounty $address $timestamp
        - Get the values of the bounty submitted by $address at $timestamp
    3) python Client/SmartContractTest.py getMeasurementResults $address $index
        - Get the test descriptors and metrics collected by $address at $index
    4) python Client/SmartContractTest.py filterMeasurementsByISP $targetISP
        - Get the measurement addresses and indexes with $targetISP
    5) python Client/SmartContractTest.py filterMeasurementsByPing $targetPing
        - Get the measurement addresses and indexes with ping in a range around $targetPing (in ms)
    6) python Client/SmartContractTest.py filterMeasurementsByDistance $targetDistance
        - Get the measurement addresses and indexes with distance in a range around $targetDistance (in km)
  