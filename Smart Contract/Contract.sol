// Solidity program to demonstrate  
pragma solidity ^0.4.26; 
pragma experimental ABIEncoderV2;
  
// Creating a contract 
contract TestContract   
{ 
    struct UserInfo {
        int64 dist2server;
        int256 ping;
    }
    
    UserInfo[] userInfos;
    
    function addUserInfo(int64 d2s, int256 png) public returns(UserInfo[]){
        userInfos.push(UserInfo({dist2server:d2s, ping:png}));
        return userInfos;
    }
    
    function getUserInfos() public view returns(UserInfo[]){
        return userInfos;
    }
    
    
    // Defining a function 
    function get_output() public pure returns (string)  
    { 
       return ("Hi, your contract ran successfully!"); 
    } 
  
} 
