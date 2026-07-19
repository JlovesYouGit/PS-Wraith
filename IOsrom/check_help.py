import subprocess
from pathlib import Path
chargfast = Path("N:/ROMLOADDER/chargfast via usb")
result = subprocess.run([str(chargfast / "idevicerestore.exe"), "--help"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)
print(result.stderr)
