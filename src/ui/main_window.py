import tkinter as tk
import time
import threading
import mss
import pystray
from PIL import Image
from pathlib import Path
from tkinter import messagebox
from src.core.capture import capture_screen
from src.core.recorder import Recorder, get_output_dir
from tkinter import filedialog
from src.core.config import load_config, save_config


PASSWORD = "Splendor2026*"
HOTKEY = "<Control-Shift-S>"
ICON_PATH = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
FPS = 24


def get_monitors():
    with mss.mss() as sct:
        return sct.monitors


class PasswordDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback

        self.overrideredirect(True)
        self.configure(bg="#0f0f0f")
        self.wm_attributes("-topmost", True)

        w, h = 260, 110
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        tk.Label(self, text="Senha:", font=("Courier New", 10),
                 bg="#0f0f0f", fg="#e8e8e8").pack(pady=(18, 4))

        self.entry = tk.Entry(self, show="*", font=("Courier New", 10),
                              bg="#1a1a1a", fg="#e8e8e8",
                              insertbackground="#e8e8e8", relief="flat",
                              width=22)
        self.entry.pack(pady=(0, 12))
        self.entry.focus_force()
        self.entry.bind("<Return>", lambda e: self._confirm())
        self.entry.bind("<Escape>", lambda e: self.destroy())

        self.grab_set()

    def _confirm(self):
        result = self.entry.get()
        self.destroy()
        self.callback(result)


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Splendor O&M - Gestão")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.root.protocol("WM_DELETE_WINDOW", self._hide_to_tray)
        self.root.wm_attributes("-topmost", True)

        self.recorder = Recorder(fps=FPS)
        self.recording = False
        self.start_time = None
        self.timer_id = None
        self.tray_icon = None
        self.tray_running = False
        self.overlays = []

        self._set_icon()
        self._build_ui()
        self._position_bottom_right()
        self._setup_drag()
        self._setup_hotkey()
        self._setup_tray()

    def _set_icon(self):
        if ICON_PATH.exists():
            self.root.iconbitmap(str(ICON_PATH))

    def _position_bottom_right(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{sw - w - 20}+{sh - h - 60}")

    def _setup_drag(self):
        self.root.bind("<ButtonPress-1>", self._drag_start)
        self.root.bind("<B1-Motion>", self._drag_motion)

    def _drag_start(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _drag_motion(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def _build_ui(self):
        BG    = "#0f0f0f"
        GREEN = "#00e5a0"
        FG    = "#e8e8e8"
        MUTED = "#555555"

        self.root.configure(bg=BG)

        frame = tk.Frame(self.root, bg=BG, padx=12, pady=10)
        frame.pack()
        frame2 = tk.Frame(self.root, bg="#0f0f0f", padx=12, pady=0)
        frame2.pack(fill="x")

        tk.Button(
            frame2, text="📁  pasta",
            font=("Courier New", 8),
            bg="#0f0f0f", fg="#555555",
            relief="flat", cursor="hand2",
            padx=6, pady=2,
            command=lambda: self._ask_password_then(self._choose_folder)
        ).pack(side="left")

        tk.Button(
            frame2, text="✕",
            font=("Courier New", 8),
            bg="#0f0f0f", fg="#555555",
            relief="flat", cursor="hand2",
            padx=6, pady=2,
            command=lambda: self._ask_password_then(self._quit)
        ).pack(side="right")

        self.btn_record = tk.Button(
            frame, text="⏺",
            font=("Courier New", 12),
            bg=GREEN, fg="#000000",
            relief="flat", cursor="hand2",
            padx=8, pady=5,
            command=self._toggle_recording)
        self.btn_record.grid(row=0, column=0, padx=(0, 6))

        self.timer_var = tk.StringVar(value="00:00")
        tk.Label(
            frame, textvariable=self.timer_var,
            font=("Courier New", 12, "bold"),
            bg=BG, fg=FG, width=5).grid(row=0, column=1, padx=(0, 6))

        tk.Button(
            frame, text="📷",
            font=("Courier New", 12),
            bg="#1a1a1a", fg=FG,
            relief="flat", cursor="hand2",
            padx=8, pady=5,
            command=self._take_screenshot).grid(row=0, column=2, padx=(0, 6))

        self.monitor_var = tk.StringVar(value="Todos")
        self.btn_monitor = tk.Button(
            frame, text="Todos",
            font=("Courier New", 9),
            bg="#1a1a1a", fg=FG,
            relief="flat", cursor="hand2",
            padx=8, pady=5,
            command=self._open_monitor_menu)
        self.btn_monitor.grid(row=0, column=3, padx=(0, 6))

        tk.Button(
            frame, text="__",
            font=("Courier New", 10),
            bg="#1a1a1a", fg=MUTED,
            relief="flat", cursor="hand2",
            padx=8, pady=5,
            command=self._hide_to_tray).grid(row=0, column=4)

    def _open_monitor_menu(self):
        self._show_monitor_overlays()
        monitors = get_monitors()
        menu = tk.Menu(self.root, tearoff=0,
                       bg="#1a1a1a", fg="#e8e8e8",
                       font=("Courier New", 9),
                       activebackground="#2a2a2a",
                       activeforeground="#e8e8e8",
                       relief="flat", bd=0)
        options = ["Todos"] + [str(i) for i in range(1, len(monitors))]
        for opt in options:
            menu.add_command(label=opt, command=lambda o=opt: self._select_monitor(o))
        x = self.btn_monitor.winfo_rootx()
        y = self.btn_monitor.winfo_rooty() - (len(options) * 22)
        menu.tk_popup(x, y)

    def _show_monitor_overlays(self):
        self._hide_monitor_overlays()
        monitors = get_monitors()
        for i, mon in enumerate(monitors[1:], start=1):
            overlay = tk.Toplevel(self.root)
            overlay.overrideredirect(True)
            overlay.wm_attributes("-topmost", True)
            overlay.wm_attributes("-alpha", 0.75)
            overlay.configure(bg="#0f0f0f")
            overlay.geometry(
                f"100x80+{mon['left'] + 20}+{mon['top'] + mon['height'] - 100}")
            tk.Label(overlay, text=str(i),
                     font=("Courier New", 48, "bold"),
                     bg="#0f0f0f", fg="#00e5a0").pack(expand=True)
            self.overlays.append(overlay)
        self.root.after(4000, self._hide_monitor_overlays)

    def _hide_monitor_overlays(self):
        for o in self.overlays:
            try:
                o.destroy()
            except Exception:
                pass
        self.overlays = []

    def _choose_folder(self):
        folder = filedialog.askdirectory(title="Escolher pasta de gravações")
        if folder:
            config = load_config()
            config["output_dir"] = folder
            save_config(config)
            messagebox.showinfo("Salvo", f"Gravações serão salvas em:\n{folder}")

    def _ask_password_then(self, callback):
        def check(pwd):
            if pwd == PASSWORD:
                callback()
            elif pwd is not None:
                messagebox.showerror("Acesso negado", "Senha incorreta.")
        self.root.after(0, lambda: PasswordDialog(self.root, check))

    def _select_monitor(self, value):
        self.monitor_var.set(value)
        self.btn_monitor.configure(text=value)
        self._hide_monitor_overlays()

    def _get_monitor_index(self):
        val = self.monitor_var.get()
        if val == "Todos":
            return 0
        return int(val)

    def _setup_hotkey(self):
        self.root.bind(HOTKEY, lambda e: self._ask_password())

    def _setup_tray(self):
        if ICON_PATH.exists():
            icon_img = Image.open(str(ICON_PATH))
        else:
            icon_img = self._fallback_icon()
        menu = pystray.Menu(
            pystray.MenuItem("Abrir", lambda icon, item: self._tray_open(), default=True),
            pystray.MenuItem("Screenshot", lambda icon, item: capture_screen()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Encerrar", lambda icon, item: self._quit()),
        )
        self.tray_icon = pystray.Icon(
            "splendor_om", icon_img,
            "Splendor O&M - Gestão", menu)

    def _fallback_icon(self):
        from PIL import ImageDraw
        img = Image.new("RGB", (64, 64), "#1c1c1c")
        draw = ImageDraw.Draw(img)
        draw.polygon([(32, 10), (54, 50), (10, 50)], outline="#c8c8c8")
        return img

    def _hide_to_tray(self):
        self.root.withdraw()
        if not self.tray_running:
            self.tray_running = True
            threading.Thread(target=self._run_tray, daemon=True).start()

    def _run_tray(self):
        self.tray_icon.run()
        self.tray_running = False

    def _tray_open(self):
        self.root.after(0, self._show_password_dialog)

    def _ask_password(self, *args):
        self.root.after(0, self._show_password_dialog)

    def _show_password_dialog(self):
        self.root.deiconify()
        self.root.withdraw()
        PasswordDialog(self.root, self._check_password)

    def _check_password(self, pwd):
        if pwd == PASSWORD:
            self._show_window()
        elif pwd is not None:
            messagebox.showerror("Acesso negado", "Senha incorreta.")

    def _show_window(self):
        if self.tray_running:
            self.tray_icon.stop()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _toggle_recording(self):
        if not self.recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        monitor_idx = self._get_monitor_index()
        self.recorder = Recorder(fps=FPS, monitor=monitor_idx)
        self.recorder.start()
        self.recording = True
        self.start_time = time.time()
        self.btn_record.configure(text="⏹", bg="#ff4757", fg="#ffffff")
        self._tick()

    def _stop_recording(self):
        self.recorder.stop()
        self.recording = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.btn_record.configure(text="⏺", bg="#00e5a0", fg="#000000")
        self.timer_var.set("00:00")
        messagebox.showinfo("Encerrado", f"Gravação salva em:\n{self.recorder.output_path}")

    def _take_screenshot(self):
        path = capture_screen()
        messagebox.showinfo("Print salvo!", f"Arquivo:\n{path}")

    def _tick(self):
        if self.recording:
            elapsed = int(time.time() - self.start_time)
            self.timer_var.set(f"{elapsed // 60:02d}:{elapsed % 60:02d}")
            self.timer_id = self.root.after(500, self._tick)

    def _quit(self):
        if self.recording:
            self.recorder.stop()
        if self.tray_running:
            self.tray_icon.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()