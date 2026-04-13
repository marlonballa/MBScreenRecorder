import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.recorder import Recorder
import time

r = Recorder(fps=24)
path = r.start()
print(f"Gravando em: {path}")

time.sleep(5)

r.stop()
print(f"Salvo! Frames: {r.frame_count}")