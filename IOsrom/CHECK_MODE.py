import subprocess
from pathlib import Path
chargfast = Path("N:/ROMLOADDER/chargfast via usb")
result = subprocess.run([str(chargfast / "irecovery.exe"), "-q"], capture_output=True, text=True, cwd=str(chargfast))
print(result.stdout)
