"""
Koda Settings — Simple GUI for configuring Koda.
Opens from the tray menu or desktop shortcut.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


class KodaSettings(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Koda Settings")
        self.geometry("520x660")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self.config_data = load_config()

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#1e1e2e", foreground="#89b4fa", font=("Segoe UI", 12, "bold"))
        style.configure("TCheckbutton", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TCombobox", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)

        # Title
        ttk.Label(main, text="Koda Settings", style="Header.TLabel").pack(anchor="w", pady=(0, 15))

        # --- Hotkeys ---
        ttk.Label(main, text="HOTKEYS", style="Header.TLabel").pack(anchor="w", pady=(10, 5))

        hk_frame = ttk.Frame(main)
        hk_frame.pack(fill="x", pady=2)

        ttk.Label(hk_frame, text="Dictation:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.hk_dict = ttk.Entry(hk_frame, width=25)
        self.hk_dict.insert(0, self.config_data.get("hotkey_dictation", "ctrl+space"))
        self.hk_dict.grid(row=0, column=1, sticky="w")

        ttk.Label(hk_frame, text="Command:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=3)
        self.hk_cmd = ttk.Entry(hk_frame, width=25)
        self.hk_cmd.insert(0, self.config_data.get("hotkey_command", "ctrl+shift+."))
        self.hk_cmd.grid(row=1, column=1, sticky="w")

        ttk.Label(hk_frame, text="Correction:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=3)
        self.hk_corr = ttk.Entry(hk_frame, width=25)
        self.hk_corr.insert(0, self.config_data.get("hotkey_correction", "ctrl+shift+z"))
        self.hk_corr.grid(row=2, column=1, sticky="w")

        ttk.Label(hk_frame, text="Read back:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=3)
        self.hk_read = ttk.Entry(hk_frame, width=25)
        self.hk_read.insert(0, self.config_data.get("hotkey_readback", "ctrl+shift+r"))
        self.hk_read.grid(row=3, column=1, sticky="w")

        # --- Model ---
        ttk.Label(main, text="SPEECH MODEL", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        model_frame = ttk.Frame(main)
        model_frame.pack(fill="x", pady=2)

        ttk.Label(model_frame, text="Model size:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.model_var = tk.StringVar(value=self.config_data.get("model_size", "base"))
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, width=22,
                                   values=["tiny", "base", "small", "medium", "large-v3"], state="readonly")
        model_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(model_frame, text="Language:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=3)
        self.lang_var = tk.StringVar(value=self.config_data.get("language", "en"))
        lang_combo = ttk.Combobox(model_frame, textvariable=self.lang_var, width=22,
                                  values=["en", "es", "fr", "de", "pt", "zh", "ja", "ko"], state="readonly")
        lang_combo.grid(row=1, column=1, sticky="w")

        # --- Mode ---
        ttk.Label(main, text="RECORDING MODE", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        self.mode_var = tk.StringVar(value=self.config_data.get("hotkey_mode", "hold"))
        mode_frame = ttk.Frame(main)
        mode_frame.pack(fill="x", pady=2)
        ttk.Radiobutton(mode_frame, text="Hold-to-talk (hold key while speaking)", variable=self.mode_var, value="hold").pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="Toggle (press once, auto-stops on silence)", variable=self.mode_var, value="toggle").pack(anchor="w")

        # --- Toggles ---
        ttk.Label(main, text="FEATURES", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        self.sound_var = tk.BooleanVar(value=self.config_data.get("sound_effects", True))
        ttk.Checkbutton(main, text="Sound effects", variable=self.sound_var).pack(anchor="w")

        self.filler_var = tk.BooleanVar(value=self.config_data.get("post_processing", {}).get("remove_filler_words", True))
        ttk.Checkbutton(main, text="Remove filler words (um, uh, you know)", variable=self.filler_var).pack(anchor="w")

        self.noise_var = tk.BooleanVar(value=self.config_data.get("noise_reduction", False))
        ttk.Checkbutton(main, text="Noise reduction (slower, for noisy environments)", variable=self.noise_var).pack(anchor="w")

        self.stream_var = tk.BooleanVar(value=self.config_data.get("streaming", True))
        ttk.Checkbutton(main, text="Streaming transcription (live preview while speaking)", variable=self.stream_var).pack(anchor="w")

        self.code_var = tk.BooleanVar(value=self.config_data.get("post_processing", {}).get("code_vocabulary", False))
        ttk.Checkbutton(main, text="Code vocabulary (open paren → ( in command mode)", variable=self.code_var).pack(anchor="w")

        # --- Read-back voice ---
        ttk.Label(main, text="READ-BACK", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        voice_frame = ttk.Frame(main)
        voice_frame.pack(fill="x", pady=2)

        self.voices = self._get_voices()
        voice_names = [name for name, _ in self.voices]
        current_voice = self.config_data.get("tts", {}).get("voice", voice_names[0] if voice_names else "")

        ttk.Label(voice_frame, text="Voice:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.voice_var = tk.StringVar(value=current_voice)
        if voice_names:
            voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_var, width=35,
                                       values=voice_names, state="readonly")
            voice_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(voice_frame, text="Speed:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=3)
        current_speed = self.config_data.get("tts", {}).get("rate", "normal")
        self.speed_var = tk.StringVar(value=current_speed)
        speed_combo = ttk.Combobox(voice_frame, textvariable=self.speed_var, width=35,
                                   values=["slow", "normal", "fast"], state="readonly")
        speed_combo.grid(row=1, column=1, sticky="w")

        # --- Buttons ---
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=(20, 0))

        ttk.Button(btn_frame, text="Save & Restart Koda", command=self.save_and_restart).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="Cancel", command=self.on_close).pack(side="left")

    def _get_voices(self):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            return [(v.name, v.id) for v in engine.getProperty('voices')]
        except Exception:
            return []

    def save(self):
        cfg = self.config_data

        cfg["hotkey_dictation"] = self.hk_dict.get().strip()
        cfg["hotkey_command"] = self.hk_cmd.get().strip()
        cfg["hotkey_correction"] = self.hk_corr.get().strip()
        cfg["hotkey_readback"] = self.hk_read.get().strip()
        cfg["model_size"] = self.model_var.get()
        cfg["language"] = self.lang_var.get()
        cfg["hotkey_mode"] = self.mode_var.get()
        cfg["sound_effects"] = self.sound_var.get()
        cfg["noise_reduction"] = self.noise_var.get()
        cfg["streaming"] = self.stream_var.get()

        pp = cfg.setdefault("post_processing", {})
        pp["remove_filler_words"] = self.filler_var.get()
        pp["code_vocabulary"] = self.code_var.get()

        tts = cfg.setdefault("tts", {})
        tts["voice"] = self.voice_var.get()
        tts["rate"] = self.speed_var.get()

        save_config(cfg)
        messagebox.showinfo("Koda", "Settings saved! Restart Koda for changes to take effect.")

    def save_and_restart(self):
        self.save()
        # Kill running Koda instances
        import subprocess
        subprocess.run(["powershell", "-Command",
                        "Get-Process pythonw -ErrorAction SilentlyContinue | Stop-Process -Force"],
                       capture_output=True)
        import time
        time.sleep(1)
        # Restart
        start_bat = os.path.join(SCRIPT_DIR, "start.bat")
        subprocess.Popen(["cmd", "/c", start_bat], cwd=SCRIPT_DIR,
                         creationflags=subprocess.CREATE_NO_WINDOW)
        self.destroy()

    def on_close(self):
        self.destroy()


if __name__ == "__main__":
    app = KodaSettings()
    app.mainloop()
