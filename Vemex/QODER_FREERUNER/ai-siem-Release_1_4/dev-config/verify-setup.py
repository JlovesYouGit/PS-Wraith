#!/usr/bin/env python3
"""
Script to verify Qoder development environment setup
"""

import json
import yaml
import os

def verify_config_files():
    """Verify that the required configuration files exist and are valid"""
    
    # Check qoder-config.json
    qoder_config_path = "qoder-config.json"
    if os.path.exists(qoder_config_path):
        try:
            with open(qoder_config_path, 'r') as f:
                config = json.load(f)
            print("✓ qoder-config.json exists and is valid JSON")
            
            # Check for required sections
            required_sections = ["toolCapabilities", "developmentEnvironment", "toolAccess"]
            for section in required_sections:
                if section in config:
                    print(f"✓ {section} section present")
                else:
                    print(f"✗ {section} section missing")
        except json.JSONDecodeError as e:
            print(f"✗ qoder-config.json is not valid JSON: {e}")
    else:
        print("✗ qoder-config.json not found")
    
    # Check tool-usage-config.yaml
    tool_config_path = "tool-usage-config.yaml"
    if os.path.exists(tool_config_path):
        try:
            with open(tool_config_path, 'r') as f:
                config = yaml.safe_load(f)
            print("✓ tool-usage-config.yaml exists and is valid YAML")
            
            # Check for required sections
            required_sections = ["tool_optimization", "development_workflow", "codebase_navigation"]
            for section in required_sections:
                if section in config:
                    print(f"✓ {section} section present")
                else:
                    print(f"✗ {section} section missing")
        except Exception as e:
            print(f"✗ tool-usage-config.yaml is not valid YAML: {e}")
    else:
        print("✗ tool-usage-config.yaml not found")

def verify_directory_structure():
    """Verify that the dev-config directory structure is correct"""
    
    required_files = [
        "qoder-config.json",
        "tool-usage-config.yaml",
        "parallel-execution-config.json",
        "security-functions-config.json",
        "bridge-implementations-config.json",
        "tool-security-mapping.yaml",
        "README.md",
        "verify-setup.py",
        "parallel-tool-demo.py",
        "security-functions-demo.py",
        "bridge-loader.py"
    ]
    
    current_files = os.listdir(".")
    
    for file in required_files:
        if file in current_files:
            print(f"✓ {file} present")
        else:
            print(f"✗ {file} missing")

if __name__ == "__main__":
    print("Verifying Qoder Development Environment Setup")
    print("=" * 50)
    
    print("\nChecking directory structure:")
    verify_directory_structure()
    
    print("\nChecking configuration files:")
    verify_config_files()
    
    print("\nVerification complete!")