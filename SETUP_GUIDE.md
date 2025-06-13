# AI Smart Contract System - Complete Setup Guide

This package contains a fully functional AI Smart Contract system that integrates off-chain AI inference with on-chain smart contracts on BSC Testnet.

## 🚀 What This System Does

- **AI-Powered Smart Contracts**: Submit data to smart contracts and get AI predictions back
- **Oracle Bridge**: Connects off-chain AI models to blockchain smart contracts
- **Fee-Based System**: Pay BNB to get AI predictions stored permanently on blockchain
- **End-to-End Integration**: Complete workflow from request to AI inference to blockchain storage

## 📦 Package Contents

```
ai-smart-contract/
├── contracts/               # Solidity smart contracts
│   ├── AIContract.sol      # Main AI contract that accepts requests
│   ├── AIOracle.sol        # Oracle contract that processes predictions
│   ├── interfaces/         # Contract interfaces
│   └── Migrations.sol      # Truffle migrations contract
├── migrations/             # Truffle deployment scripts
├── test/                   # Smart contract tests
├── src/
│   └── ai/                 # AI model and inference code
├── models/                 # Pre-trained AI models
├── build/                  # Compiled contract artifacts
├── scripts/                # Setup and testing scripts
└── config files            # Configuration and environment files
```

## 🛠️ Prerequisites

### Required Software
1. **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
2. **Python** (3.8 or higher) - [Download](https://python.org/)
3. **Git** - [Download](https://git-scm.com/)

### Required Accounts
1. **BSC Testnet Wallet** - Use MetaMask or similar
2. **BSC Testnet BNB** - [Get from faucet](https://testnet.bnbchain.org/faucet-smart)

## ⚙️ Setup Instructions

### Step 1: Extract and Navigate
```bash
# Extract the ZIP file to your desired location
# Open terminal/command prompt and navigate to the project folder
cd ai-smart-contract
```

### Step 2: Install Node.js Dependencies
```bash
npm install
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

1. **Copy the environment template:**
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. **Edit `.env` file with your settings:**
   ```
   # BSC Testnet Configuration
   ORACLE_PRIVATE_KEY=your_private_key_here
   RPC_URL=https://data-seed-prebsc-1-s1.binance.org:8545
   CHAIN_ID=97
   ```

   **⚠️ Important:** Replace `your_private_key_here` with your actual wallet private key

### Step 5: Get Testnet BNB

1. Visit [BSC Testnet Faucet](https://testnet.bnbchain.org/faucet-smart)
2. Enter your wallet address
3. Request testnet BNB (you'll need ~0.1 BNB for testing)

### Step 6: Deploy Smart Contracts

```bash
# Compile contracts
npx truffle compile

# Deploy to BSC Testnet
npx truffle migrate --network bscTestnet
```

**Expected Output:**
```
✅ Deployment completed successfully!
📝 Contract Addresses:
   AIOracle: 0x...
   AIContract: 0x...
```

### Step 7: Update Configuration

```bash
# Run setup script to update config.json with deployed addresses
python setup_bridge.py
```

## 🧪 Testing the System

### Test 1: Complete End-to-End Test
```bash
python test_bsc_interaction.py
```

**Expected Output:**
```
🚀 Testing BSC Testnet AI Smart Contract Integration
✅ Connected to BSC Testnet
✅ AI Model working
✅ Transaction successful!
🎯 Prediction request created with ID: 0x...
```

### Test 2: Oracle Fulfillment

After creating a prediction request, edit the request ID in the fulfillment script and run:

```bash
# Edit direct_oracle_fulfillment.py with the request ID from Test 1
# Then run:
python direct_oracle_fulfillment.py
```

**Expected Output:**
```
✅ Prediction submitted successfully!
🎉 Oracle fulfillment completed!
```

### Test 3: Verify Events

```bash
python decode_events.py
```

**Expected Output:**
```
✅ Successfully decoded PredictionFulfilled:
   Request ID: 0x...
   Prediction: 0
   Confidence: 98%
```

## 🔧 Running the Oracle Bridge

To run the continuous oracle bridge service:

```bash
python simple_oracle_bridge.py
```

This will monitor for new prediction requests and automatically fulfill them.

## 📊 System Architecture

1. **User submits prediction request** → AI Contract (pays 0.001 BNB fee)
2. **AI Contract emits event** → Oracle Bridge detects it
3. **Oracle Bridge processes data** → AI Model generates prediction
4. **Oracle submits prediction** → Oracle Contract stores result
5. **Result stored on blockchain** → Permanent, verifiable AI prediction

## 🎯 Key Features Demonstrated

- ✅ **Smart Contract Development** (Solidity)
- ✅ **AI Model Integration** (Python/Scikit-learn)
- ✅ **Blockchain Deployment** (Truffle)
- ✅ **Oracle Pattern** (Off-chain to on-chain bridge)
- ✅ **Event Monitoring** (Web3.py)
- ✅ **Transaction Handling** (Gas estimation, signing)
- ✅ **Fee Management** (Pay-per-prediction model)

## 🚨 Troubleshooting

### Common Issues

1. **"Insufficient funds" error**
   - Get more testnet BNB from the faucet
   - Check your wallet balance

2. **"Network connection failed"**
   - Check your internet connection
   - Try a different RPC endpoint

3. **"Contract not deployed"**
   - Make sure `truffle migrate` completed successfully
   - Check if contract addresses are in `config.json`

4. **"Rate limit exceeded"**
   - Wait a few minutes between requests
   - The system handles this automatically

### Getting Help

- Check the console output for detailed error messages
- All transactions can be verified on [BSC Testnet Explorer](https://testnet.bscscan.com/)
- Review the log files for debugging information

## 🌟 What You've Built

This is a **production-ready foundation** for:

- **DeFi applications** with AI-driven strategies
- **Prediction markets** with machine learning
- **NFT projects** with AI-generated content  
- **Gaming** with AI-powered mechanics
- **Insurance** with AI risk assessment
- **Supply chain** with AI optimization

## 📈 Next Steps

1. **Deploy to Mainnet** - Update configuration for BSC Mainnet
2. **Improve AI Models** - Add more sophisticated ML models
3. **Build Frontend** - Create a web interface for users
4. **Add More Features** - Implement additional smart contract functionality
5. **Scale Up** - Optimize for higher throughput

## 📄 License

MIT License - Feel free to use this as a foundation for your own projects!

---

**🎉 Congratulations on building your first AI Smart Contract system!**

For questions or issues, review the troubleshooting section above or check the transaction logs on BSC Testnet Explorer.
