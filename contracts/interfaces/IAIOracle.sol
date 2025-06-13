// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IAIOracle {
    struct ModelMetadata {
        string modelName;
        string version;
        uint256 accuracy;
        uint256 lastUpdated;
    }
    
    event PredictionRequested(bytes32 indexed requestId, bytes inputData);
    event PredictionFulfilled(bytes32 indexed requestId, int256 prediction, uint256 confidence);
    event ModelUpdated(string modelName, string version, uint256 accuracy);
    
    function getPrediction(bytes32 requestId) external view returns (int256, uint256, bool);
    function requestPrediction(bytes32 requestId, bytes calldata inputData) external returns (bool);
    function fulfillPrediction(bytes32 requestId, int256 prediction, uint256 confidence) external;
    
    function updateModel(string calldata modelName, string calldata version, uint256 accuracy) external;
    function getModelMetadata() external view returns (ModelMetadata memory);
    
    function isRequestPending(bytes32 requestId) external view returns (bool);
    function getRequestTimestamp(bytes32 requestId) external view returns (uint256);
}