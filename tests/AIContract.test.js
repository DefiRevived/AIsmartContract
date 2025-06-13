const { expect } = require('chai');
const { ethers } = require('hardhat');

describe('AIContract', function () {
    let AIContract, AIOracle;
    let aiContract, aiOracle;
    let owner, addr1, addr2;
    const modelName = "TestAIModel";
    const predictionFee = ethers.utils.parseEther("0.001");

    beforeEach(async function () {
        [owner, addr1, addr2] = await ethers.getSigners();
        
        // Deploy Oracle first
        AIOracle = await ethers.getContractFactory('AIOracle');
        aiOracle = await AIOracle.deploy(ethers.constants.AddressZero); // Temporary address
        await aiOracle.deployed();
        
        // Deploy AI Contract
        AIContract = await ethers.getContractFactory('AIContract');
        aiContract = await AIContract.deploy(modelName, aiOracle.address);
        await aiContract.deployed();
        
        // Update oracle with correct AI contract address
        await aiOracle.setAIContract(aiContract.address);
    });

    describe('Deployment', function () {
        it('Should set the correct model name', async function () {
            expect(await aiContract.modelName()).to.equal(modelName);
        });

        it('Should set the correct oracle address', async function () {
            expect(await aiContract.oracleAddress()).to.equal(aiOracle.address);
        });

        it('Should set the correct owner', async function () {
            expect(await aiContract.owner()).to.equal(owner.address);
        });

        it('Should set correct prediction fee', async function () {
            expect(await aiContract.predictionFee()).to.equal(predictionFee);
        });
    });

    describe('Model Training', function () {
        it('Should allow owner to train model', async function () {
            await expect(aiContract.trainModel())
                .to.emit(aiContract, 'ModelTrained')
                .withArgs(modelName, await getBlockTimestamp());
        });

        it('Should not allow non-owner to train model', async function () {
            await expect(aiContract.connect(addr1).trainModel())
                .to.be.revertedWith('Only owner can call this function');
        });
    });

    describe('Prediction Requests', function () {
        const inputData = ethers.utils.toUtf8Bytes(JSON.stringify([1.0, 2.0, 3.0]));

        it('Should allow prediction request with correct fee', async function () {
            const tx = await aiContract.connect(addr1).requestPrediction(inputData, {
                value: predictionFee
            });
            
            const receipt = await tx.wait();
            const event = receipt.events.find(e => e.event === 'PredictionRequested');
            
            expect(event).to.not.be.undefined;
            expect(event.args.requester).to.equal(addr1.address);
        });

        it('Should reject prediction request with insufficient fee', async function () {
            const insufficientFee = ethers.utils.parseEther("0.0005");
            
            await expect(aiContract.connect(addr1).requestPrediction(inputData, {
                value: insufficientFee
            })).to.be.revertedWith('Insufficient fee');
        });

        it('Should generate unique request IDs', async function () {
            const tx1 = await aiContract.connect(addr1).requestPrediction(inputData, {
                value: predictionFee
            });
            const tx2 = await aiContract.connect(addr2).requestPrediction(inputData, {
                value: predictionFee
            });

            const receipt1 = await tx1.wait();
            const receipt2 = await tx2.wait();
            
            const requestId1 = receipt1.events.find(e => e.event === 'PredictionRequested').args.requestId;
            const requestId2 = receipt2.events.find(e => e.event === 'PredictionRequested').args.requestId;
            
            expect(requestId1).to.not.equal(requestId2);
        });
    });

    describe('Oracle Management', function () {
        it('Should allow owner to authorize oracles', async function () {
            await expect(aiContract.authorizeOracle(addr1.address))
                .to.emit(aiContract, 'OracleAuthorized')
                .withArgs(addr1.address);
            
            expect(await aiContract.authorizedOracles(addr1.address)).to.be.true;
        });

        it('Should allow owner to revoke oracles', async function () {
            await aiContract.authorizeOracle(addr1.address);
            
            await expect(aiContract.revokeOracle(addr1.address))
                .to.emit(aiContract, 'OracleRevoked')
                .withArgs(addr1.address);
            
            expect(await aiContract.authorizedOracles(addr1.address)).to.be.false;
        });

        it('Should not allow non-owner to manage oracles', async function () {
            await expect(aiContract.connect(addr1).authorizeOracle(addr2.address))
                .to.be.revertedWith('Only owner can call this function');
        });
    });

    describe('Fee Management', function () {
        it('Should allow owner to update prediction fee', async function () {
            const newFee = ethers.utils.parseEther("0.002");
            await aiContract.setPredictionFee(newFee);
            expect(await aiContract.predictionFee()).to.equal(newFee);
        });

        it('Should not allow non-owner to update fee', async function () {
            const newFee = ethers.utils.parseEther("0.002");
            await expect(aiContract.connect(addr1).setPredictionFee(newFee))
                .to.be.revertedWith('Only owner can call this function');
        });

        it('Should allow owner to withdraw funds', async function () {
            // Make a prediction request to add funds
            await aiContract.connect(addr1).requestPrediction(
                ethers.utils.toUtf8Bytes("test"), 
                { value: predictionFee }
            );
            
            const initialBalance = await ethers.provider.getBalance(owner.address);
            await aiContract.withdraw();
            const finalBalance = await ethers.provider.getBalance(owner.address);
            
            expect(finalBalance).to.be.gt(initialBalance);
        });
    });

    describe('Integration with Oracle', function () {
        const inputData = ethers.utils.toUtf8Bytes(JSON.stringify([1.5, 2.5, 3.5]));
        
        it('Should fulfill prediction through oracle', async function () {
            // Request prediction
            const tx = await aiContract.connect(addr1).requestPrediction(inputData, {
                value: predictionFee
            });
            const receipt = await tx.wait();
            const requestId = receipt.events.find(e => e.event === 'PredictionRequested').args.requestId;
            
            // Oracle fulfills prediction
            const prediction = 1250; // Represents 1.25 scaled by 1000
            const confidence = 85;
            
            await expect(aiOracle.fulfillPrediction(requestId, prediction, confidence))
                .to.emit(aiOracle, 'PredictionFulfilled')
                .withArgs(requestId, prediction, confidence);
            
            // Check prediction was stored
            const predictionData = await aiContract.getPrediction(requestId);
            expect(predictionData.fulfilled).to.be.true;
            expect(predictionData.result).to.equal(prediction);
        });
    });

    // Helper function to get block timestamp
    async function getBlockTimestamp() {
        const blockNumber = await ethers.provider.getBlockNumber();
        const block = await ethers.provider.getBlock(blockNumber);
        return block.timestamp;
    }
});