# 🚀 Blockchain Setup Guide

You have multiple options for deploying your AI smart contract. Choose the one that best fits your needs:

## 🌐 Option 1: Sepolia Testnet (RECOMMENDED)

**Best for:** Testing without real money, most similar to mainnet

### Setup Steps:
1. **Get Sepolia ETH** (free):
   - Visit: https://sepoliafaucet.com/
   - Connect your MetaMask wallet
   - Request test ETH

2. **Get Infura API Key** (free):
   - Sign up at: https://infura.io/
   - Create new project
   - Copy your Project ID

3. **Update .env file:**
   ```env
   ORACLE_PRIVATE_KEY=your_metamask_private_key
   RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
   CHAIN_ID=11155111
   ```

---

## 🏠 Option 2: Local Ganache (EASIEST)

**Best for:** Rapid development and testing

### Setup Steps:
1. **Install Ganache:**
   ```bash
   npm install -g ganache-cli
   ```

2. **Start local blockchain:**
   ```bash
   ganache-cli --deterministic --accounts 10 --host 0.0.0.0
   ```

3. **Update .env file:**
   ```env
   ORACLE_PRIVATE_KEY=YOUR_WALLET_PRIVATE_KEY
   RPC_URL=http://localhost:8545
   CHAIN_ID=1337
   ```

---

## 🟨 Option 4: BSC Testnet

**Best for:** Testing Binance Smart Chain features

### Setup Steps:
1. **Get testnet BNB** (free):
   - Visit: https://testnet.binance.org/faucet-smart
   - Request test BNB

2. **Update .env file:**
   ```env
   ORACLE_PRIVATE_KEY=your_metamask_private_key
   RPC_URL=https://data-seed-prebsc-1-s1.binance.org:8545
   CHAIN_ID=97
   ```

---

## 🔐 Getting Your Private Key

### From MetaMask:
1. Open MetaMask
2. Click account menu → Account Details
3. Click "Export Private Key"
4. Enter password
5. Copy the private key

⚠️ **NEVER share your private key or commit it to version control!**

---

## 🚀 Quick Start Commands

After choosing your blockchain and updating `.env`:

```bash
# Install dependencies (if not done already)
npm install

# Compile contracts
npx truffle compile

# Deploy to your chosen network
npx truffle migrate --network development

# Run tests
npm test

# Start the AI oracle bridge
python src/ai/oracle_bridge.py
```

---

## 🎯 Recommended Path

For beginners: **Start with Ganache (local)** → Test on **Sepolia** → Deploy to **Mainnet**

1. **Development**: Use Ganache for fast iteration
2. **Testing**: Use Sepolia for realistic testing
3. **Production**: Deploy to Ethereum/Polygon mainnet

---

## 💡 Pro Tips

- **Ganache**: Instant transactions, unlimited ETH, perfect for development
- **Testnets**: Real network conditions but free test tokens
- **Mainnet**: Real money, real users, deploy when ready

Choose your preferred option and let's get your AI smart contract deployed! 🚀
