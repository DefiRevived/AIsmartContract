#!/usr/bin/env python3
"""
Test script to interact with deployed AI contracts on BSC Testnet
"""

import json
import os
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.ai.inference import InferenceModel

def test_contract_interaction():
    """Test interaction with the deployed contracts on BSC Testnet"""
    
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Setup Web3 connection
    w3 = Web3(Web3.HTTPProvider(config['blockchain']['rpc_url']))
    if not w3.is_connected():
        print("❌ Failed to connect to BSC Testnet")
        return False
    
    print(f"✅ Connected to BSC Testnet (Chain ID: {w3.eth.chain_id})")
    
    # Setup account
    private_key = os.getenv('ORACLE_PRIVATE_KEY')
    if not private_key:
        print("❌ ORACLE_PRIVATE_KEY not found in environment")
        return False
    
    account = Account.from_key(private_key)
    print(f"🔑 Using account: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    balance_bnb = w3.from_wei(balance, 'ether')
    print(f"💰 Account balance: {balance_bnb:.4f} BNB")
    
    if balance_bnb < 0.01:
        print("⚠️  Low balance! You might need more BNB for gas fees.")
        print("Get testnet BNB from: https://testnet.bnbchain.org/faucet-smart")
    
    # Setup contracts
    ai_contract_address = config['blockchain']['ai_contract_address']
    oracle_address = config['blockchain']['oracle_address']
    
    print(f"📄 AI Contract: {ai_contract_address}")
    print(f"🔮 Oracle Contract: {oracle_address}")
    
    # Load AI Contract ABI
    with open('build/contracts/AIContract.json', 'r') as f:
        ai_contract_data = json.load(f)
        ai_contract_abi = ai_contract_data['abi']
    
    ai_contract = w3.eth.contract(
        address=ai_contract_address,
        abi=ai_contract_abi
    )
    
    # Load Oracle ABI from config
    oracle_abi = config['blockchain']['oracle_abi']
    oracle_contract = w3.eth.contract(
        address=oracle_address,
        abi=oracle_abi
    )
    
    print("\n🧪 Testing AI Model locally...")
      # Test AI model
    try:
        ai_model = InferenceModel(
            model_path=config['model']['path'],
            model_type=config['model']['type']
        )
          # Test prediction
        test_input = [1.0, 2.0, 3.0]  # 3 features for the demo model
        prediction, confidence = ai_model.predict_with_confidence(test_input)
        print(f"✅ AI Model working: Prediction = {prediction[0]:.3f}, Confidence = {confidence}%")
    except Exception as e:
        print(f"❌ AI Model error: {e}")
        return False
    
    print("\n🔗 Testing contract interaction...")
    
    try:        # Check if oracle is set in AI contract
        oracle_in_contract = ai_contract.functions.oracleAddress().call()
        print(f"🔮 Oracle address in AI contract: {oracle_in_contract}")
        
        if oracle_in_contract.lower() != oracle_address.lower():
            print("❌ Oracle address mismatch!")
            return False
        
        # Make a test prediction request
        print("\n📤 Making prediction request...")
          # Encode test input data
        test_data = [1.5, 2.5, 3.5]  # 3 features for the demo model
        input_bytes = bytes(str(test_data), 'utf-8')
          # Get the required fee
        prediction_fee = ai_contract.functions.predictionFee().call()
        print(f"💰 Required prediction fee: {w3.from_wei(prediction_fee, 'ether')} BNB")
        
        # Build transaction
        function = ai_contract.functions.requestPrediction(input_bytes)
          # Estimate gas
        gas_estimate = function.estimate_gas({
            'from': account.address,
            'value': prediction_fee
        })
        print(f"⛽ Estimated gas: {gas_estimate}")
          # Build transaction with fee
        transaction = function.build_transaction({
            'from': account.address,
            'value': prediction_fee,  # Include the required fee
            'gas': int(gas_estimate * 1.2),  # Add 20% buffer
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
          # Sign and send
        signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        print(f"📝 Transaction sent: {tx_hash.hex()}")
        print("⏳ Waiting for confirmation...")
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print("✅ Transaction successful!")
            print(f"⛽ Gas used: {receipt.gasUsed}")
            
            # Check for events
            prediction_events = ai_contract.events.PredictionRequested().process_receipt(receipt)
            if prediction_events:
                event = prediction_events[0]
                request_id = event['args']['requestId']
                print(f"🎯 Prediction request created with ID: {request_id.hex()}")
                
                print("\n🤖 For the Oracle Bridge to process this request:")
                print("1. Make sure the Oracle Bridge is running: python src/ai/oracle_bridge.py")
                print("2. The bridge will detect this request and submit a prediction")
                print("3. Check the PredictionFulfilled events for the result")
                
                return True
            else:
                print("⚠️  No PredictionRequested event found")
        else:
            print("❌ Transaction failed!")
            
    except Exception as e:
        print(f"❌ Contract interaction error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Testing BSC Testnet AI Smart Contract Integration")
    print("=" * 60)
    
    success = test_contract_interaction()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start the Oracle Bridge: python src/ai/oracle_bridge.py")
        print("2. Monitor the bridge logs for request processing")
        print("3. Check for PredictionFulfilled events in subsequent blocks")
    else:
        print("\n❌ Test failed. Check the errors above.")
