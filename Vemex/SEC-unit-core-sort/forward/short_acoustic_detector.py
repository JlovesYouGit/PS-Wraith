import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from acoustic_fluctuation_detector import AcousticFluctuationDetector

# Create detector with shorter monitoring period
detector = AcousticFluctuationDetector(
    monitoring_duration=10,  # Just 10 seconds for demo
    sampling_interval=0.5
)

# Run detection
results = detector.run_detection()