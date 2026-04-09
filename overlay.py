"""
Koda Floating Status Overlay — always-on-top mini widget.

Shows recording state, live streaming preview, and transcription status.
Draggable, semi-transparent pill with rounded corners. Toggleable from tray menu.

Uses Windows -transparentcolor trick: the root window has a "key" background color
that's made invisible, and a Canvas draws the actual rounded pill shape on top.
This gives true rounded corners on Windows.
"""

import tkinter as tk
import threading
import time


# Transparent key color — must not appear anywhere in the actual UI
_KEY_COLOR = "#010101"


class KodaOverlay:
    """Floating status pill that shows Koda's current state."""

    COLORS = {
        "ready": "#2ecc71",
        "recording": "#e74c3c",
        "transcribing": "#f39c12",
        "reading": "#9b59b6",
        "listening": "#3498db",
    }

    def __init__(self):
        self._root = None
        self._canvas = None
        self._label_id = None
        self._dot_id = None
        self._preview_id = None
        self._bg_id = None
        self._state = "ready"
        self._preview_text = ""
        self._visible = True
        self._drag_data = {"x": 0, "y": 0}
        self._thread = None
        self._running = False
        self._opacity = 0.75
        self._position = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass

    def _run(self):
        self._root = tk.Tk()
        root = self._root

        W, H = 260, 42
        RADIUS = 21  # Half of height = perfect pill

        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", self._opacity)
        root.attributes("-toolwindow", True)
        # Make the key color fully transparent → shaped window
        root.configure(bg=_KEY_COLOR)
        root.attributes("-transparentcolor", _KEY_COLOR)

        # Canvas fills the window — we draw the pill shape on it
        self._canvas = tk.Canvas(root, width=W, height=H, bg=_KEY_COLOR,
                                 highlightthickness=0, bd=0)
        self._canvas.pack()

        # Draw rounded pill background
        BG = "#1e1e2e"
        self._bg_id = self._rounded_rect(0, 0, W, H, RADIUS, fill=BG, outline="#313244", width=1)

        # Status dot
        DOT_X, DOT_Y, DOT_R = 18, H // 2, 5
        self._dot_id = self._canvas.create_oval(
            DOT_X - DOT_R, DOT_Y - DOT_R, DOT_X + DOT_R, DOT_Y + DOT_R,
            fill="#2ecc71", outline="",
        )

        # Label
        self._label_id = self._canvas.create_text(
            32, H // 2, text="Koda — Ready", anchor="w",
            fill="#cdd6f4", font=("Segoe UI Semibold", 10),
        )

        # Preview (hidden initially, shown below pill when recording)
        self._preview_id = None
        self._W = W
        self._H = H
        self._RADIUS = RADIUS

        # Position: bottom-right, above taskbar
        root.update_idletasks()
        if self._position:
            x, y = self._position
        else:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            x = screen_w - W - 30
            y = screen_h - 160
        root.geometry(f"{W}x{H}+{x}+{y}")

        # Drag
        self._canvas.bind("<Button-1>", self._on_drag_start)
        self._canvas.bind("<B1-Motion>", self._on_drag_motion)
        self._canvas.bind("<Button-3>", lambda e: self.toggle_visible())

        self._poll()

        try:
            root.mainloop()
        except Exception:
            pass

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """Draw a rounded rectangle on the canvas."""
        c = self._canvas
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return c.create_polygon(points, smooth=True, **kwargs)

    def _poll(self):
        if not self._running or not self._root:
            return
        try:
            self._apply_state()
            self._root.after(200, self._poll)
        except Exception:
            pass

    def _apply_state(self):
        color = self.COLORS.get(self._state, "#2ecc71")
        labels = {
            "ready": "Koda — Ready",
            "recording": "Recording...",
            "transcribing": "Transcribing...",
            "reading": "Reading aloud...",
            "listening": "Listening...",
        }

        self._canvas.itemconfig(self._dot_id, fill=color)
        self._canvas.itemconfig(self._label_id, text=labels.get(self._state, "Koda"))

        # Resize window for preview text during recording
        if self._preview_text and self._state in ("recording", "transcribing"):
            preview = self._preview_text
            if len(preview) > 80:
                preview = "..." + preview[-77:]

            if self._preview_id:
                self._canvas.itemconfig(self._preview_id, text=preview)
            else:
                # Expand pill
                new_h = 62
                self._canvas.delete(self._bg_id)
                self._bg_id = self._rounded_rect(0, 0, self._W, new_h, self._RADIUS,
                                                  fill="#1e1e2e", outline="#313244", width=1)
                self._canvas.tag_lower(self._bg_id)
                self._preview_id = self._canvas.create_text(
                    32, 42, text=preview, anchor="w",
                    fill="#a6adc8", font=("Segoe UI", 8),
                )
                self._root.geometry(f"{self._W}x{new_h}")
        else:
            if self._preview_id:
                self._canvas.delete(self._preview_id)
                self._preview_id = None
                # Shrink pill back
                self._canvas.delete(self._bg_id)
                self._bg_id = self._rounded_rect(0, 0, self._W, self._H, self._RADIUS,
                                                  fill="#1e1e2e", outline="#313244", width=1)
                self._canvas.tag_lower(self._bg_id)
                self._root.geometry(f"{self._W}x{self._H}")

        # Slightly dimmer when idle
        if self._state == "ready":
            self._root.attributes("-alpha", self._opacity * 0.85)
        else:
            self._root.attributes("-alpha", min(1.0, self._opacity * 1.1))

    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x_root - self._root.winfo_x()
        self._drag_data["y"] = event.y_root - self._root.winfo_y()

    def _on_drag_motion(self, event):
        x = event.x_root - self._drag_data["x"]
        y = event.y_root - self._drag_data["y"]
        self._root.geometry(f"+{x}+{y}")
        self._position = (x, y)

    # --- Public API ---

    def set_state(self, state, preview=""):
        self._state = state
        self._preview_text = preview

    def set_preview(self, text):
        self._preview_text = text

    def toggle_visible(self):
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
        if self._root and not self._visible:
            try:
                self._root.deiconify()
                self._visible = True
            except Exception:
                pass

    def hide(self):
        if self._root and self._visible:
            try:
                self._root.withdraw()
                self._visible = False
            except Exception:
                pass

    @property
    def is_visible(self):
        return self._visible
