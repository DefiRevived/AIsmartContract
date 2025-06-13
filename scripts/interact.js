const Web3 = require('web3');
const AIContractABI = require('../contracts/AIContract.json'); // Adjust the path as necessary
const contractAddress = 'YOUR_CONTRACT_ADDRESS'; // Replace with your deployed contract address

const web3 = new Web3('http://localhost:8545'); // Replace with your Ethereum node URL
const aiContract = new web3.eth.Contract(AIContractABI, contractAddress);

async function getAIData() {
    try {
        const data = await aiContract.methods.getAIData().call();
        console.log('AI Data:', data);
    } catch (error) {
        console.error('Error fetching AI data:', error);
    }
}

async function setAIData(newData) {
    const accounts = await web3.eth.getAccounts();
    try {
        const receipt = await aiContract.methods.setAIData(newData).send({ from: accounts[0] });
        console.log('Transaction receipt:', receipt);
    } catch (error) {
        console.error('Error setting AI data:', error);
    }
}

// Example usage
getAIData();
setAIData('New AI Data'); // Replace with actual data to set