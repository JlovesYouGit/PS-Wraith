#!/usr/bin/env python3
"""
Test script for network space training system.
Trains the TESA system on Bitcoin network space by adjusting weights to correlate with valid signatures.
"""

from blockchain_tesa_bridge import BlockchainTesaBridge

def test_network_space_training():
    """Test the network space training system."""
    
    # Initialize bridge
    bridge = BlockchainTesaBridge()
    
    # Use sample Bitcoin addresses for training
    training_addresses = [
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Satoshi's address
    ]
    
    print("=" * 80)
    print("TESTING NETWORK SPACE TRAINING SYSTEM")
    print("=" * 80)
    print(f"Training Addresses: {len(training_addresses)}")
    print(f"🧠 TRAINING ON BITCOIN NETWORK SPACE")
    print("=" * 80)
    
    # Train the system on network space
    training_result = bridge.train_network_space_weights(
        training_addresses=training_addresses,
        epochs=50  # Reduced for testing
    )
    
    print("\n" + "=" * 80)
    print("TRAINING RESULTS")
    print("=" * 80)
    print(f"Best Correlation: {training_result['best_correlation']:.4f}")
    print(f"Epochs Completed: {training_result['epochs_completed']}")
    print(f"Trained Weights: {training_result['trained_weights']}")
    
    # Test the trained system on the original address
    print("\n" + "=" * 80)
    print("TESTING TRAINED SYSTEM ON ORIGINAL ADDRESS")
    print("=" * 80)
    
    test_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    print(f"Test Address: {test_address}")
    print(f"Updated Base Frequency: {bridge.base_frequency} Hz")
    
    # Extract data and test correlation
    blockchain_data = bridge._fetch_blockchain_data(test_address)
    network_signature = bridge._calculate_network_space_signature(blockchain_data)
    tesa_signature = bridge._calculate_weighted_tesa_signature(test_address, bridge.trained_weights)
    correlation = bridge._calculate_signature_correlation(network_signature, tesa_signature)
    
    print(f"Network Signature: {network_signature[:16]}...")
    print(f"TESA Signature: {tesa_signature[:16]}...")
    print(f"Correlation: {correlation:.4f}")
    
    if correlation > 0.8:
        print("✅ TRAINED SYSTEM ACHIEVES HIGH CORRELATION WITH VALID SIGNATURES")
    else:
        print("⚠️  CORRELATION BELOW THRESHOLD - MAY NEED MORE TRAINING")
    
    return training_result

if __name__ == "__main__":
    test_network_space_training()
