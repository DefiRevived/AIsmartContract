#!/usr/bin/env python3
"""
Setup script to prepare the AI Oracle Bridge for testing
"""

import json
import os
from pathlib import Path

def extract_contract_abi():
    """Extract contract ABI and update config.json"""
    
    # Paths
    build_dir = Path("build/contracts")
    config_file = Path("config.json")
    
    # Load Oracle ABI
    oracle_abi_file = build_dir / "AIOracle.json"
    with open(oracle_abi_file, 'r') as f:
        oracle_contract = json.load(f)
        oracle_abi = oracle_contract['abi']
    
    # Load current config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Update config with ABI
    config['blockchain']['oracle_abi'] = oracle_abi
    
    # Save updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Contract ABI added to config.json")
    print(f"📁 Oracle ABI has {len(oracle_abi)} functions/events")
    
    return config

def main():
    """Main setup function"""
    print("🔧 Setting up AI Oracle Bridge...")
    
    # Extract ABI
    config = extract_contract_abi()
    
    # Show current configuration
    print("\n📋 Current Configuration:")
    print(f"   RPC URL: {config['blockchain']['rpc_url']}")
    print(f"   Chain ID: {config['blockchain']['chain_id']}")
    print(f"   Oracle Address: {config['blockchain']['oracle_address']}")
    print(f"   AI Contract: {config['blockchain']['ai_contract_address']}")
    print(f"   Model Path: {config['model']['path']}")
    print(f"   Model Type: {config['model']['type']}")
    
    print("\n🚀 Ready to start Oracle Bridge!")
    print("Next: Run 'python src/ai/oracle_bridge.py'")

if __name__ == "__main__":
    main()
