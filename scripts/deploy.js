const hre = require("hardhat");
const fs = require('fs');
const path = require('path');

async function main() {
    const [deployer] = await hre.ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy AI Oracle first
    console.log("\n1. Deploying AI Oracle...");
    const AIOracle = await hre.ethers.getContractFactory("AIOracle");
    const aiOracle = await AIOracle.deploy(hre.ethers.constants.AddressZero); // Temporary address
    await aiOracle.deployed();
    console.log("AI Oracle deployed to:", aiOracle.address);

    // Deploy AI Contract
    console.log("\n2. Deploying AI Contract...");
    const modelName = "AI Prediction Model v1.0";
    const AIContract = await hre.ethers.getContractFactory("AIContract");
    const aiContract = await AIContract.deploy(modelName, aiOracle.address);
    await aiContract.deployed();
    console.log("AI Contract deployed to:", aiContract.address);

    // Update Oracle with AI Contract address
    console.log("\n3. Configuring Oracle...");
    await aiOracle.setAIContract(aiContract.address);
    console.log("Oracle configured with AI Contract address");

    // Save deployment addresses
    const deploymentInfo = {
        network: hre.network.name,
        aiContract: aiContract.address,
        aiOracle: aiOracle.address,
        deployer: deployer.address,
        modelName: modelName,
        deployedAt: new Date().toISOString(),
        blockNumber: await hre.ethers.provider.getBlockNumber()
    };

    const deploymentsDir = path.join(__dirname, '..', '..', 'deployments');
    if (!fs.existsSync(deploymentsDir)) {
        fs.mkdirSync(deploymentsDir, { recursive: true });
    }

    fs.writeFileSync(
        path.join(deploymentsDir, `${hre.network.name}.json`),
        JSON.stringify(deploymentInfo, null, 2)
    );

    console.log("\n4. Deployment Summary:");
    console.log("=".repeat(50));
    console.log(`Network: ${hre.network.name}`);
    console.log(`AI Contract: ${aiContract.address}`);
    console.log(`AI Oracle: ${aiOracle.address}`);
    console.log(`Model Name: ${modelName}`);
    console.log(`Deployer: ${deployer.address}`);
    console.log(`Block Number: ${deploymentInfo.blockNumber}`);
    console.log("=".repeat(50));

    // Verify contracts on Etherscan (if not local network)
    if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
        console.log("\n5. Verifying contracts...");
        try {
            await hre.run("verify:verify", {
                address: aiOracle.address,
                constructorArguments: [hre.ethers.constants.AddressZero],
            });
            console.log("AI Oracle verified");

            await hre.run("verify:verify", {
                address: aiContract.address,
                constructorArguments: [modelName, aiOracle.address],
            });
            console.log("AI Contract verified");
        } catch (error) {
            console.log("Verification failed:", error.message);
        }
    }

    console.log("\nDeployment completed successfully!");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });