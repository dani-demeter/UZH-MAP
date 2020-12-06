// Solidity program to demonstrate  
pragma solidity ^0.4.26; 
pragma experimental ABIEncoderV2;
  
// Creating a contract 
contract TestContract   
{ 
    struct UserInfo {
        int64 dist2server;
        int256 ping;
        string ISP;
        string[] hops;
        int256 avgLatency_html; 
        int256 avgJitter_html;
        int256 avgLatency_video;
        int256 avgJitter_video;
        int256 avgLatency_audio;
        int256 avgJitter_audio;
    }
    
    
    UserInfo[] userInfos;
    
    function addMeasurement(int64 d2s, int256 png, string isp, string[] hops2server, int256 al_html, int256 aj_html, int256 al_video, int256 aj_video, int256 al_audio, int256 aj_audio) public returns(uint256){
        userInfos.push(UserInfo({dist2server:d2s, ping:png, ISP: isp, hops: hops2server, avgLatency_html: al_html, avgJitter_html: aj_html, avgLatency_video: al_video, avgJitter_video: aj_video, avgLatency_audio: al_audio, avgJitter_audio: aj_audio}));
        return userInfos.length;
    }
    
    function getAllMeasurements() public view returns(UserInfo[]){
        return userInfos;
    }
    
    function  (string filterISP) public view returns (UserInfo[]){
        UserInfo[] memory res = new UserInfo[](userInfos.length);
        bytes32 kFilterISP = keccak256(abi.encodePacked(filterISP));
        uint256 counter = 0;
        for (uint i=0; i<userInfos.length; i++) {
          if(keccak256(abi.encodePacked(userInfos[i].ISP)) == kFilterISP){
              res[counter] = userInfos[i];
              counter += 1;
          }
        }
        return res;
    }
    
    
    function get_output() public pure returns (string)  
    { 
       return ("Hi, your contract ran successfully!"); 
    } 
    
} 
