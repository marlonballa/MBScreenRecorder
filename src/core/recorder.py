import threading
import time
import queue
import cv2
import numpy as np
import mss
from pathlib import Path
from datetime import datetime


def get_output_dir() -> Path:
    path = Path.home() / "Recordings"
    path.mkdir(exist_ok=True)
    return path


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class Recorder:
    def __init__(self, fps: int = 15, monitor: int = 0):
        self.fps = fps
        self.monitor = monitor
        self.recording = False
        self.output_path = None
        self.frame_count = 0
        self._capture_thread = None
        self._write_thread = None
        self._frame_queue = queue.Queue(maxsize=30)

    def start(self) -> Path:
        self.output_path = get_output_dir() / f"recording_{timestamp()}.mp4"
        self.recording = True
        self.frame_count = 0

        # Thread de captura — prioridade baixa
        self._capture_thread = threading.Thread(
            target=self._capture_loop, daemon=True)

        # Thread de escrita em disco — prioridade baixa
        self._write_thread = threading.Thread(
            target=self._write_loop, daemon=True)

        self._capture_thread.start()
        self._write_thread.start()

        # Reduz prioridade no Windows
        self._set_low_priority(self._capture_thread)
        self._set_low_priority(self._write_thread)

        return self.output_path

    def stop(self):
        self.recording = False
        if self._capture_thread:
            self._capture_thread.join(timeout=5)
        # Aguarda fila esvaziar antes de fechar o writer
        self._frame_queue.join()
        if self._write_thread:
            self._write_thread.join(timeout=5)

    def _set_low_priority(self, thread):
        try:
            import ctypes
            handle = ctypes.windll.kernel32.OpenThread(0x0200, False, thread.ident)
            ctypes.windll.kernel32.SetThreadPriority(handle, -2)
            ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            pass  # Silencia em caso de erro — não crítico

    def _capture_loop(self):
        with mss.mss() as sct:
            monitor = sct.monitors[self.monitor]
            interval = 1.0 / self.fps

            while self.recording:
                t0 = time.perf_counter()

                frame = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                try:
                    self._frame_queue.put_nowait(frame)
                except queue.Full:
                    pass  # Descarta frame se fila cheia — evita acúmulo

                elapsed = time.perf_counter() - t0
                time.sleep(max(0, interval - elapsed))

            # Sinaliza fim para a thread de escrita
            self._frame_queue.put(None)

    def _write_loop(self):
        writer = None

        while True:
            frame = self._frame_queue.get()

            if frame is None:
                self._frame_queue.task_done()
                break

            if writer is None:
                h, w = frame.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(
                    str(self.output_path), fourcc, self.fps, (w, h))

            writer.write(frame)
            self.frame_count += 1
            self._frame_queue.task_done()

        if writer:
            writer.release()