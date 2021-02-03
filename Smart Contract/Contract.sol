// Solidity program to demonstrate  
pragma solidity ^0.4.26; 
pragma experimental ABIEncoderV2;
  
// Creating a contract 
contract TestContract   
{ 
    struct MeasurementResult {
        int64 dist2server;
        int256 ping;
        string ISP;
        string[] hops;
        mapping(string => mapping(string => int256)) collectedMetrics;
    }
    
    struct Bounty {
        uint16 repeats;
        uint256 bountyValue;
        string bountyType;
        bytes32 bountyReq;
    }
    
    
    mapping(address => MeasurementResult[]) measurementResults;
    address[] addressesWithMeasurements;
    uint256 numberOfMeasurements = 0;
    
    mapping(address => mapping(uint => Bounty)) bounties;
    mapping(address => bool) addressHasBounties;
    address[] addressesWithBounties;
    mapping(address => uint[]) bountyAddressTimestamps;
    uint256 numberOfBounties = 0;
    
    function addNewTestDescriptors(int64 d2s, int256 png, string isp, string[] hops2server) public returns(uint256){
        if(measurementResults[msg.sender].length == 0){
            addressesWithMeasurements.push(msg.sender);
        }
        measurementResults[msg.sender].push(MeasurementResult({dist2server:d2s, ping:png, ISP: isp, hops: hops2server}));
        numberOfMeasurements++;
        return measurementResults[msg.sender].length;
    }
    
    function addNewMeasurement(string mediaType, string metricType, int256 measurementValue) public returns(uint256){
        require(measurementResults[msg.sender].length > 0);
        measurementResults[msg.sender][measurementResults[msg.sender].length - 1].collectedMetrics[mediaType][metricType] = measurementValue;
        return 0;
    }
    
    function filterMeasurementsByISP(string filterISP) public view returns (address[], uint256[]){
        address[] memory resAddressesFull = new address[](numberOfMeasurements);
        uint256[] memory resIndexesFull = new uint256[](numberOfMeasurements);
        bytes32 kFilterISP = keccak256(abi.encodePacked(filterISP));
        uint256 counter = 0;
        for (uint i=0; i<addressesWithMeasurements.length; i++) {
            for(uint j = 0; j<measurementResults[addressesWithMeasurements[i]].length; j++){
                if(keccak256(abi.encodePacked(measurementResults[addressesWithMeasurements[i]][j].ISP)) == kFilterISP){
                    resAddressesFull[counter] = addressesWithMeasurements[i];
                    resIndexesFull[counter] = j;
                    counter += 1;
                }
            }
        }
        address[] memory resAddresses = new address[](counter);
        uint256[] memory resIndexes = new uint256[](counter);
        for(uint k = 0; k<counter; k++){
            resAddresses[k] = resAddressesFull[k];
            resIndexes[k] = resIndexesFull[k];
        }
        return (resAddresses, resIndexes);
    }
    
    function filterMeasurementsByPing(int256 testPing) public view returns (address[], uint256[]){
        address[] memory resAddressesFull = new address[](numberOfMeasurements);
        uint256[] memory resIndexesFull = new uint256[](numberOfMeasurements);
        int256 lowerBound = testPing - 10;
        int256 upperBound = testPing + 10;
        uint256 counter = 0;
        for (uint i=0; i<addressesWithMeasurements.length; i++) {
            for(uint j = 0; j<measurementResults[addressesWithMeasurements[i]].length; j++){
                if(lowerBound <= measurementResults[addressesWithMeasurements[i]][j].ping && measurementResults[addressesWithMeasurements[i]][j].ping <= upperBound){
                    resAddressesFull[counter] = addressesWithMeasurements[i];
                    resIndexesFull[counter] = j;
                    counter += 1;
                }
            }
        }
        address[] memory resAddresses = new address[](counter);
        uint256[] memory resIndexes = new uint256[](counter);
        for(uint k = 0; k<counter; k++){
            resAddresses[k] = resAddressesFull[k];
            resIndexes[k] = resIndexesFull[k];
        }
        return (resAddresses, resIndexes);
    }
    
    //bounty types: ISP, d2s, ping
    function placeBounty(uint256 valuePerBounty, uint16 numRepeats, string bType, bytes32 bReq) external payable{
        require(msg.value==valuePerBounty*numRepeats);
        if(!addressHasBounties[msg.sender] || bounties[msg.sender][block.timestamp].repeats==0){
            numberOfBounties += 1;
            addressHasBounties[msg.sender] = true;
            addressesWithBounties.push(msg.sender);
            bountyAddressTimestamps[msg.sender].push(block.timestamp);
        }
        bounties[msg.sender][block.timestamp] = Bounty({repeats:numRepeats, bountyType:bType, bountyReq:bReq, bountyValue:msg.value});
    }
    
    function getQualifiedBounties(int64 d2s, int256 png, bytes32 isp, string[] hops2server) public view returns(address[], uint256[]){
        address[] memory resAddressesFull = new address[](numberOfBounties);
        uint256[] memory resIndexesFull = new uint256[](numberOfBounties);
        
        // bytes32 kFilterISP = keccak256(abi.encodePacked(isp));
        uint256 counter = 0;
        
        for (uint i=0; i<addressesWithBounties.length; i++) {
            for(uint j = 0; j<bountyAddressTimestamps[addressesWithBounties[i]].length; j++){
                bytes32 typeOfBounty = keccak256(abi.encodePacked(bounties[addressesWithBounties[i]][bountyAddressTimestamps[addressesWithBounties[i]][j]].bountyType));
                bytes32 bountyReq = keccak256(abi.encodePacked(bounties[addressesWithBounties[i]][bountyAddressTimestamps[addressesWithBounties[i]][j]].bountyReq));
                if(typeOfBounty == keccak256(abi.encodePacked("ISP")) && bountyReq == keccak256(abi.encodePacked(isp))){
                    resAddressesFull[counter] = addressesWithMeasurements[i];
                    resIndexesFull[counter] = bountyAddressTimestamps[addressesWithBounties[i]][j];
                    counter += 1;
                }else if(typeOfBounty == keccak256(abi.encodePacked("d2s")) 
                            && int(bounties[addressesWithBounties[i]][bountyAddressTimestamps[addressesWithBounties[i]][j]].bountyReq)-100 <= d2s 
                            && int(bounties[addressesWithBounties[i]][bountyAddressTimestamps[addressesWithBounties[i]][j]].bountyReq)+100 >= d2s){
                    resAddressesFull[counter] = addressesWithMeasurements[i];
                    resIndexesFull[counter] = bountyAddressTimestamps[addressesWithBounties[i]][j];
                    counter += 1;
                }else if(typeOfBounty == keccak256(abi.encodePacked("ping")) 
                            && int(bounties[addressesWithBounties[i]][bountyAddressTimestamps[addressesWithBounties[i]][j]].bountyReq)-10 <= png 
                            && int(bounties[addressesWithBounties[i]][bountyAddressTimestamps[addressesWithBounties[i]][j]].bountyReq)+10 >= png){
                    resAddressesFull[counter] = addressesWithMeasurements[i];
                    resIndexesFull[counter] = bountyAddressTimestamps[addressesWithBounties[i]][j];
                    counter += 1;
                }
            }
        }
        address[] memory resAddresses = new address[](counter);
        uint256[] memory resIndexes = new uint256[](counter);
        for(uint k = 0; k<counter; k++){
            resAddresses[k] = resAddressesFull[k];
            resIndexes[k] = resIndexesFull[k];
        }
        return (resAddresses, resIndexes);
    }
    
    function getBounty(address addr, uint timest) public view returns(Bounty){
        require(addressHasBounties[addr] && bounties[addr][timest].repeats>0);
        return bounties[addr][timest];
    }
    
} 
