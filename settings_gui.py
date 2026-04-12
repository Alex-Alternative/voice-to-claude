"""
Koda Settings — Simple GUI for configuring Koda.
Opens from the tray menu or desktop shortcut.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
        self.geometry("520x1020")
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

        # Safe hotkey options: F-keys and ctrl+space (proven to work without conflicts)
        FKEY_OPTIONS = ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"]
        DICTATION_OPTIONS = ["ctrl+space", "ctrl+alt+d"] + FKEY_OPTIONS

        ttk.Label(hk_frame, text="Dictation:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.hk_dict_var = tk.StringVar(value=self.config_data.get("hotkey_dictation", "ctrl+space"))
        ttk.Combobox(hk_frame, textvariable=self.hk_dict_var, width=22,
                     values=DICTATION_OPTIONS, state="readonly").grid(row=0, column=1, sticky="w")

        ttk.Label(hk_frame, text="Command:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=3)
        self.hk_cmd_var = tk.StringVar(value=self.config_data.get("hotkey_command", "f8"))
        ttk.Combobox(hk_frame, textvariable=self.hk_cmd_var, width=22,
                     values=FKEY_OPTIONS, state="readonly").grid(row=1, column=1, sticky="w")

        ttk.Label(hk_frame, text="Prompt Assist:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=3)
        self.hk_prompt_var = tk.StringVar(value=self.config_data.get("hotkey_prompt", "f9"))
        ttk.Combobox(hk_frame, textvariable=self.hk_prompt_var, width=22,
                     values=FKEY_OPTIONS, state="readonly").grid(row=2, column=1, sticky="w")

        ttk.Label(hk_frame, text="Correction:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=3)
        self.hk_corr_var = tk.StringVar(value=self.config_data.get("hotkey_correction", "f7"))
        ttk.Combobox(hk_frame, textvariable=self.hk_corr_var, width=22,
                     values=FKEY_OPTIONS, state="readonly").grid(row=3, column=1, sticky="w")

        ttk.Label(hk_frame, text="Read back:").grid(row=4, column=0, sticky="w", padx=(0, 10), pady=3)
        self.hk_read_var = tk.StringVar(value=self.config_data.get("hotkey_readback", "f6"))
        ttk.Combobox(hk_frame, textvariable=self.hk_read_var, width=22,
                     values=FKEY_OPTIONS, state="readonly").grid(row=4, column=1, sticky="w")

        ttk.Label(hk_frame, text="Read selected:").grid(row=5, column=0, sticky="w", padx=(0, 10), pady=3)
        self.hk_readsel_var = tk.StringVar(value=self.config_data.get("hotkey_readback_selected", "f5"))
        ttk.Combobox(hk_frame, textvariable=self.hk_readsel_var, width=22,
                     values=FKEY_OPTIONS, state="readonly").grid(row=5, column=1, sticky="w")

        # --- Model ---
        ttk.Label(main, text="SPEECH MODEL", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        model_frame = ttk.Frame(main)
        model_frame.pack(fill="x", pady=2)

        ttk.Label(model_frame, text="Model size:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.model_var = tk.StringVar(value=self.config_data.get("model_size", "base"))
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, width=22,
                                   values=["tiny", "base", "small", "medium", "large-v2", "large-v3",
                                           "large-v3-turbo", "distil-large-v3", "distil-medium.en"],
                                   state="readonly")
        model_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(model_frame, text="Language:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=3)
        self.lang_var = tk.StringVar(value=self.config_data.get("language", "en"))
        lang_combo = ttk.Combobox(model_frame, textvariable=self.lang_var, width=22,
                                  values=["en", "es", "fr", "de", "pt", "zh", "ja", "ko",
                                          "ar", "hi", "ru", "it", "nl", "pl", "tr", "auto"],
                                  state="readonly")
        lang_combo.grid(row=1, column=1, sticky="w")

        # --- Mode ---
        ttk.Label(main, text="RECORDING MODE", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        self.mode_var = tk.StringVar(value=self.config_data.get("hotkey_mode", "hold"))
        mode_frame = ttk.Frame(main)
        mode_frame.pack(fill="x", pady=2)
        ttk.Radiobutton(mode_frame, text="Hold-to-talk (hold key while speaking)", variable=self.mode_var, value="hold").pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="Toggle (press once, auto-stops on silence)", variable=self.mode_var, value="toggle").pack(anchor="w")

        # --- Output Mode ---
        ttk.Label(main, text="OUTPUT MODE", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        self.output_var = tk.StringVar(value=self.config_data.get("output_mode", "auto_paste"))
        output_frame = ttk.Frame(main)
        output_frame.pack(fill="x", pady=2)
        ttk.Radiobutton(output_frame, text="Auto-paste (copy + Ctrl+V into active window)", variable=self.output_var, value="auto_paste").pack(anchor="w")
        ttk.Radiobutton(output_frame, text="Clipboard only (copy to clipboard, no paste)", variable=self.output_var, value="clipboard").pack(anchor="w")

        # --- Custom Words ---
        ttk.Label(main, text="CUSTOM WORDS", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        cw_frame = ttk.Frame(main)
        cw_frame.pack(fill="x", pady=2)
        ttk.Label(cw_frame, text="Replace misheard words with correct versions:").pack(anchor="w")
        btn_row = ttk.Frame(cw_frame)
        btn_row.pack(anchor="w", pady=(5, 0))
        ttk.Button(btn_row, text="Edit custom_words.json", command=self._open_custom_words).pack(side="left", padx=(0, 10))
        ttk.Button(btn_row, text="Edit profiles.json", command=self._open_profiles).pack(side="left")

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

        self.autoformat_var = tk.BooleanVar(value=self.config_data.get("post_processing", {}).get("auto_format", True))
        ttk.Checkbutton(main, text="Auto-format (numbers, dates, smart punctuation)", variable=self.autoformat_var).pack(anchor="w")

        self.overlay_var = tk.BooleanVar(value=self.config_data.get("overlay_enabled", True))
        ttk.Checkbutton(main, text="Floating status overlay (live recording preview)", variable=self.overlay_var).pack(anchor="w")

        self.voicecmds_var = tk.BooleanVar(value=self.config_data.get("voice_commands", True))
        ttk.Checkbutton(main, text="Voice commands (say 'select all', 'undo', 'new line')", variable=self.voicecmds_var).pack(anchor="w")

        self.profiles_var = tk.BooleanVar(value=self.config_data.get("profiles_enabled", True))
        ttk.Checkbutton(main, text="Per-app profiles (auto-switch settings by active window)", variable=self.profiles_var).pack(anchor="w")

        # --- Translation ---
        ttk.Label(main, text="TRANSLATION", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        trans_frame = ttk.Frame(main)
        trans_frame.pack(fill="x", pady=2)

        self.trans_var = tk.BooleanVar(value=self.config_data.get("translation", {}).get("enabled", False))
        ttk.Checkbutton(trans_frame, text="Enable translation (speak one language, type another)",
                         variable=self.trans_var).pack(anchor="w")

        target_frame = ttk.Frame(main)
        target_frame.pack(fill="x", pady=2)
        ttk.Label(target_frame, text="Target language:").pack(side="left", padx=(0, 10))
        self.trans_lang_var = tk.StringVar(value=self.config_data.get("translation", {}).get("target_language", "English"))
        trans_combo = ttk.Combobox(target_frame, textvariable=self.trans_lang_var, width=22,
                                   values=["English", "Spanish", "French", "German", "Portuguese",
                                           "Japanese", "Korean", "Chinese", "Italian", "Russian"],
                                   state="readonly")
        trans_combo.pack(side="left")
        ttk.Label(target_frame, text="(English uses Whisper; others need Ollama)").pack(side="left", padx=(10, 0))

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

        # --- Performance ---
        ttk.Label(main, text="PERFORMANCE", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        perf_frame = ttk.Frame(main)
        perf_frame.pack(fill="x", pady=2)

        current_compute = self.config_data.get("compute_type", "int8")
        mode_label = "Power Mode (NVIDIA GPU)" if current_compute == "float16" else "Standard Mode (CPU)"
        ttk.Label(perf_frame, text=f"Current mode:  {mode_label}").pack(anchor="w")

        self._perf_status_var = tk.StringVar(value="")
        ttk.Label(perf_frame, textvariable=self._perf_status_var,
                  foreground="#a6e3a1").pack(anchor="w", pady=(2, 0))

        perf_btn_row = ttk.Frame(perf_frame)
        perf_btn_row.pack(anchor="w", pady=(6, 0))
        ttk.Button(perf_btn_row, text="Check GPU", command=self._check_gpu).pack(side="left", padx=(0, 8))
        if current_compute != "float16":
            ttk.Button(perf_btn_row, text="Enable Power Mode",
                       command=self._enable_power_mode).pack(side="left", padx=(0, 8))
        else:
            ttk.Button(perf_btn_row, text="Switch to Standard Mode",
                       command=self._disable_power_mode).pack(side="left", padx=(0, 8))
        ttk.Button(perf_btn_row, text="Learn more",
                   command=self._open_cuda_url).pack(side="left")

        # --- History ---
        ttk.Label(main, text="HISTORY", style="Header.TLabel").pack(anchor="w", pady=(15, 5))

        hist_frame = ttk.Frame(main)
        hist_frame.pack(fill="x", pady=2)
        ttk.Button(hist_frame, text="View transcript history", command=self._open_history).pack(side="left", padx=(0, 10))
        ttk.Button(hist_frame, text="Export history", command=self._export_history).pack(side="left")

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

        cfg["hotkey_dictation"] = self.hk_dict_var.get()
        cfg["hotkey_command"] = self.hk_cmd_var.get()
        cfg["hotkey_prompt"] = self.hk_prompt_var.get()
        cfg["hotkey_correction"] = self.hk_corr_var.get()
        cfg["hotkey_readback"] = self.hk_read_var.get()
        cfg["hotkey_readback_selected"] = self.hk_readsel_var.get()
        cfg["model_size"] = self.model_var.get()
        cfg["language"] = self.lang_var.get()
        cfg["hotkey_mode"] = self.mode_var.get()
        cfg["output_mode"] = self.output_var.get()
        cfg["sound_effects"] = self.sound_var.get()
        cfg["noise_reduction"] = self.noise_var.get()
        cfg["streaming"] = self.stream_var.get()
        cfg["overlay_enabled"] = self.overlay_var.get()
        cfg["profiles_enabled"] = self.profiles_var.get()
        cfg["voice_commands"] = self.voicecmds_var.get()

        trans = cfg.setdefault("translation", {})
        trans["enabled"] = self.trans_var.get()
        trans["target_language"] = self.trans_lang_var.get()

        pp = cfg.setdefault("post_processing", {})
        pp["remove_filler_words"] = self.filler_var.get()
        pp["code_vocabulary"] = self.code_var.get()
        pp["auto_format"] = self.autoformat_var.get()

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
                        "Get-Process pythonw,python -ErrorAction SilentlyContinue | Stop-Process -Force"],
                       capture_output=True)
        import time
        time.sleep(1)
        # Restart
        start_bat = os.path.join(SCRIPT_DIR, "start.bat")
        subprocess.Popen(["cmd", "/c", start_bat], cwd=SCRIPT_DIR,
                         creationflags=subprocess.CREATE_NO_WINDOW)
        self.destroy()

    def _open_custom_words(self):
        """Open custom_words.json in the default editor."""
        custom_words_path = os.path.join(SCRIPT_DIR, "custom_words.json")
        if not os.path.exists(custom_words_path):
            with open(custom_words_path, "w", encoding="utf-8") as f:
                json.dump({"coda": "Koda", "claude code": "Claude Code"}, f, indent=2)
        os.startfile(custom_words_path)

    def _open_profiles(self):
        """Open profiles.json in the default editor."""
        profiles_path = os.path.join(SCRIPT_DIR, "profiles.json")
        if not os.path.exists(profiles_path):
            from profiles import load_profiles
            load_profiles()  # Creates default file
        os.startfile(profiles_path)

    def _open_history(self):
        """Open a simple history viewer window."""
        try:
            from history import get_recent, search_history
        except ImportError:
            messagebox.showerror("Koda", "History module not found.")
            return

        hist_win = tk.Toplevel(self)
        hist_win.title("Koda - Transcript History")
        hist_win.geometry("600x450")
        hist_win.configure(bg="#1e1e2e")

        top_frame = ttk.Frame(hist_win)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(top_frame, text="Search:").pack(side="left", padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=search_var, width=40)
        search_entry.pack(side="left", padx=(0, 5))

        text_widget = tk.Text(hist_win, bg="#313244", fg="#cdd6f4", font=("Consolas", 10),
                              wrap="word", state="disabled")
        text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def refresh(query=None):
            if query:
                rows = search_history(query, limit=50)
            else:
                rows = get_recent(limit=50)
            text_widget.config(state="normal")
            text_widget.delete("1.0", "end")
            if not rows:
                text_widget.insert("end", "No transcriptions found.")
            else:
                for row in rows:
                    _id, ts, text, mode, dur = row
                    ts_short = ts[:19].replace("T", " ") if ts else ""
                    text_widget.insert("end", f"[{ts_short}] ({mode}, {dur:.1f}s)\n")
                    text_widget.insert("end", f"  {text}\n\n")
            text_widget.config(state="disabled")

        def on_search(*args):
            query = search_var.get().strip()
            refresh(query if query else None)

        ttk.Button(top_frame, text="Search", command=on_search).pack(side="left")
        search_entry.bind("<Return>", on_search)

        refresh()

    def _export_history(self):
        """Export transcript history to a text file."""
        try:
            from history import export_history
        except ImportError:
            messagebox.showerror("Koda", "History module not found.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Transcript History",
        )
        if filepath:
            try:
                export_history(filepath)
                messagebox.showinfo("Koda", f"History exported to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Koda", f"Export failed: {e}")

    def _check_gpu(self):
        """Run GPU detection and report result in the UI."""
        self._perf_status_var.set("Checking...")
        self.update_idletasks()
        try:
            from hardware import detect_gpu, get_nvidia_gpu_name
            status = detect_gpu()
            if status == "cuda_ready":
                gpu = get_nvidia_gpu_name() or "NVIDIA GPU"
                self._perf_status_var.set(f"Power Mode available — {gpu} detected with CUDA ready.")
            elif status == "nvidia_no_cuda":
                gpu = get_nvidia_gpu_name() or "NVIDIA GPU"
                self._perf_status_var.set(f"{gpu} found but CUDA not set up. Click 'Enable Power Mode' to try.")
            else:
                self._perf_status_var.set("No NVIDIA GPU detected — Standard Mode is the right choice.")
        except Exception as e:
            self._perf_status_var.set(f"Detection error: {e}")

    def _enable_power_mode(self):
        """Attempt to install CUDA packages and switch to Power Mode."""
        from tkinter import messagebox
        self._perf_status_var.set("Installing GPU support — this may take a few minutes...")
        self.update_idletasks()
        try:
            from hardware import detect_gpu, try_install_cuda_packages
            status = detect_gpu()
            if status == "cuda_ready":
                self.config_data["compute_type"] = "float16"
                self.config_data["model_size"] = "large-v3-turbo"
                save_config(self.config_data)
                self._perf_status_var.set("Power Mode enabled! Restart Koda to apply.")
                messagebox.showinfo("Koda", "Power Mode enabled!\n\nRestart Koda to use your GPU.")
            elif status == "nvidia_no_cuda":
                success = try_install_cuda_packages()
                if success:
                    self.config_data["compute_type"] = "float16"
                    self.config_data["model_size"] = "large-v3-turbo"
                    save_config(self.config_data)
                    self._perf_status_var.set("Power Mode enabled! Restart Koda to apply.")
                    messagebox.showinfo("Koda", "Power Mode enabled!\n\nRestart Koda to use your GPU.")
                else:
                    self._perf_status_var.set("Automatic setup failed. See 'Learn more' for manual steps.")
                    messagebox.showwarning(
                        "Koda",
                        "Automatic GPU setup didn't work on this system.\n\n"
                        "Click 'Learn more' to download the NVIDIA CUDA Toolkit manually.\n"
                        "After installing it, come back here and click 'Enable Power Mode' again."
                    )
            else:
                self._perf_status_var.set("No NVIDIA GPU found — Power Mode is not available on this machine.")
        except Exception as e:
            self._perf_status_var.set(f"Error: {e}")

    def _disable_power_mode(self):
        """Switch back to Standard Mode (CPU)."""
        self.config_data["compute_type"] = "int8"
        self.config_data["model_size"] = "small"
        save_config(self.config_data)
        self._perf_status_var.set("Switched to Standard Mode. Restart Koda to apply.")

    def _open_cuda_url(self):
        """Open the NVIDIA CUDA download page in the browser."""
        import webbrowser
        webbrowser.open("https://developer.nvidia.com/cuda-downloads")

    def on_close(self):
        self.destroy()


if __name__ == "__main__":
    app = KodaSettings()
    app.mainloop()
