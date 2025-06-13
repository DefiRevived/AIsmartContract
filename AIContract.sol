// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./interfaces/IAIOracle.sol";

contract AIContract {
    string public modelName;
    address public oracleAddress;
    address public owner;
    
    struct PredictionRequest {
        bytes32 requestId;
        address requester;
        bytes inputData;
        bool fulfilled;
        int256 result;
        uint256 timestamp;
    }
    
    mapping(bytes32 => PredictionRequest) public predictions;
    mapping(address => bool) public authorizedOracles;
    
    uint256 public predictionFee = 0.001 ether;
    uint256 public requestCounter = 0;

    event ModelTrained(string modelName, uint256 timestamp);
    event PredictionRequested(bytes32 indexed requestId, address indexed requester, bytes inputData);
    event PredictionFulfilled(bytes32 indexed requestId, int256 result);
    event OracleAuthorized(address indexed oracle);
    event OracleRevoked(address indexed oracle);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyAuthorizedOracle() {
        require(authorizedOracles[msg.sender], "Only authorized oracles can call this function");
        _;
    }

    constructor(string memory _modelName, address _oracleAddress) {
        modelName = _modelName;
        oracleAddress = _oracleAddress;
        owner = msg.sender;
        authorizedOracles[_oracleAddress] = true;
    }

    function trainModel() public onlyOwner {
        // Logic to trigger AI model training
        emit ModelTrained(modelName, block.timestamp);
    }

    function requestPrediction(bytes memory inputData) public payable returns (bytes32) {
        require(msg.value >= predictionFee, "Insufficient fee");
        
        requestCounter++;
        bytes32 requestId = keccak256(abi.encodePacked(block.timestamp, msg.sender, requestCounter));
        
        predictions[requestId] = PredictionRequest({
            requestId: requestId,
            requester: msg.sender,
            inputData: inputData,
            fulfilled: false,
            result: 0,
            timestamp: block.timestamp
        });
        
        // Call oracle to process prediction
        IAIOracle(oracleAddress).requestPrediction(requestId, inputData);
        
        emit PredictionRequested(requestId, msg.sender, inputData);
        return requestId;
    }
    
    function fulfillPrediction(bytes32 requestId, int256 result) external onlyAuthorizedOracle {
        require(!predictions[requestId].fulfilled, "Prediction already fulfilled");
        
        predictions[requestId].fulfilled = true;
        predictions[requestId].result = result;
        
        emit PredictionFulfilled(requestId, result);
    }
    
    function getPrediction(bytes32 requestId) external view returns (PredictionRequest memory) {
        return predictions[requestId];
    }

    function authorizeOracle(address _oracle) external onlyOwner {
        authorizedOracles[_oracle] = true;
        emit OracleAuthorized(_oracle);
    }
    
    function revokeOracle(address _oracle) external onlyOwner {
        authorizedOracles[_oracle] = false;
        emit OracleRevoked(_oracle);
    }

    function setOracleAddress(address _oracleAddress) public onlyOwner {
        oracleAddress = _oracleAddress;
        authorizedOracles[_oracleAddress] = true;
    }
    
    function setPredictionFee(uint256 _fee) external onlyOwner {
        predictionFee = _fee;
    }

    function getOracleAddress() public view returns (address) {
        return oracleAddress;
    }
    
    function withdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}