#!/usr/bin/env python3
"""
Simplified AI Oracle Bridge for BSC Testnet
"""

import asyncio
import json
import logging
from web3 import Web3
from eth_account import Account
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.ai.inference import InferenceModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleOraculeBridge:
    """Simplified Oracle Bridge for processing AI predictions"""
    
    def __init__(self):
        # Load configuration
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        # Setup Web3
        self.w3 = Web3(Web3.HTTPProvider(self.config['blockchain']['rpc_url']))
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to blockchain")
        logger.info(f"Connected to BSC Testnet (Chain ID: {self.w3.eth.chain_id})")
        
        # Setup account
        private_key = os.getenv('ORACLE_PRIVATE_KEY')
        if not private_key:
            raise ValueError("ORACLE_PRIVATE_KEY environment variable not set")
        self.account = Account.from_key(private_key)
        logger.info(f"Using oracle account: {self.account.address}")
        
        # Setup contracts
        self.setup_contracts()
        
        # Setup AI model
        self.ai_model = InferenceModel(
            model_path=self.config['model']['path'],
            model_type=self.config['model']['type']
        )
        logger.info("AI model loaded successfully")
        
        self.is_running = False
        self.last_processed_block = self.w3.eth.block_number
        
    def setup_contracts(self):
        """Setup contract instances"""
        # Oracle contract
        oracle_abi = self.config['blockchain']['oracle_abi']
        oracle_address = self.config['blockchain']['oracle_address']
        self.oracle_contract = self.w3.eth.contract(
            address=oracle_address,
            abi=oracle_abi
        )
        
        # AI contract (for events)
        with open('build/contracts/AIContract.json', 'r') as f:
            ai_contract_data = json.load(f)
        
        ai_address = self.config['blockchain']['ai_contract_address']
        self.ai_contract = self.w3.eth.contract(
            address=ai_address,
            abi=ai_contract_data['abi']
        )
        
        logger.info(f"Oracle contract: {oracle_address}")
        logger.info(f"AI contract: {ai_address}")
    
    async def start_bridge(self):
        """Start the oracle bridge service"""
        logger.info("🚀 Starting AI Oracle Bridge...")
        logger.info(f"📊 Monitoring from block: {self.last_processed_block}")
        
        self.is_running = True
        
        while self.is_running:
            try:
                current_block = self.w3.eth.block_number
                
                if current_block > self.last_processed_block:
                    logger.info(f"📋 Checking blocks {self.last_processed_block + 1} to {current_block}")
                    await self.process_new_events(self.last_processed_block + 1, current_block)
                    self.last_processed_block = current_block
                else:
                    logger.info(f"⏳ Waiting... Current block: {current_block}")
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def process_new_events(self, from_block: int, to_block: int):
        """Process new prediction request events"""
        try:            # Get PredictionRequested events from AI contract
            events = self.ai_contract.events.PredictionRequested.get_logs(
                from_block=from_block,
                to_block=to_block
            )
            
            if events:
                logger.info(f"🎯 Found {len(events)} prediction request(s)")
                
                for event in events:
                    await self.handle_prediction_request(event)
            else:
                logger.info("📭 No new prediction requests")
                
        except Exception as e:
            logger.error(f"❌ Error processing events: {e}")
            # If rate limited, wait longer
            if 'limit exceeded' in str(e).lower():
                logger.warning("⚠️ Rate limit hit, waiting 60 seconds...")
                await asyncio.sleep(60)
    
    async def handle_prediction_request(self, event):
        """Handle a single prediction request"""
        try:
            request_id = event['args']['requestId']
            input_data = event['args']['inputData']
            
            logger.info(f"🔍 Processing request: {request_id.hex()}")
            logger.info(f"📥 Input data: {input_data}")
            
            # Decode input data
            input_str = input_data.decode('utf-8')
            # Parse the input (expecting format like "[1.5, 2.5, 3.5]")
            import ast
            input_values = ast.literal_eval(input_str)
            
            logger.info(f"🧮 Parsed input: {input_values}")
            
            # Make prediction
            prediction, confidence = self.ai_model.predict_with_confidence(input_values)
            
            # Convert to integers for blockchain
            prediction_int = int(prediction[0] * 1000)  # Scale by 1000
            confidence_int = int(confidence)
            
            logger.info(f"🤖 AI Prediction: {prediction[0]:.3f} (scaled: {prediction_int})")
            logger.info(f"📊 Confidence: {confidence}%")
            
            # Submit prediction to oracle
            await self.submit_prediction(request_id, prediction_int, confidence_int)
            
        except Exception as e:
            logger.error(f"❌ Error handling prediction: {e}")
    
    async def submit_prediction(self, request_id: bytes, prediction: int, confidence: int):
        """Submit prediction to the oracle contract"""
        try:
            logger.info(f"📤 Submitting prediction for request: {request_id.hex()}")
            
            # Build transaction
            function = self.oracle_contract.functions.fulfillPrediction(
                request_id, prediction, confidence
            )
            
            # Estimate gas
            gas_estimate = function.estimate_gas({'from': self.account.address})
            logger.info(f"⛽ Estimated gas: {gas_estimate}")
            
            # Build transaction
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': int(gas_estimate * 1.2),
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            logger.info(f"📝 Transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"✅ Prediction submitted successfully!")
                logger.info(f"⛽ Gas used: {receipt.gasUsed}")
                
                # Check for fulfillment events
                try:
                    fulfill_events = self.ai_contract.events.PredictionFulfilled().process_receipt(receipt)
                    if fulfill_events:
                        event = fulfill_events[0]
                        logger.info(f"🎉 Prediction fulfilled: Result = {event['args']['result']}")
                    else:
                        logger.info("📋 Prediction submitted (no fulfill event detected)")
                except Exception as e:
                    logger.warning(f"⚠️ Could not process fulfill events: {e}")
                    
            else:
                logger.error(f"❌ Transaction failed: {tx_hash.hex()}")
                
        except Exception as e:
            logger.error(f"❌ Error submitting prediction: {e}")
    
    def stop(self):
        """Stop the bridge service"""
        logger.info("🛑 Stopping Oracle Bridge...")
        self.is_running = False

async def main():
    """Main function"""
    try:
        bridge = SimpleOraculeBridge()
        
        logger.info("=" * 60)
        logger.info("🤖 AI Oracle Bridge for BSC Testnet")
        logger.info("=" * 60)
        logger.info(f"🔑 Oracle Address: {bridge.account.address}")
        logger.info(f"💰 Balance: {bridge.w3.from_wei(bridge.w3.eth.get_balance(bridge.account.address), 'ether')} BNB")
        logger.info(f"🌐 Network: BSC Testnet (Chain ID: {bridge.w3.eth.chain_id})")
        logger.info("=" * 60)
        
        await bridge.start_bridge()
        
    except KeyboardInterrupt:
        logger.info("👋 Bridge stopped by user")
    except Exception as e:
        logger.error(f"❌ Bridge error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
