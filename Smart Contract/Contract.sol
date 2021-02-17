pragma solidity ^0.4.26; 
pragma experimental ABIEncoderV2;
  
contract UZMAPContract   
{ 
    struct MeasurementResult {
        int64 dist2server;
        int256 ping;
        string ISP;
        mapping(bytes32 => mapping(bytes32 => int256)) collectedMetrics;
    }
    
    struct Bounty {
        uint16 repeats;
        uint256 bountyValue;
        string bountyType;
        bytes32 bountyReq;
    }
    
    struct AddressAndIndex {
        address addr;
        uint index;
    }
    
    
    mapping(address => MeasurementResult[]) measurementResults;
    address[] addressesWithMeasurements;
    uint256 numberOfMeasurements = 0;
    
    mapping(address => mapping(uint => Bounty)) bounties;
    mapping(address => mapping(uint => AddressAndIndex[])) bountyMeasurements;
    mapping(address => bool) addressHasBounties;
    address[] addressesWithBounties;
    mapping(address => uint[]) bountyAddressTimestamps;
    uint256 numberOfBounties = 0;
    
    //CONSTANTS
    bytes32[] acceptedMediaTypes = [keccak256(abi.encodePacked("video")), keccak256(abi.encodePacked("audio")), keccak256(abi.encodePacked("html"))];
    bytes32[] acceptedMetricTypes = [keccak256(abi.encodePacked("avgLatency")), keccak256(abi.encodePacked("avgJitter"))]; //ADD MORE
    
    
    function getMeasurementResults(address addr, uint index) public view returns (int64, int256, string, int256[]){
        int256[] memory measurements = new int256[](acceptedMediaTypes.length * acceptedMetricTypes.length);
        uint counter = 0;
        for(uint i = 0; i<acceptedMediaTypes.length; i++){
            for(uint j = 0; j<acceptedMetricTypes.length; j++){
                int256 measurement = measurementResults[addr][index].collectedMetrics[acceptedMediaTypes[i]][acceptedMetricTypes[j]];
                measurements[counter] = measurement;
                counter++;
            }
        }
        return (measurementResults[addr][index].dist2server, measurementResults[addr][index].ping, measurementResults[addr][index].ISP, measurements);
    }
    
    function addNewTestDescriptors(int64 d2s, int256 png, string isp) public returns(uint256){
        if(measurementResults[msg.sender].length == 0){
            addressesWithMeasurements.push(msg.sender);
        }
        measurementResults[msg.sender].push(MeasurementResult({dist2server:d2s, ping:png, ISP: isp}));
        numberOfMeasurements++;
        return measurementResults[msg.sender].length;
    }
    
    function checkMeasurementTypes(string mediaType, string metricType) internal view returns (bool){
        bool mediaTypeChecksOut = false;
        for(uint i = 0; i<acceptedMediaTypes.length; i++){
            if(acceptedMediaTypes[i] == keccak256(abi.encodePacked(mediaType))){
                mediaTypeChecksOut = true;
                break;
            }
        }
        if(!mediaTypeChecksOut) return false;
        
        bool metricTypeChecksOut = false;
        for(uint j = 0; j<acceptedMetricTypes.length; j++){
            if(acceptedMetricTypes[j] == keccak256(abi.encodePacked(metricType))){
                metricTypeChecksOut = true;
                break;
            }
        }
        return metricTypeChecksOut;
    }
    
    function addNewMeasurement(string mediaType, string metricType, int256 measurementValue) public returns(uint256){
        require(measurementResults[msg.sender].length > 0);
        require(checkMeasurementTypes(mediaType, metricType));
        measurementResults[msg.sender][measurementResults[msg.sender].length - 1].collectedMetrics[keccak256(abi.encodePacked(mediaType))][keccak256(abi.encodePacked(metricType))] = measurementValue;
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
    function placeBounty(uint256 valuePerBounty, uint16 numRepeats, string bType, bytes32 bReq) external payable returns (bool){
        if(msg.value!=valuePerBounty*numRepeats){
            return false;
        }
        if(!addressHasBounties[msg.sender] || bounties[msg.sender][block.timestamp].repeats==0){
            numberOfBounties += 1;
            addressHasBounties[msg.sender] = true;
            addressesWithBounties.push(msg.sender);
            bountyAddressTimestamps[msg.sender].push(block.timestamp);
        }
        bounties[msg.sender][block.timestamp] = Bounty({repeats:numRepeats, bountyType:bType, bountyReq:bReq, bountyValue:msg.value});
        return true;
        
    }
    
    function getQualifiedBounties(int64 d2s, int256 png, bytes32 isp) public view returns(address[], uint256[]){
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
    
    function claimBounty(address bountyAddr, uint timest) external returns (bool){
        bool addrHasMeasurements = false;
        for (uint i=0; i<addressesWithMeasurements.length; i++) {
            if(addressesWithMeasurements[i] == msg.sender){
                addrHasMeasurements = true;
                break;
            }
        }
        if(!addrHasMeasurements) return false;
        if(!addressHasBounties[bountyAddr]) return false;
        bool bountyExists = false;
        uint timestIndex;
        for(uint j = 0; j<bountyAddressTimestamps[bountyAddr].length; j++){
            if(bountyAddressTimestamps[bountyAddr][j] == timest){
                bountyExists = true;
                timestIndex = j;
                break;
            }
        }
        if(!bountyExists) return false;
        
        MeasurementResult memory lastMeasurement = measurementResults[msg.sender][measurementResults[msg.sender].length-1];
        bool validClaim = false;
        bytes32 typeOfBountyHash = keccak256(abi.encodePacked(bounties[bountyAddr][timest].bountyType));
        bytes32 bountyReqHash = keccak256(abi.encodePacked(bounties[bountyAddr][timest].bountyReq));
        if(typeOfBountyHash == keccak256(abi.encodePacked("ISP")) && bountyReqHash == keccak256(abi.encodePacked(lastMeasurement.ISP))){
            validClaim = true;
        }else if(typeOfBountyHash == keccak256(abi.encodePacked("d2s")) 
                    && int(bounties[bountyAddr][timest].bountyReq)-100 <= lastMeasurement.dist2server 
                    && int(bounties[bountyAddr][timest].bountyReq)+100 >= lastMeasurement.dist2server){
            validClaim = true;
        }else if(typeOfBountyHash == keccak256(abi.encodePacked("ping")) 
                    && int(bounties[bountyAddr][timest].bountyReq)-10 <= lastMeasurement.ping 
                    && int(bounties[bountyAddr][timest].bountyReq)+10 >= lastMeasurement.ping){
            validClaim = true;
        }
        if(validClaim){
            fulfillBounty(bountyAddr, timest, timestIndex);
            msg.sender.transfer(bounties[bountyAddr][timest].bountyValue);
            return true;
        }
    }
    
    function fulfillBounty(address bountyAddr, uint timest, uint timestIndex) internal{
        bountyMeasurements[bountyAddr][timest].push(AddressAndIndex({addr: msg.sender, index: measurementResults[msg.sender].length-1}));
        bounties[bountyAddr][timest].repeats--;
        if(bounties[bountyAddr][timest].repeats <= 0){
            numberOfBounties--;
            
            //remove timestamp from bounty address' list
            for (uint l = timestIndex; l<bountyAddressTimestamps[bountyAddr].length-1; l++){
                bountyAddressTimestamps[bountyAddr][l] = bountyAddressTimestamps[bountyAddr][l+1];
            }
            delete bountyAddressTimestamps[bountyAddr][bountyAddressTimestamps[bountyAddr].length-1];
            bountyAddressTimestamps[bountyAddr].length--;
            
            //remove bounty declaration at timestamp
            delete bounties[bountyAddr][timest];
            
            //check if address has any other bounties
            if(bountyAddressTimestamps[bountyAddr].length == 0){
                
                //remove address from bounty timestamp list altogether
                delete bountyAddressTimestamps[bountyAddr];
                
                //mark address as not having any bounties
                addressHasBounties[bountyAddr] = false;
                
                //remove address from list bounty addresses list
                bool pastAddress = false;
                for(uint m = 0; m<addressesWithBounties.length-1; m++){
                    if(addressesWithBounties[m] == bountyAddr) pastAddress = true;
                    if(pastAddress){
                        addressesWithBounties[m] = addressesWithBounties[m+1];
                    }
                }
                delete addressesWithBounties[addressesWithBounties.length-1];
                addressesWithBounties.length--;
            }
        }
    }
    
    function getRetiredBountyMeasurements(address bountyAddr, uint timest) public view returns(address[], uint256[]){
        address[] memory resAddresses = new address[](bountyMeasurements[bountyAddr][timest].length);
        uint256[] memory resIndexes = new uint256[](bountyMeasurements[bountyAddr][timest].length);
        for(uint i = 0; i<bountyMeasurements[bountyAddr][timest].length; i++){
            resAddresses[i] = bountyMeasurements[bountyAddr][timest][i].addr;
            resIndexes[i] = bountyMeasurements[bountyAddr][timest][i].index;
        }
        return (resAddresses, resIndexes);
    }
} 
