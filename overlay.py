"""
Koda Floating Status Overlay — always-on-top mini widget.

Shows recording state, live streaming preview, and transcription status.
Draggable, semi-transparent, unobtrusive. Toggleable from tray menu.
"""

import tkinter as tk
import threading
import time


class KodaOverlay:
    """Floating status pill that shows Koda's current state."""

    # State colors
    COLORS = {
        "ready": "#2ecc71",       # Green
        "recording": "#e74c3c",   # Red
        "transcribing": "#f39c12", # Orange
        "reading": "#9b59b6",     # Purple
        "listening": "#3498db",   # Blue (wake word)
    }

    def __init__(self):
        self._root = None
        self._label = None
        self._preview_label = None
        self._state = "ready"
        self._preview_text = ""
        self._visible = True
        self._drag_data = {"x": 0, "y": 0}
        self._thread = None
        self._running = False
        self._opacity = 0.85
        self._position = None  # (x, y) — remembers last drag position

    def start(self):
        """Launch the overlay in its own thread (tkinter needs its own mainloop)."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Shut down the overlay."""
        self._running = False
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass

    def _run(self):
        """Tkinter mainloop — runs in its own thread."""
        self._root = tk.Tk()
        root = self._root

        # Frameless, always-on-top, transparent background
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", self._opacity)
        root.configure(bg="#1e1e2e")

        # Remove from taskbar
        root.attributes("-toolwindow", True)

        # Main frame with rounded-corner look
        frame = tk.Frame(root, bg="#1e1e2e", padx=12, pady=6)
        frame.pack(fill="both", expand=True)

        # Status indicator + text on one line
        top_row = tk.Frame(frame, bg="#1e1e2e")
        top_row.pack(fill="x")

        self._dot = tk.Canvas(top_row, width=12, height=12, bg="#1e1e2e",
                              highlightthickness=0)
        self._dot.pack(side="left", padx=(0, 6))
        self._dot_item = self._dot.create_oval(2, 2, 10, 10, fill="#2ecc71", outline="")

        self._label = tk.Label(top_row, text="Koda — Ready",
                               bg="#1e1e2e", fg="#cdd6f4",
                               font=("Segoe UI", 9), anchor="w")
        self._label.pack(side="left", fill="x", expand=True)

        # Preview text (shown during recording/transcribing)
        self._preview_label = tk.Label(frame, text="",
                                       bg="#1e1e2e", fg="#a6adc8",
                                       font=("Segoe UI", 8), anchor="w",
                                       wraplength=280, justify="left")
        self._preview_label.pack(fill="x", pady=(2, 0))
        self._preview_label.pack_forget()  # Hidden initially

        # Position: bottom-right of screen, above taskbar
        root.update_idletasks()
        if self._position:
            x, y = self._position
        else:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            w = 300
            x = screen_w - w - 20
            y = screen_h - 80
        root.geometry(f"+{x}+{y}")
        root.minsize(200, 0)

        # Drag bindings
        for widget in (root, frame, top_row, self._label, self._dot):
            widget.bind("<Button-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)

        # Right-click to hide
        for widget in (root, frame, top_row, self._label, self._dot):
            widget.bind("<Button-3>", lambda e: self.toggle_visible())

        # Start update loop
        self._poll()

        try:
            root.mainloop()
        except Exception:
            pass

    def _poll(self):
        """Periodic UI update from the tkinter thread."""
        if not self._running or not self._root:
            return
        try:
            self._apply_state()
            self._root.after(200, self._poll)
        except Exception:
            pass

    def _apply_state(self):
        """Update the visual state of the overlay."""
        color = self.COLORS.get(self._state, "#2ecc71")
        labels = {
            "ready": "Koda — Ready",
            "recording": "Koda — Recording...",
            "transcribing": "Koda — Transcribing...",
            "reading": "Koda — Reading aloud...",
            "listening": "Koda — Listening...",
        }

        self._dot.itemconfig(self._dot_item, fill=color)
        self._label.config(text=labels.get(self._state, "Koda"))

        if self._preview_text and self._state in ("recording", "transcribing"):
            preview = self._preview_text
            if len(preview) > 120:
                preview = "..." + preview[-117:]
            self._preview_label.config(text=preview)
            self._preview_label.pack(fill="x", pady=(2, 0))
        else:
            self._preview_label.pack_forget()

        # Pulse effect: slightly lower opacity when ready (more subtle)
        if self._state == "ready":
            self._root.attributes("-alpha", self._opacity * 0.7)
        else:
            self._root.attributes("-alpha", self._opacity)

    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x_root - self._root.winfo_x()
        self._drag_data["y"] = event.y_root - self._root.winfo_y()

    def _on_drag_motion(self, event):
        x = event.x_root - self._drag_data["x"]
        y = event.y_root - self._drag_data["y"]
        self._root.geometry(f"+{x}+{y}")
        self._position = (x, y)

    # --- Public API (thread-safe, called from voice.py) ---

    def set_state(self, state, preview=""):
        """Update overlay state. Safe to call from any thread.

        Args:
            state: One of 'ready', 'recording', 'transcribing', 'reading', 'listening'
            preview: Optional preview text to show
        """
        self._state = state
        self._preview_text = preview

    def set_preview(self, text):
        """Update just the preview text without changing state."""
        self._preview_text = text

    def toggle_visible(self):
        """Toggle overlay visibility."""
        if not self._root:
            return
        try:
            if self._visible:
                self._root.withdraw()
                self._visible = False
            else:
                self._root.deiconify()
                self._visible = True
        except Exception:
            pass

    def show(self):
        """Show the overlay."""
        if self._root and not self._visible:
            try:
                self._root.deiconify()
                self._visible = True
            except Exception:
                pass

    def hide(self):
        """Hide the overlay."""
        if self._root and self._visible:
            try:
                self._root.withdraw()
                self._visible = False
            except Exception:
                pass

    @property
    def is_visible(self):
        return self._visible
