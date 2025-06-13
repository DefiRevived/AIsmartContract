const { expect } = require('chai');
const AIContract = artifacts.require('AIContract');
const AIOracle = artifacts.require('AIOracle');

contract('AIContract', function(accounts) {
    let aiContract, aiOracle;
    const [owner, addr1, addr2] = accounts;
    const modelName = "TestAIModel";
    const predictionFee = web3.utils.toWei("0.001", "ether");

    beforeEach(async function () {
        // Deploy Oracle first
        aiOracle = await AIOracle.new(web3.utils.padLeft(0, 40));
        
        // Deploy AI Contract
        aiContract = await AIContract.new(modelName, aiOracle.address);
        
        // Update oracle with correct AI contract address
        await aiOracle.setAIContract(aiContract.address);
    });

    describe('Deployment', function () {
        it('Should set the correct model name', async function () {
            const result = await aiContract.modelName();
            expect(result).to.equal(modelName);
        });

        it('Should set the correct oracle address', async function () {
            const result = await aiContract.oracleAddress();
            expect(result).to.equal(aiOracle.address);
        });

        it('Should set the correct owner', async function () {
            const result = await aiContract.owner();
            expect(result).to.equal(owner);
        });

        it('Should set correct prediction fee', async function () {
            const result = await aiContract.predictionFee();
            expect(result.toString()).to.equal(predictionFee);
        });
    });

    describe('Model Training', function () {
        it('Should allow owner to train model', async function () {
            const tx = await aiContract.trainModel({ from: owner });
            
            // Check event was emitted
            expect(tx.logs).to.have.lengthOf(1);
            expect(tx.logs[0].event).to.equal('ModelTrained');
            expect(tx.logs[0].args.modelName).to.equal(modelName);
        });

        it('Should not allow non-owner to train model', async function () {
            try {
                await aiContract.trainModel({ from: addr1 });
                expect.fail('Should have thrown error');
            } catch (error) {
                expect(error.message).to.include('Only owner can call this function');
            }
        });
    });

    describe('Prediction Requests', function () {
        const inputData = web3.utils.asciiToHex(JSON.stringify([1.0, 2.0, 3.0]));

        it('Should allow prediction request with correct fee', async function () {
            const tx = await aiContract.requestPrediction(inputData, {
                from: addr1,
                value: predictionFee
            });
            
            // Check event was emitted
            expect(tx.logs).to.have.lengthOf(1);
            expect(tx.logs[0].event).to.equal('PredictionRequested');
            expect(tx.logs[0].args.requester).to.equal(addr1);
        });

        it('Should reject prediction request with insufficient fee', async function () {
            const insufficientFee = web3.utils.toWei("0.0005", "ether");
            
            try {
                await aiContract.requestPrediction(inputData, {
                    from: addr1,
                    value: insufficientFee
                });
                expect.fail('Should have thrown error');
            } catch (error) {
                expect(error.message).to.include('Insufficient fee');
            }
        });
    });
});
