"""
Koda Floating Status Overlay — minimal mic icon with status dot.

Small, unobtrusive widget in the corner. Mic icon with a colored dot
that changes by state. Draggable, semi-transparent.
"""

import tkinter as tk
import threading
import time

_KEY_COLOR = "#010101"


class KodaOverlay:
    """Minimal mic + dot overlay."""

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
        self._state = "ready"
        self._preview_text = ""
        self._visible = True
        self._drag_data = {"x": 0, "y": 0}
        self._thread = None
        self._running = False
        self._opacity = 0.9
        self._position = None
        self._dot_id = None
        self._pulse = False

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

        SIZE = 40

        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", self._opacity)
        root.attributes("-toolwindow", True)
        root.configure(bg=_KEY_COLOR)
        root.attributes("-transparentcolor", _KEY_COLOR)

        self._canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg=_KEY_COLOR,
                                 highlightthickness=0, bd=0)
        self._canvas.pack()

        self._SIZE = SIZE
        cx, cy = SIZE // 2, SIZE // 2

        # Draw mic icon (static, white/light gray)
        MIC_COLOR = "#cdd6f4"

        # Mic body (rounded rectangle via oval approximation)
        self._canvas.create_oval(cx - 5, cy - 12, cx + 5, cy + 2, fill=MIC_COLOR, outline="")

        # Mic cradle arc
        self._canvas.create_arc(cx - 9, cy - 6, cx + 9, cy + 10,
                                 start=0, extent=180, outline=MIC_COLOR, width=2, style="arc")

        # Mic stand
        self._canvas.create_line(cx, cy + 10, cx, cy + 14, fill=MIC_COLOR, width=2)
        self._canvas.create_line(cx - 5, cy + 14, cx + 5, cy + 14, fill=MIC_COLOR, width=2)

        # Status dot (bottom-right of mic) — this changes color
        dot_x, dot_y, dot_r = cx + 10, cy + 10, 5
        # Dot outline for visibility
        self._canvas.create_oval(dot_x - dot_r - 1, dot_y - dot_r - 1,
                                  dot_x + dot_r + 1, dot_y + dot_r + 1,
                                  fill="#1e1e2e", outline="")
        self._dot_id = self._canvas.create_oval(
            dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r,
            fill="#2ecc71", outline="",
        )

        # Position: bottom-right
        root.update_idletasks()
        if self._position:
            x, y = self._position
        else:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            x = screen_w - SIZE - 20
            y = screen_h - SIZE - 110
        root.geometry(f"{SIZE}x{SIZE}+{x}+{y}")

        self._canvas.bind("<Button-1>", self._on_drag_start)
        self._canvas.bind("<B1-Motion>", self._on_drag_motion)
        self._canvas.bind("<Button-3>", lambda e: self.toggle_visible())

        self._poll()

        try:
            root.mainloop()
        except Exception:
            pass

    def _poll(self):
        if not self._running or not self._root:
            return
        try:
            color = self.COLORS.get(self._state, "#2ecc71")

            # Pulse the dot when recording (alternate size)
            if self._state == "recording":
                self._pulse = not self._pulse
                cx, cy = self._SIZE // 2 + 10, self._SIZE // 2 + 10
                r = 6 if self._pulse else 4
                self._canvas.coords(self._dot_id, cx - r, cy - r, cx + r, cy + r)
            else:
                cx, cy = self._SIZE // 2 + 10, self._SIZE // 2 + 10
                self._canvas.coords(self._dot_id, cx - 5, cy - 5, cx + 5, cy + 5)

            self._canvas.itemconfig(self._dot_id, fill=color)

            # Full opacity always — user wants it visible
            self._root.attributes("-alpha", self._opacity)

            interval = 400 if self._state == "recording" else 300
            self._root.after(interval, self._poll)
        except Exception:
            pass

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
