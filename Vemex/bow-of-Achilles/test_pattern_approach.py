#!/usr/bin/env python3
"""
Test script for TESA grid-based Bitcoin key derivation.
Tests pointer travel patterns connected to TESA hash goal for valid key derivation.
"""

from blockchain_tesa_bridge import BlockchainTesaBridge

def test_tesa_grid_derivation():
    """Test the TESA grid-based approach for Bitcoin key derivation."""
    
    # Initialize bridge
    bridge = BlockchainTesaBridge()
    
    # Use existing address and private key
    address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    private_key = "1e5b7276104ed66900b2035a706fdfe0e720fa5ca233d43870ab1b5a819f3cd9"
    
    print("=" * 80)
    print("TESTING TESA GRID-BASED BITCOIN KEY DERIVATION")
    print("=" * 80)
    print(f"Address: {address}")
    print(f"Private Key: {private_key}")
    print(f"🎯 CONNECTING GRID PATTERNS TO TESA HASH GOAL")
    print("=" * 80)
    
    # Test TESA grid-based key derivation
    print("\n🎯 TESA GRID ANALYSIS")
    grid_analysis = bridge.analyze_tesa_grid_key_derivation(address, private_key, grid_size=64)
    
    print(f"\n" + "=" * 80)
    print("TESA GRID DERIVATION RESULTS")
    print("=" * 80)
    print(f"Pointer Paths: {len(grid_analysis['pointer_paths'])}")
    print(f"End Locations: {len(grid_analysis['end_locations'])}")
    print(f"Dense Areas: {len(grid_analysis['dense_areas'])}")
    print(f"Key Candidates: {len(grid_analysis['key_candidates'])}")
    print(f"Valid Keys: {len(grid_analysis['valid_keys'])}")
    
    # Use grid analysis data to improve TESA weights
    print(f"\n" + "=" * 80)
    print("🔧 IMPROVING TESA WEIGHTS FROM GRID DATA")
    print("=" * 80)
    
    weight_improvement = bridge.improve_tesa_weights_from_grid_data(grid_analysis)
    
    print(f"\n" + "=" * 80)
    print("WEIGHT IMPROVEMENT RESULTS")
    print("=" * 80)
    print(f"Dense Area Analysis: {weight_improvement['dense_area_analysis']}")
    print(f"Key Candidate Analysis: {weight_improvement['key_candidate_analysis']}")
    print(f"Weight Adjustments: {weight_improvement['weight_adjustments']}")
    print(f"Updated Base Frequency: {bridge.base_frequency} Hz")
    
    # Display dense areas
    if grid_analysis['dense_areas']:
        print(f"\n📊 DENSE AREAS (Target Areas for Valid Keys):")
        for i, area in enumerate(grid_analysis['dense_areas'][:5]):
            print(f"   {i+1}. Position: ({area['x']}, {area['y']}), Density: {area['density']}")
    
    # Display valid keys
    if grid_analysis['valid_keys']:
        print(f"\n✅ VALID BITCOIN KEYS FOUND:")
        for valid_key in grid_analysis['valid_keys']:
            print(f"   Key: {valid_key['key']}")
            print(f"   Address: {valid_key['address']}")
            print(f"   Validation: {valid_key['validation']}")
    else:
        print(f"\n⚠️  NO VALID KEYS FOUND - TESA GRID ANALYSIS DID NOT FIND CRYPTOGRAPHICALLY VALID KEYS")
    
    return grid_analysis

if __name__ == "__main__":
    test_tesa_grid_derivation()
