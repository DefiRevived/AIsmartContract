// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./interfaces/IAIOracle.sol";

contract AIOracle is IAIOracle {
    address public owner;
    address public aiContract;
    
    struct PredictionData {
        int256 prediction;
        uint256 confidence;
        bool fulfilled;
        uint256 timestamp;
        bytes inputData;
    }
    
    mapping(bytes32 => PredictionData) public predictions;
    mapping(address => bool) public authorizedCallers;
    
    ModelMetadata public modelMetadata;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyAuthorizedCaller() {
        require(authorizedCallers[msg.sender] || msg.sender == aiContract, "Unauthorized caller");
        _;
    }
    
    constructor(address _aiContract) {
        owner = msg.sender;
        aiContract = _aiContract;
        authorizedCallers[_aiContract] = true;
        
        // Initialize model metadata
        modelMetadata = ModelMetadata({
            modelName: "AI Prediction Model",
            version: "1.0.0",
            accuracy: 85,
            lastUpdated: block.timestamp
        });
    }
    
    function getPrediction(bytes32 requestId) external view override returns (int256, uint256, bool) {
        PredictionData memory data = predictions[requestId];
        return (data.prediction, data.confidence, data.fulfilled);
    }
    
    function requestPrediction(bytes32 requestId, bytes calldata inputData) external override onlyAuthorizedCaller returns (bool) {
        require(predictions[requestId].timestamp == 0, "Request already exists");
        
        predictions[requestId] = PredictionData({
            prediction: 0,
            confidence: 0,
            fulfilled: false,
            timestamp: block.timestamp,
            inputData: inputData
        });
        
        emit PredictionRequested(requestId, inputData);
        return true;
    }
    
    function fulfillPrediction(bytes32 requestId, int256 prediction, uint256 confidence) external override onlyOwner {
        require(predictions[requestId].timestamp != 0, "Request does not exist");
        require(!predictions[requestId].fulfilled, "Prediction already fulfilled");
        require(confidence <= 100, "Confidence must be <= 100");
        
        predictions[requestId].prediction = prediction;
        predictions[requestId].confidence = confidence;
        predictions[requestId].fulfilled = true;
        
        emit PredictionFulfilled(requestId, prediction, confidence);
    }
    
    function updateModel(string calldata modelName, string calldata version, uint256 accuracy) external override onlyOwner {
        require(accuracy <= 100, "Accuracy must be <= 100");
        
        modelMetadata.modelName = modelName;
        modelMetadata.version = version;
        modelMetadata.accuracy = accuracy;
        modelMetadata.lastUpdated = block.timestamp;
        
        emit ModelUpdated(modelName, version, accuracy);
    }
    
    function getModelMetadata() external view override returns (ModelMetadata memory) {
        return modelMetadata;
    }
    
    function isRequestPending(bytes32 requestId) external view override returns (bool) {
        return predictions[requestId].timestamp != 0 && !predictions[requestId].fulfilled;
    }
    
    function getRequestTimestamp(bytes32 requestId) external view override returns (uint256) {
        return predictions[requestId].timestamp;
    }
    
    function authorizeCaller(address caller) external onlyOwner {
        authorizedCallers[caller] = true;
    }
    
    function revokeCaller(address caller) external onlyOwner {
        authorizedCallers[caller] = false;
    }
    
    function setAIContract(address _aiContract) external onlyOwner {
        aiContract = _aiContract;
        authorizedCallers[_aiContract] = true;
    }
    
    function getRequestData(bytes32 requestId) external view returns (PredictionData memory) {
        return predictions[requestId];
    }
}
