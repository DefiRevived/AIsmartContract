const AIOracle = artifacts.require("AIOracle");
const AIContract = artifacts.require("AIContract");

module.exports = async function (deployer, network, accounts) {
  console.log("Deploying to network:", network);
  console.log("Using account:", accounts[0]);
  
  // First deploy the Oracle (with temporary contract address)
  console.log("Deploying AIOracle...");
  await deployer.deploy(AIOracle, "0x0000000000000000000000000000000000000000");
  const oracleInstance = await AIOracle.deployed();
  console.log("AIOracle deployed at:", oracleInstance.address);
  
  // Then deploy the AI Contract with the Oracle address
  console.log("Deploying AIContract...");
  await deployer.deploy(AIContract, "AI Prediction Model v1.0", oracleInstance.address);
  const contractInstance = await AIContract.deployed();
  console.log("AIContract deployed at:", contractInstance.address);
  
  // Update the Oracle with the correct AI Contract address
  console.log("Setting AI Contract address in Oracle...");
  await oracleInstance.setAIContract(contractInstance.address);
  
  console.log("✅ Deployment completed successfully!");
  console.log("📝 Contract Addresses:");
  console.log(`   AIOracle: ${oracleInstance.address}`);
  console.log(`   AIContract: ${contractInstance.address}`);
  console.log("");
  console.log("🔧 Next steps:");
  console.log("1. Update config.json with these contract addresses");
  console.log("2. Run the oracle bridge: python src/ai/oracle_bridge.py");
  console.log("3. Test predictions through the smart contract!");
};
