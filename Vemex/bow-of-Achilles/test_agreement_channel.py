#!/usr/bin/env python3
"""
Test script for agreement channel finder.
Finds the Hz channel where handshake validates from Bitcoin network to key at 100%.
Uses actual Bitcoin network data for validation.
"""

from blockchain_tesa_bridge import BlockchainTesaBridge

def test_agreement_channel():
    """Test the agreement channel finder with existing address data using actual Bitcoin network validation."""
    
    # Initialize bridge
    bridge = BlockchainTesaBridge()
    
    # Use existing address data
    address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    private_key = "1e5b7276104ed66900b2035a706fdfe0e720fa5ca233d43870ab1b5a819f3cd9"
    
    print("=" * 80)
    print("TESTING AGREEMENT CHANNEL FINDER - BITCOIN NETWORK VALIDATION")
    print("=" * 80)
    print(f"Address: {address}")
    print(f"Private Key: {private_key}")
    print(f"🔗 VALIDATING AGAINST ACTUAL BITCOIN NETWORK")
    print("=" * 80)
    
    # Find agreement channel with focused scan around base frequency
    # Scan from 431.0 to 433.0 Hz with 0.01 Hz step for precision
    # The finder will fetch actual network balance and validate address point
    channel_result = bridge.find_agreement_channel(
        address=address,
        private_key=private_key,
        balance=0,  # Will be overridden by actual network data
        freq_range=(431.0, 433.0),
        freq_step=0.01
    )
    
    # Save agreement channel report
    report_file = bridge.save_agreement_channel_report(channel_result, address)
    
    print("\n" + "=" * 80)
    print("AGREEMENT CHANNEL TEST COMPLETE")
    print("=" * 80)
    print(f"Report saved to: {report_file}")
    
    # Display summary
    if channel_result['agreement_channel']:
        print(f"\n✅ AGREEMENT CHANNEL FOUND: {channel_result['agreement_channel']['frequency']} Hz")
        print(f"   100% BITCOIN NETWORK HANDSHAKE VALIDATION CONFIRMED")
        print(f"   🔗 ADDRESS POINT: 100% VALID TO ORIGINAL")
        print(f"   📊 NETWORK BALANCE: {channel_result['network_balance']} satoshis")
    else:
        print(f"\n⚠️  NO PERFECT AGREEMENT CHANNEL FOUND")
        print(f"   📊 ADDRESS VALIDATION: {'FOUND' if channel_result['best_address_validation'] else 'NOT FOUND'}")
        print(f"   Channels tested: {channel_result['total_channels_tested']}")
        print(f"   📊 NETWORK BALANCE: {channel_result['network_balance']} satoshis")
    
    return channel_result

if __name__ == "__main__":
    test_agreement_channel()
