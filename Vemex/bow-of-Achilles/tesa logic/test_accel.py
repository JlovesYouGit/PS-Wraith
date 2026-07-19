import time
start = time.time()
from bridge_asi_tessa import DarkMatterFTLAccelerator
accel = DarkMatterFTLAccelerator()
signal = accel.prepare_dark_matter_signal()
elapsed_ns = (time.time() - start) * 1e9
print("Enhanced delay:", signal["enhanced_delay_s"]*1e9, "ns")
print("Actual overhead:", elapsed_ns, "ns")
print("Kerr available:", accel.kerr_bh is not None)