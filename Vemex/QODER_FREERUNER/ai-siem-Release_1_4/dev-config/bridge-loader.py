#!/usr/bin/env python3
"""
Script to detect and load bridge implementations for placeholder parsers
"""

import os
import json
import yaml

def load_bridge_config():
    """Load the bridge implementations configuration"""
    config_path = "bridge-implementations-config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def find_bridge_files(parser_path):
    """Find bridge implementation files in a parser directory"""
    bridge_files = []
    if os.path.exists(parser_path):
        for file in os.listdir(parser_path):
            if file.endswith("_bridge.conf"):
                bridge_files.append(file)
    return bridge_files

def validate_bridge_implementation(parser_path, bridge_file):
    """Validate that a bridge implementation is complete"""
    bridge_path = os.path.join(parser_path, bridge_file)
    if not os.path.exists(bridge_path):
        return False, "Bridge file not found"
    
    # Check that the bridge file has content
    try:
        with open(bridge_path, 'r') as f:
            content = f.read()
            if len(content.strip()) == 0:
                return False, "Bridge file is empty"
    except Exception as e:
        return False, f"Error reading bridge file: {e}"
    
    return True, "Bridge implementation is valid"

def get_parser_metadata(parser_path):
    """Get metadata for a parser"""
    metadata_path = os.path.join(parser_path, "metadata.yaml")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not read metadata for {parser_path}: {e}")
    return {}

def check_parser_needs_bridge(parser_path):
    """Check if a parser is marked as a placeholder or needs bridging"""
    metadata = get_parser_metadata(parser_path)
    if metadata and "metadata_details" in metadata:
        details = metadata["metadata_details"]
        # Check if performance impact indicates it's a placeholder
        if "performance_impact" in details:
            impact = details["performance_impact"]
            if "placeholder" in impact.lower():
                return True, "Marked as placeholder in metadata"
        
        # Check if purpose indicates it's migrated and potentially incomplete
        if "purpose" in details:
            purpose = details["purpose"]
            if "migrated" in purpose.lower() and "placeholder" in purpose.lower():
                return True, "Migrated placeholder implementation"
    
    return False, "No bridge needed"

def load_all_bridges():
    """Load all bridge implementations"""
    print("🔍 Detecting and loading bridge implementations...")
    print("=" * 50)
    
    config = load_bridge_config()
    if not config:
        print("❌ Bridge configuration not found")
        return [], []
    
    bridges = config.get("bridgeImplementations", {}).get("parsers", {})
    
    loaded_bridges = []
    failed_bridges = []
    
    for parser_name, bridge_info in bridges.items():
        parser_path = bridge_info["originalPath"]
        bridge_file = bridge_info["bridgeFile"]
        
        print(f"\n📄 Checking {parser_name}...")
        
        # Validate the bridge implementation
        is_valid, message = validate_bridge_implementation(parser_path, bridge_file)
        if is_valid:
            print(f"✅ {bridge_file} - {message}")
            loaded_bridges.append({
                "parser": parser_name,
                "path": parser_path,
                "bridge": bridge_file,
                "description": bridge_info.get("description", "No description")
            })
        else:
            print(f"❌ {bridge_file} - {message}")
            failed_bridges.append({
                "parser": parser_name,
                "path": parser_path,
                "bridge": bridge_file,
                "error": message
            })
    
    print(f"\n📊 Summary:")
    print(f"✅ Successfully loaded: {len(loaded_bridges)} bridges")
    print(f"❌ Failed to load: {len(failed_bridges)} bridges")
    
    if loaded_bridges:
        print("\n✅ Loaded bridges:")
        for bridge in loaded_bridges:
            print(f"  • {bridge['parser']}: {bridge['description']}")
    
    if failed_bridges:
        print("\n❌ Failed bridges:")
        for bridge in failed_bridges:
            print(f"  • {bridge['parser']}: {bridge['error']}")
    
    return loaded_bridges, failed_bridges

def auto_detect_bridges():
    """Automatically detect parsers that need bridges"""
    print("🔍 Auto-detecting parsers that need bridges...")
    print("=" * 50)
    
    parsers_root = "../parsers/community"
    if not os.path.exists(parsers_root):
        print("❌ Parsers directory not found")
        return
    
    placeholder_parsers = []
    
    for parser_dir in os.listdir(parsers_root):
        parser_path = os.path.join(parsers_root, parser_dir)
        if os.path.isdir(parser_path):
            needs_bridge, reason = check_parser_needs_bridge(parser_path)
            if needs_bridge:
                bridge_files = find_bridge_files(parser_path)
                placeholder_parsers.append({
                    "name": parser_dir,
                    "path": parser_path,
                    "reason": reason,
                    "bridge_files": bridge_files
                })
    
    if placeholder_parsers:
        print(f"🔍 Found {len(placeholder_parsers)} parsers that may need bridges:")
        for parser in placeholder_parsers:
            print(f"  • {parser['name']} - {parser['reason']}")
            if parser['bridge_files']:
                print(f"    🔄 Bridge files found: {', '.join(parser['bridge_files'])}")
            else:
                print(f"    ⚠️  No bridge files found")
    else:
        print("✅ No placeholder parsers found that need bridges")
    
    return placeholder_parsers

if __name__ == "__main__":
    print("🌉 AI-SIEM Bridge Implementation Loader")
    print("=" * 60)
    
    # Load configured bridges
    loaded_bridges, failed_bridges = load_all_bridges()
    
    print("\n" + "=" * 60)
    
    # Auto-detect placeholder parsers
    placeholder_parsers = auto_detect_bridges()
    
    print("\n🎉 Bridge loading complete!")
    print(f"📊 Results: {len(loaded_bridges)} bridges loaded, {len(failed_bridges)} failed")