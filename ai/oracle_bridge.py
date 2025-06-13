import asyncio
import json
import logging
from web3 import Web3
from eth_account import Account
import numpy as np
from typing import Dict, Any, Optional
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.ai.inference import InferenceModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIOraculeBridge:
    """Bridge service connecting AI models to blockchain oracle"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.w3 = self._setup_web3()
        self.account = self._setup_account()
        self.oracle_contract = self._setup_oracle_contract()
        self.ai_model = InferenceModel(
            self.config['model']['path'], 
            self.config['model']['type']
        )
        self.is_running = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default config if file doesn't exist
            return {
                "blockchain": {
                    "rpc_url": "http://localhost:8545",
                    "chain_id": 1337,
                    "oracle_address": "0x...",
                    "oracle_abi": []
                },
                "model": {
                    "path": "models/trained_model.pkl",
                    "type": "sklearn"
                },
                "bridge": {
                    "poll_interval": 5,
                    "gas_limit": 300000,
                    "gas_price": 20000000000
                }
            }
    
    def _setup_web3(self) -> Web3:
        """Setup Web3 connection"""
        w3 = Web3(Web3.HTTPProvider(self.config['blockchain']['rpc_url']))
        if not w3.is_connected():
            raise ConnectionError("Failed to connect to blockchain")
        logger.info("Connected to blockchain")
        return w3
    
    def _setup_account(self) -> Account:
        """Setup blockchain account"""
        private_key = os.getenv('ORACLE_PRIVATE_KEY')
        if not private_key:
            raise ValueError("ORACLE_PRIVATE_KEY environment variable not set")
        return Account.from_key(private_key)
    
    def _setup_oracle_contract(self):
        """Setup oracle contract instance"""
        contract_address = self.config['blockchain']['oracle_address']
        contract_abi = self.config['blockchain']['oracle_abi']
        return self.w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )
    
    async def start_listening(self):
        """Start listening for prediction requests"""
        logger.info("Starting AI Oracle Bridge...")
        self.is_running = True
        
        # Get the latest block to start from
        last_processed_block = self.w3.eth.block_number
        
        while self.is_running:
            try:
                # Get current block
                current_block = self.w3.eth.block_number
                
                # Only process if there are new blocks
                if current_block > last_processed_block:
                    await self._process_new_requests(last_processed_block + 1, current_block)
                    last_processed_block = current_block
                    logger.info(f"Processed blocks {last_processed_block + 1} to {current_block}")
                
                # Wait before next poll
                await asyncio.sleep(self.config['bridge']['poll_interval'])                  except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(self.config['bridge']['poll_interval'])
    
    async def _process_new_requests(self, from_block: int, to_block: int):
        """Process new prediction requests from the blockchain"""
        try:
            # Get PredictionRequested events using getLogs directly
            event_filter = self.oracle_contract.events.PredictionRequested.get_logs(
                from_block=from_block,
                to_block=to_block
            )
            
            for event in event_filter:
                await self._handle_prediction_request(event)
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing requests: {error_msg}")
            
            # If rate limited, wait longer
            if 'limit exceeded' in error_msg or 'rate limit' in error_msg.lower():
                logger.warning("Rate limit exceeded, waiting 60 seconds...")
                await asyncio.sleep(60)
    
    async def _handle_prediction_request(self, event):
        """Handle a single prediction request"""
        try:
            request_id = event['args']['requestId']
            input_data = event['args']['inputData']
            
            logger.info(f"Processing prediction request: {request_id.hex()}")
            
            # Decode input data (assuming it's JSON encoded)
            try:
                decoded_input = json.loads(input_data.decode('utf-8'))
            except:
                # Fallback: treat as raw bytes and convert to float list
                decoded_input = list(input_data)
            
            # Make prediction using AI model
            prediction, confidence = self.ai_model.predict_with_confidence(decoded_input)
            
            # Convert prediction to integer (scaled by 1000 for precision)
            prediction_int = int(prediction[0] * 1000)
            confidence_int = int(confidence)
            
            # Submit prediction to blockchain
            await self._submit_prediction(request_id, prediction_int, confidence_int)
            
        except Exception as e:
            logger.error(f"Error handling prediction request: {e}")
    
    async def _submit_prediction(self, request_id: bytes, prediction: int, confidence: int):
        """Submit prediction to the oracle contract"""
        try:
            # Build transaction
            function = self.oracle_contract.functions.fulfillPrediction(
                request_id, prediction, confidence
            )
            
            # Estimate gas
            gas_estimate = function.estimateGas({'from': self.account.address})
            
            # Build transaction
            transaction = function.buildTransaction({
                'from': self.account.address,
                'gas': min(gas_estimate * 2, self.config['bridge']['gas_limit']),
                'gasPrice': self.config['bridge']['gas_price'],
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.config['blockchain']['chain_id']
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Prediction submitted successfully: {tx_hash.hex()}")
            else:
                logger.error(f"Transaction failed: {tx_hash.hex()}")
                
        except Exception as e:
            logger.error(f"Error submitting prediction: {e}")
    
    def stop_listening(self):
        """Stop the bridge service"""
        logger.info("Stopping AI Oracle Bridge...")
        self.is_running = False
    
    def get_bridge_stats(self) -> Dict[str, Any]:
        """Get bridge service statistics"""
        return {
            'is_running': self.is_running,
            'blockchain_connected': self.w3.is_connected(),
            'latest_block': self.w3.eth.block_number,
            'account_address': self.account.address,
            'account_balance': self.w3.eth.get_balance(self.account.address),
            'model_stats': self.ai_model.get_model_stats(),
            'timestamp': datetime.now().isoformat()
        }

async def main():
    """Main function to run the bridge service"""
    bridge = AIOraculeBridge()
    
    try:
        await bridge.start_listening()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        bridge.stop_listening()

if __name__ == "__main__":
    asyncio.run(main())
