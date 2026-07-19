#!/usr/bin/env python3
import zipfile
import os
import sys

class IPSWTool:
    def extract_all(self, ipsw_path, output_dir):
        """Extract IPSW contents"""
        try:
            os.makedirs(output_dir, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"Permission denied creating directory: {output_dir}")
        
        try:
            with zipfile.ZipFile(ipsw_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
        except zipfile.BadZipFile:
            raise ValueError(f"Invalid IPSW file: {ipsw_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"IPSW file not found: {ipsw_path}")
        
        print(f"Extracted IPSW to {output_dir}")
    
    def extract_file(self, ipsw_path, filename, output_path):
        """Extract specific file from IPSW"""
        try:
            with zipfile.ZipFile(ipsw_path, 'r') as zip_ref:
                try:
                    with zip_ref.open(filename) as source:
                        with open(output_path, 'wb') as target:
                            target.write(source.read())
                    print(f"Extracted {filename} to {output_path}")
                except KeyError:
                    print(f"File {filename} not found in IPSW")
        except zipfile.BadZipFile:
            raise ValueError(f"Invalid IPSW file: {ipsw_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"IPSW file not found: {ipsw_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied writing to: {output_path}")
    
    def list_contents(self, ipsw_path):
        """List IPSW contents"""
        with zipfile.ZipFile(ipsw_path, 'r') as zip_ref:
            for info in zip_ref.infolist():
                print(f"{info.filename} ({info.file_size} bytes)")

def main():
    if len(sys.argv) < 3:
        print("Usage: python ipsw_tool.py -extract <ipsw> <output_dir>")
        print("       python ipsw_tool.py -file <ipsw> <filename> <output>")
        print("       python ipsw_tool.py -list <ipsw>")
        sys.exit(1)
    
    tool = IPSWTool()
    
    try:
        if sys.argv[1] == '-extract' and len(sys.argv) >= 4:
            tool.extract_all(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == '-file' and len(sys.argv) >= 5:
            tool.extract_file(sys.argv[2], sys.argv[3], sys.argv[4])
        elif sys.argv[1] == '-list' and len(sys.argv) >= 3:
            tool.list_contents(sys.argv[2])
        else:
            print("Invalid arguments")
            sys.exit(1)
    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()