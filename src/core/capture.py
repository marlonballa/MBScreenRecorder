import mss
import mss.tools
from pathlib import Path
from datetime import datetime

def get_output_dir() -> Path:
    path = Path.home() / "Screenshots"
    path.mkdir(exist_ok=True)
    return path

def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def capture_screen() -> Path:
    output_path = get_output_dir() / f"screenshot_{timestamp()}.png"

    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[0])
        mss.tools.to_png(shot.rgb, shot.size, output=output_path)

        return output_path
    
    


