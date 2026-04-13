import tkinter as tk
from tkinter import messagebox
import threading
import time
from src.core.capture import capture_screen
from src.core.recorder import Recorder


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MBScreenRecorder")
        self.root.resizable(False, False)

        self.recorder = Recorder(fps=24)
        self.recording = False
        self.start_time = None
        self.timer_id = None

        self._build_ui()

    def _build_ui(self):
        BG      = "#0f0f0f"
        CARD    = "#1a1a1a"
        GREEN   = "#00e5a0"
        RED     = "#ff4757"
        FG      = "#e8e8e8"
        MUTED   = "#888888"

        self.root.configure(bg=BG)

        # Título
        tk.Label(self.root, text="MB SCREEN RECORDER",
                 font=("Courier New", 11, "bold"),
                 bg=BG, fg=GREEN).pack(pady=(20, 4))

        # Card central
        card = tk.Frame(self.root, bg=CARD, padx=24, pady=20)
        card.pack(padx=20, fill="x")

        # Cronômetro
        self.timer_var = tk.StringVar(value="00:00")
        tk.Label(card, textvariable=self.timer_var,
                 font=("Courier New", 36, "bold"),
                 bg=CARD, fg=FG).pack()

        # Status
        self.status_var = tk.StringVar(value="Pronto")
        self.status_label = tk.Label(card, textvariable=self.status_var,
                                     font=("Courier New", 9),
                                     bg=CARD, fg=MUTED)
        self.status_label.pack(pady=(4, 16))

        # Botões
        btn_frame = tk.Frame(card, bg=CARD)
        btn_frame.pack(fill="x")

        self.btn_record = tk.Button(
            btn_frame, text="⏺  GRAVAR",
            font=("Courier New", 10, "bold"),
            bg=GREEN, fg="#000000",
            relief="flat", cursor="hand2",
            padx=12, pady=8,
            command=self._toggle_recording)
        self.btn_record.pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            btn_frame, text="📷  PRINT",
            font=("Courier New", 10, "bold"),
            bg="#2a2a2a", fg=FG,
            relief="flat", cursor="hand2",
            padx=12, pady=8,
            command=self._take_screenshot).pack(side="left", fill="x", expand=True)

        # Abrir pasta
        tk.Button(card, text="📁  abrir pasta de gravações",
                  font=("Courier New", 8),
                  bg=CARD, fg=MUTED,
                  relief="flat", cursor="hand2",
                  command=self._open_folder).pack(pady=(14, 0))

    def _toggle_recording(self):
        if not self.recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        self.recorder.start()
        self.recording = True
        self.start_time = time.time()
        self.btn_record.configure(text="⏹  PARAR", bg="#ff4757", fg="#ffffff")
        self.status_var.set("● gravando...")
        self.status_label.configure(fg="#ff4757")
        self._tick()

    def _stop_recording(self):
        self.recorder.stop()
        self.recording = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.btn_record.configure(text="⏺  GRAVAR", bg="#00e5a0", fg="#000000")
        self.status_var.set("Pronto")
        self.status_label.configure(fg="#888888")
        self.timer_var.set("00:00")
        messagebox.showinfo("Salvo!", f"Gravação salva em:\n{self.recorder.output_path}")

    def _take_screenshot(self):
        path = capture_screen()
        messagebox.showinfo("Print salvo!", f"Arquivo:\n{path}")

    def _open_folder(self):
        import os
        from src.core.recorder import get_output_dir
        os.startfile(get_output_dir())

    def _tick(self):
        if self.recording:
            elapsed = int(time.time() - self.start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            self.timer_var.set(f"{mins:02d}:{secs:02d}")
            self.timer_id = self.root.after(500, self._tick)

    def run(self):
        self.root.mainloop()