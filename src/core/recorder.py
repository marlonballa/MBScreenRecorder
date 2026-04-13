import threading
import time
import cv2
import numpy as np
import mss
from pathlib import Path
from datetime import datetime


def get_output_dir() -> Path:
    # Cria a pasta "Recordings" na pasta home do usuário, se não existir
    path = Path.home() / "Recordings"
    path.mkdir(exist_ok=True)
    return path


def timestamp() -> str:
    # Retorna a data e hora atual formatada para uso em nomes de arquivo
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class Recorder:
    def __init__(self, fps: int = 10):
        # Taxa de quadros por segundo da gravação
        self.fps = fps
        # Indica se a gravação está em andamento
        self.recording = False
        # Caminho do arquivo de saída gerado
        self.output_path = None
        # Contador de quadros capturados
        self.frame_count = 0
        # Thread responsável pelo loop de gravação
        self._thread = None

    def start(self) -> Path:
        # Define o caminho do arquivo de saída com base no horário atual
        self.output_path = get_output_dir() / f"recording_{timestamp()}.mp4"
        self.recording = True
        self.frame_count = 0
        # Inicia a gravação em uma thread separada para não bloquear a interface
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        return self.output_path

    def stop(self):
        # Sinaliza o fim da gravação e aguarda a thread encerrar
        self.recording = False
        if self._thread:
            self._thread.join(timeout=5)

    def _record_loop(self):
        # Loop principal de captura de tela e escrita dos quadros no arquivo
        with mss.mss() as sct:
            # Seleciona o monitor principal (índice 1 no mss)
            monitor = sct.monitors[1]
            w, h = monitor["width"], monitor["height"]
            # Codec mp4v para gerar arquivos .mp4
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(self.output_path), fourcc, self.fps, (w, h))
            # Intervalo em segundos entre cada quadro
            interval = 1.0 / self.fps

            while self.recording:
                t0 = time.time()
                # Captura a tela e converte para array NumPy
                frame = np.array(sct.grab(monitor))
                # Converte de BGRA (formato do mss) para BGR (formato do OpenCV)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                writer.write(frame)
                self.frame_count += 1
                # Aguarda o tempo restante do intervalo para manter o FPS alvo
                elapsed = time.time() - t0
                time.sleep(max(0, interval - elapsed))

            # Libera o arquivo de vídeo ao encerrar
            writer.release()
