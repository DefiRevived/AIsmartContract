require('dotenv').config();
const HDWalletProvider = require('@truffle/hdwallet-provider');

const ORACLE_PRIVATE_KEY = process.env.ORACLE_PRIVATE_KEY;
const RPC_URL = process.env.RPC_URL;

module.exports = {
  networks: {
    // Local development with Ganache
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*",
      gas: 6721975,
      gasPrice: 20000000000
    },
    
    // Ganache GUI
    ganache: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "*",
      gas: 6721975,
      gasPrice: 20000000000
    },

    // Sepolia Testnet
    sepolia: {
      provider: () => new HDWalletProvider(
        ORACLE_PRIVATE_KEY,
        `https://sepolia.infura.io/v3/${process.env.INFURA_PROJECT_ID}`
      ),
      network_id: 11155111,
      gas: 4000000,
      gasPrice: 10000000000,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true
    },

    // BSC Testnet
    bscTestnet: {
      provider: () => new HDWalletProvider(
        [ORACLE_PRIVATE_KEY],
        "https://data-seed-prebsc-1-s1.binance.org:8545"
      ),
      network_id: 97,
      gas: 4000000,
      gasPrice: 10000000000,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true
    },

    // For when using custom RPC_URL from .env
    custom: {
      provider: () => new HDWalletProvider(ORACLE_PRIVATE_KEY, RPC_URL),
      network_id: "*",
      gas: 4000000,
      gasPrice: 20000000000
    }
  },

  mocha: {
    timeout: 100000
  },

  compilers: {
    solc: {
      version: "0.8.19",
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        },
        evmVersion: "london"
      }
    }
  },

  plugins: ["truffle-plugin-verify"],

  api_keys: {
    etherscan: process.env.ETHERSCAN_API_KEY,
    polygonscan: process.env.POLYGONSCAN_API_KEY,
    bscscan: process.env.BSCSCAN_API_KEY
  }
};