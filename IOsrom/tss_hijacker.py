#!/usr/bin/env python3
"""TSS Server Hijacker - Intercept iTunes SHSH requests and provide fake responses"""
import socket
import threading
import sys
import time
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Create log file
log_file = "itunes_requests.log"
with open(log_file, 'w') as f:
    f.write(f"iTunes Request Log - {datetime.datetime.now()}\n")
    f.write("=" * 50 + "\n\n")

def log_to_file(message):
    """Log message to both console and file"""
    print(message)
    with open(log_file, 'a') as f:
        f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}\n")

class TSSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle iTunes TSS requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        log_to_file(f"\n[+] POST REQUEST from iTunes")
        log_to_file(f"[+] Path: {self.path}")
        log_to_file(f"[+] Headers: {dict(self.headers)}")
        log_to_file(f"[+] Content Length: {content_length} bytes")
        log_to_file(f"[+] Post Data (first 200 chars): {post_data[:200]}")
        
        # Save full post data to file
        with open(log_file, 'a') as f:
            f.write(f"FULL POST DATA:\n{post_data.decode('utf-8', errors='ignore')}\n")
            f.write("-" * 30 + "\n")
        
        # Check if it's photo sync request
        if b'photo' in post_data.lower() or 'photo' in self.path.lower():
            log_to_file("[!] DETECTED: Photo sync request - bypassing")
            fake_response = '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict><key>PhotoSyncDisabled</key><true/></dict></plist>'''
        elif b'tss' in post_data.lower() or 'tss' in self.path.lower():
            log_to_file("[!] DETECTED: TSS/SHSH request - sending fake blob")
            fake_response = self.create_fake_shsh()
        else:
            log_to_file("[!] DETECTED: Unknown request - sending generic success")
            fake_response = '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict><key>Status</key><string>SUCCESS</string></dict></plist>'''
        
        # Send successful response
        self.send_response(200)
        self.send_header('Content-Type', 'text/xml; charset=UTF-8')
        self.send_header('Content-Length', str(len(fake_response)))
        self.send_header('Server', 'Apple')
        self.end_headers()
        self.wfile.write(fake_response.encode())
        
        log_to_file(f"[✅] Sent {len(fake_response)} byte response to iTunes\n")
        
        # Save response to file
        with open(log_file, 'a') as f:
            f.write(f"RESPONSE SENT:\n{fake_response}\n")
            f.write("=" * 50 + "\n\n")
    
    def create_fake_shsh(self):
        """Create fake SHSH blob that iTunes accepts"""
        # Proper TSS response format
        fake_blob = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>@APTicket</key>
	<data>ZmFrZV90aWNrZXRfZGF0YQ==</data>
	<key>@BBTicket</key>
	<data>ZmFrZV9iYXNlYmFuZF90aWNrZXQ=</data>
	<key>@HostPlatformInfo</key>
	<string>windows</string>
</dict>
</plist>'''
        return fake_blob
    
    def do_GET(self):
        """Handle iTunes GET requests (photo sync, etc.)"""
        log_to_file(f"\n[+] GET REQUEST from iTunes")
        log_to_file(f"[+] Path: {self.path}")
        log_to_file(f"[+] Headers: {dict(self.headers)}")
        
        if 'photo' in self.path.lower():
            log_to_file("[!] DETECTED: Photo sync GET request - bypassing")
            response = '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict><key>PhotoAppAvailable</key><true/></dict></plist>'''
        elif 'tss' in self.path.lower():
            log_to_file("[!] DETECTED: TSS GET request - sending success")
            response = '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict><key>Status</key><string>OK</string></dict></plist>'''
        else:
            log_to_file("[!] DETECTED: Generic GET request - sending OK")
            response = '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict><key>Status</key><string>OK</string></dict></plist>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/xml; charset=UTF-8')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode())
        
        log_to_file(f"[✅] Sent {len(response)} byte response to iTunes\n")
        
        # Save response to file
        with open(log_file, 'a') as f:
            f.write(f"GET RESPONSE SENT:\n{response}\n")
            f.write("=" * 50 + "\n\n")
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def start_tss_server():
    """Start fake TSS server on port 80"""
    try:
        server = HTTPServer(('127.0.0.1', 80), TSSHandler)
        log_to_file("[+] TSS Hijacker started on 127.0.0.1:80")
        log_to_file("[+] iTunes requests will be intercepted")
        log_to_file(f"[+] Logging to file: {log_file}")
        log_to_file("[+] Press Ctrl+C to stop")
        server.serve_forever()
    except PermissionError:
        print("[!] Need Administrator privileges to bind to port 80")
        print("[!] Run as Administrator")
        return False
    except Exception as e:
        print(f"[!] TSS server failed: {e}")
        return False

def setup_dns_hijack():
    """Setup DNS hijacking for Apple servers"""
    hosts_entries = [
        "127.0.0.1 gs.apple.com",
        "127.0.0.1 phobos.apple.com", 
        "127.0.0.1 albert.apple.com",
        "127.0.0.1 ocsp.apple.com",
        "127.0.0.1 crl.apple.com",
        "127.0.0.1 valid.apple.com",
        "127.0.0.1 init.itunes.apple.com",
        "127.0.0.1 iosapps.itunes.apple.com",
        "127.0.0.1 itunes.apple.com",
        "127.0.0.1 ax.itunes.apple.com",
        "127.0.0.1 se.itunes.apple.com",
        "127.0.0.1 su.itunes.apple.com",
        "127.0.0.1 client-api.itunes.apple.com",
        "127.0.0.1 photos.apple.com",
        "127.0.0.1 configuration.apple.com"
    ]
    
    hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
    
    try:
        # Read existing hosts
        with open(hosts_file, 'r') as f:
            existing = f.read()
        
        # Add our entries if not present
        modified = existing
        for entry in hosts_entries:
            if entry not in existing:
                modified += f"\n{entry}"
        
        # Write back
        with open(hosts_file, 'w') as f:
            f.write(modified)
        
        log_to_file("[+] DNS hijacking configured")
        return True
        
    except PermissionError:
        print("[!] Cannot modify hosts file - run as Administrator")
        return False
    except Exception as e:
        print(f"[!] DNS setup failed: {e}")
        return False

def main():
    """Main TSS hijacker"""
    log_to_file("[+] iTunes TSS Hijacker")
    log_to_file("[+] This will intercept iTunes SHSH requests")
    
    # Setup DNS hijacking
    if not setup_dns_hijack():
        print("[!] DNS hijacking failed")
        return
    
    log_to_file("[+] Instructions:")
    log_to_file("1. Keep this running")
    log_to_file("2. Start iTunes restore in another window")
    log_to_file("3. iTunes will get fake SHSH blobs from this server")
    log_to_file(f"4. All requests logged to: {log_file}")
    log_to_file("")
    
    # Start TSS server
    start_tss_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_to_file("\n[+] TSS Hijacker stopped")
        sys.exit(0)