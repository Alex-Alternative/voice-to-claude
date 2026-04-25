"""
Koda Floating Status Overlay — branded K icon floating on desktop.

Same branded icon as the tray (dark square, white K, colored dot),
displayed as a draggable floating widget. Right-click to hide.

Also hosts show_prompt_preview() — the larger window the prompt-assist v2
flow uses to confirm an assembled prompt before paste.
"""

import ctypes
import ctypes.wintypes
import logging
import os
import tkinter as tk
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageTk
import threading

logger = logging.getLogger("koda")


def _is_on_screen(x, y, size):
    """Return True if the centre of the overlay at (x, y) falls on any connected monitor."""
    pt = ctypes.wintypes.POINT(x + size // 2, y + size // 2)
    # MONITOR_DEFAULTTONULL returns NULL when the point is off all monitors
    return ctypes.windll.user32.MonitorFromPoint(pt, 0) != 0


def _default_position(size):
    """Return (x, y) for bottom-right of the primary monitor work area (excludes taskbar)."""
    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                    ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
    work = RECT()
    # SPI_GETWORKAREA = 0x0030
    ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(work), 0)
    x = work.right - size - 20
    y = work.bottom - size - 20
    return x, y


class KodaOverlay:
    """Floating branded K icon with status dot."""

    COLORS = {
        "ready": "#2ecc71",
        "recording": "#e74c3c",
        "transcribing": "#f39c12",
        "reading": "#9b59b6",
        "listening": "#3498db",
    }

    def __init__(self):
        self._root = None
        self._label = None
        self._state = "ready"
        self._preview_text = ""
        self._visible = True
        self._drag_data = {"x": 0, "y": 0}
        self._thread = None
        self._running = False
        self._position = None
        self._photo = None  # Keep reference to prevent GC
        self._prev_state = None
        self._icon_size = 48

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

        SIZE = self._icon_size

        KEY = "#010101"  # Transparent key color
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-toolwindow", True)
        root.attributes("-alpha", 0.85)
        root.configure(bg=KEY)
        root.attributes("-transparentcolor", KEY)

        # Label with transparent bg so rounded corners show through
        self._label = tk.Label(root, bg=KEY, bd=0, highlightthickness=0)
        self._label.pack()

        # Render initial icon
        self._update_icon()

        # Position bottom-right of primary monitor work area (excludes taskbar)
        root.update_idletasks()
        if self._position and _is_on_screen(*self._position, SIZE):
            x, y = self._position
        else:
            x, y = _default_position(SIZE)
        root.geometry(f"{SIZE}x{SIZE}+{x}+{y}")

        # Drag and hide
        root.bind("<Button-1>", self._on_drag_start)
        root.bind("<B1-Motion>", self._on_drag_motion)
        root.bind("<Button-3>", lambda e: self.toggle_visible())
        self._label.bind("<Button-1>", self._on_drag_start)
        self._label.bind("<B1-Motion>", self._on_drag_motion)
        self._label.bind("<Button-3>", lambda e: self.toggle_visible())

        self._poll()

        try:
            root.mainloop()
        except Exception:
            pass

    def _update_icon(self):
        """Re-render the branded icon with current state dot."""
        from voice import create_branded_icon
        dot_color = self.COLORS.get(self._state, "#2ecc71")
        img = create_branded_icon(self._icon_size, dot_color=dot_color)
        self._photo = ImageTk.PhotoImage(img)
        self._label.config(image=self._photo)

    def _poll(self):
        if not self._running or not self._root:
            return
        try:
            if self._state != self._prev_state:
                self._update_icon()
                self._prev_state = self._state
            self._root.after(300, self._poll)
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


# ============================================================
# Prompt-assist v2 — confirmation preview window
# ============================================================

def _lighten(hex_color, amount=0.15):
    """Lighten a hex color like '#3498db' toward white by amount (0..1).
    Used for button hover states — small lift on top of the accent color."""
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


def _hex_rgba(hex_color, alpha=255):
    """Convert '#rrggbb' (or '#rgb') to (r, g, b, a) for PIL fills."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def _rounded_rect_image(width, height, radius, fill_rgba):
    """PIL RGBA image of a filled rounded rectangle, anti-aliased corners."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=fill_rgba)
    return img


class _Tooltip:
    """Hover tooltip for any tk widget. tk has no native tooltip; this is the
    standard pattern — Toplevel with overrideredirect, topmost, shown after a
    short delay on <Enter>, hidden on <Leave>/<ButtonPress>. Multiline text
    via wraplength + justify=left.
    """

    def __init__(
        self,
        widget,
        text,
        delay_ms=400,
        bg="#16191f",
        fg="#e6e8ec",
        outline="#242932",
        font=("Segoe UI", 9),
        wrap_px=320,
    ):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.bg = bg
        self.fg = fg
        self.outline = outline
        self.font = font
        self.wrap_px = wrap_px
        self._tip = None
        self._after_id = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _e=None):
        self._cancel_pending()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel_pending(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        if self._tip is not None:
            return
        try:
            tip = tk.Toplevel(self.widget)
            tip.wm_overrideredirect(True)
            tip.attributes("-topmost", True)
            tip.configure(bg=self.outline)  # 1px outline via padx/pady on inner Label
            inner = tk.Label(
                tip, text=self.text, bg=self.bg, fg=self.fg,
                font=self.font, padx=12, pady=8,
                bd=0, highlightthickness=0,
                justify="left", wraplength=self.wrap_px,
            )
            inner.pack(padx=1, pady=1)  # gap reveals outline as border
            tip.update_idletasks()
            tip_w = tip.winfo_width()
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2 - tip_w // 2
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
            tip.geometry(f"+{x}+{y}")
            self._tip = tip
        except Exception as e:
            logger.debug("tooltip show failed: %s", e)
            self._tip = None

    def _hide(self, _e=None):
        self._cancel_pending()
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


def show_prompt_preview(text, callbacks):
    """Open a topmost preview window showing the assembled prompt + 4 actions.

    Args:
        text: assembled prompt to display.
        callbacks: dict with keys 'on_confirm', 'on_refine', 'on_add',
                   'on_cancel'. Exactly one fires; the window then closes.

    Spawns its own thread + Tk root. Returns immediately.
    """
    def _run():
        decided = {"v": False}
        root_holder = {"r": None}

        def _fire(key, *args):
            if decided["v"]:
                return
            decided["v"] = True
            try:
                cb = callbacks.get(key)
                if cb:
                    cb(*args)
            except Exception as e:
                logger.error("prompt_preview callback %s failed: %s", key, e, exc_info=True)
            try:
                if root_holder["r"]:
                    root_holder["r"].destroy()
            except Exception:
                pass

        root = tk.Tk()
        root_holder["r"] = root
        root.title("Koda — Prompt Preview")
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "koda.ico")
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except Exception:
            pass
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.0)  # fade in on show

        # -------------------------------------------------------------
        # Koda Atlas Navy — premium "blues + whites" aesthetic. Deep
        # midnight charcoal-blue surfaces + cool premium white text +
        # ONE bold premium navy accent (Maersk / IBM / Pan-Am blue,
        # NOT Tailwind blue-500). Refined business-class feel.
        # -------------------------------------------------------------
        BG_BASE     = "#0e1419"   # deep midnight charcoal-blue
        BG_SURFACE  = "#161d24"   # raised card (body)
        BG_ELEVATED = "#1f2832"   # hover / interactive surface
        BG_FLOAT    = "#293340"   # floating elements (tooltip, popovers)
        HAIRLINE    = "#293340"   # 1px separators
        TEXT        = "#eef2f7"   # cool premium white (no halation)
        TEXT_DIM    = "#9aa5b8"   # cool steel
        TEXT_MUTED  = "#5a6478"
        BRAND       = "#1c5fb8"   # premium navy — Maersk/IBM/Pan-Am blue, NOT Tailwind
        BRAND_DIM   = "#13417f"   # darker navy for low-emphasis cues
        # Single-accent philosophy: no separate INFO / WARN / DANGER colors.
        # Differentiation comes from text weight + bg contrast + position,
        # not from a full traffic-light palette.
        INFO   = TEXT_DIM
        WARN   = BRAND
        DANGER = TEXT_DIM

        # Intent-pill color map — single-accent treatment. CODE (most common
        # in dev/AI use) gets the brand. Other intents recede to TEXT_DIM —
        # the label text differentiates them, not multiple accent colors.
        INTENT_COLORS = {
            "code":    BRAND,
            "debug":   TEXT_DIM,
            "explain": TEXT_DIM,
            "review":  TEXT_DIM,
            "write":   TEXT_DIM,
            "general": TEXT_MUTED,
        }

        root.configure(bg=BG_BASE)
        W, H = 760, 580
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")

        # Pick the best available font family on this system. Hubot Sans /
        # JetBrains Mono are the design targets; fall back to what's already
        # installed (Segoe UI Variable on Win 11, Cascadia Mono with Terminal,
        # then perennial fallbacks). Avoids bundling fontfiles for now.
        _installed = set(tkfont.families())
        def _pick(*candidates):
            for c in candidates:
                if c in _installed:
                    return c
            return candidates[-1]
        FONT_DISPLAY = _pick("Hubot Sans", "Segoe UI Variable Display", "Segoe UI")
        FONT_BODY    = _pick("Segoe UI Variable Text", "Segoe UI")
        FONT_MONO    = _pick("JetBrains Mono", "Cascadia Mono", "Consolas")

        # =============== LEFT-EDGE ACCENT BAR ===============
        # Ableton-style — a thin orange spine that runs the full modal height.
        # Visual signature; instantly recognizable as Koda across screenshots.
        left_bar = tk.Frame(root, bg=BRAND, width=5)
        left_bar.pack(side="left", fill="y")

        # All other content packs into `outer` (right of the accent bar).
        outer = tk.Frame(root, bg=BG_BASE)
        outer.pack(side="left", fill="both", expand=True)

        # =============== FOOTER (hints) — packed bottom first ===============
        footer = tk.Frame(outer, bg=BG_BASE)
        footer.pack(side="bottom", fill="x", padx=28, pady=(0, 14))
        tk.Label(
            footer, text="⏎  Paste       Esc  Cancel",
            bg=BG_BASE, fg=TEXT_MUTED, font=(FONT_BODY, 9),
        ).pack(side="right")

        # Hairline above footer (between buttons and hints)
        tk.Frame(outer, bg=HAIRLINE, height=1).pack(
            side="bottom", fill="x", padx=28, pady=(12, 10),
        )

        # =============== BUTTON ROW ===============
        btn_row = tk.Frame(outer, bg=BG_BASE)
        btn_row.pack(side="bottom", fill="x", padx=28)

        add_holder = {"frame": None}

        # =============== HEADER (brand lockup + intent pill) ===============
        header = tk.Frame(outer, bg=BG_BASE)
        header.pack(side="top", fill="x", padx=28, pady=(22, 14))

        # Koda K mark at 40px. Dot color is the OPERATIONAL state (ready=green),
        # not the BRAND accent. They're separate concerns — like Ableton having
        # orange branding but distinct clip-state colors. KodaOverlay.COLORS
        # holds the canonical state map; "ready" = #2ecc71 here matches that.
        STATUS_READY_DOT = "#2ecc71"
        try:
            from voice import create_branded_icon
            mark_img = create_branded_icon(40, dot_color=STATUS_READY_DOT)
            mark_photo = ImageTk.PhotoImage(mark_img)
            mark_label = tk.Label(header, image=mark_photo, bg=BG_BASE, bd=0)
            mark_label.image = mark_photo  # prevent GC
            mark_label.pack(side="left", padx=(0, 14))
        except Exception as e:
            logger.debug("brand mark render failed: %s", e)

        title_col = tk.Frame(header, bg=BG_BASE)
        title_col.pack(side="left", fill="y")
        tk.Label(
            title_col, text="Koda", bg=BG_BASE, fg=TEXT,
            font=(FONT_DISPLAY, 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_col, text="Prompt Preview  ·  Review before paste",
            bg=BG_BASE, fg=TEXT_DIM, font=(FONT_BODY, 10),
        ).pack(anchor="w", pady=(2, 0))

        # Intent pill — right side, color per detected intent. Tooltip on hover
        # explains it (the pill is informational, not actionable — clicking it
        # does nothing; you'd refine or re-speak to change the detected intent).
        try:
            from prompt_assist import detect_intent
            intent = detect_intent(text or "")
            pill_color = INTENT_COLORS.get(intent, TEXT_MUTED)
            pill = tk.Label(
                header, text=f"  {intent.upper()}  ",
                bg=BG_ELEVATED, fg=pill_color,
                font=(FONT_DISPLAY, 9, "bold"),
                padx=12, pady=6,
                cursor="question_arrow",
            )
            pill.pack(side="right", pady=(8, 0))
            _Tooltip(
                pill,
                text=(
                    f"Koda detected your speech as a {intent.upper()} request and "
                    f"used the {intent} prompt template. Click Polish to AI-rewrite, "
                    f"or Cancel to start over."
                ),
                bg=BG_FLOAT, fg=TEXT, outline=HAIRLINE, font=(FONT_BODY, 9),
            )
        except Exception as e:
            logger.debug("intent pill render failed: %s", e)

        # Hairline under header
        tk.Frame(outer, bg=HAIRLINE, height=1).pack(side="top", fill="x", padx=28)

        # =============== BODY (prompt card) ===============
        body_wrap = tk.Frame(outer, bg=BG_BASE)
        body_wrap.pack(side="top", fill="both", expand=True, padx=28, pady=18)

        body = tk.Frame(body_wrap, bg=BG_SURFACE)
        body.pack(fill="both", expand=True)

        # 1px top-edge highlight — faked depth (lighter line = raised card feel)
        tk.Frame(body, bg=BG_ELEVATED, height=1).pack(side="top", fill="x")

        # Prompt body uses monospace — signals "for technical/voice users",
        # distinct from chat-app body text. Slight size decrease since mono
        # characters are wider per glyph.
        txt = tk.Text(
            body, wrap="word", bg=BG_SURFACE, fg=TEXT, bd=0,
            highlightthickness=0, font=(FONT_MONO, 11),
            padx=24, pady=22, insertbackground=TEXT,
            selectbackground=BG_ELEVATED, spacing1=4, spacing3=4,
        )
        txt.insert("1.0", text or "")
        txt.config(state="disabled")
        scroll = tk.Scrollbar(
            body, command=txt.yview, bg=BG_SURFACE,
            troughcolor=BG_SURFACE, bd=0, highlightthickness=0,
            activebackground=BG_ELEVATED, width=10,
        )
        txt.config(yscrollcommand=scroll.set)
        txt.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # =============== BUTTON FACTORIES ===============
        # Three hierarchies — text (ghost), elevated (secondary prominent),
        # primary (solid CTA). All use PIL-rendered rounded-rect background
        # images for true rounded corners (tk widgets don't natively support
        # border-radius). Differentiation by weight + bg contrast.
        _font_primary = tkfont.Font(family=FONT_BODY, size=11, weight="bold")
        _font_secondary = tkfont.Font(family=FONT_BODY, size=10, weight="bold")
        _btn_image_refs = []  # hold PhotoImage refs so they aren't GC'd while window is alive

        def _btn_images(w, h, radius, normal_hex, hover_hex):
            """Return (normal_photo, hover_photo). normal_hex=None → fully transparent normal state."""
            if normal_hex is None:
                normal_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            else:
                normal_img = _rounded_rect_image(w, h, radius, _hex_rgba(normal_hex))
            hover_img = _rounded_rect_image(w, h, radius, _hex_rgba(hover_hex))
            n_photo = ImageTk.PhotoImage(normal_img)
            h_photo = ImageTk.PhotoImage(hover_img)
            _btn_image_refs.extend([n_photo, h_photo])
            return n_photo, h_photo

        def _measure(font, label, padx, pady):
            return font.measure(label) + 2 * padx, font.metrics("linespace") + 2 * pady

        BTN_RADIUS = 8

        def _make_text_btn(parent, label, color, action):
            w, h = _measure(_font_secondary, label, padx=14, pady=9)
            n_photo, h_photo = _btn_images(w, h, BTN_RADIUS, None, BG_ELEVATED)
            btn = tk.Label(
                parent, image=n_photo, text=label, compound="center",
                bg=BG_BASE, fg=color, font=_font_secondary,
                bd=0, highlightthickness=0, cursor="hand2",
            )
            btn.bind("<Button-1>", lambda e: action())
            btn.bind("<Enter>", lambda e: btn.configure(image=h_photo, fg=_lighten(color, 0.2)))
            btn.bind("<Leave>", lambda e: btn.configure(image=n_photo, fg=color))
            return btn

        def _make_elevated_btn(parent, label, color, action):
            w, h = _measure(_font_secondary, label, padx=20, pady=10)
            n_photo, h_photo = _btn_images(w, h, BTN_RADIUS, BG_ELEVATED, _lighten(BG_ELEVATED, 0.35))
            btn = tk.Label(
                parent, image=n_photo, text=label, compound="center",
                bg=BG_BASE, fg=color, font=_font_secondary,
                bd=0, highlightthickness=0, cursor="hand2",
            )
            btn.bind("<Button-1>", lambda e: action())
            btn.bind("<Enter>", lambda e: btn.configure(image=h_photo))
            btn.bind("<Leave>", lambda e: btn.configure(image=n_photo))
            return btn

        def _make_primary_btn(parent, label, action):
            w, h = _measure(_font_primary, label, padx=26, pady=11)
            n_photo, h_photo = _btn_images(w, h, BTN_RADIUS, BRAND, _lighten(BRAND, 0.12))
            btn = tk.Label(
                parent, image=n_photo, text=label, compound="center",
                bg=BG_BASE, fg=BG_BASE, font=_font_primary,
                bd=0, highlightthickness=0, cursor="hand2",
            )
            btn.bind("<Button-1>", lambda e: action())
            btn.bind("<Enter>", lambda e: btn.configure(image=h_photo))
            btn.bind("<Leave>", lambda e: btn.configure(image=n_photo))
            return btn

        # =============== ADD-INLINE ===============
        def _show_add_inline():
            if add_holder["frame"]:
                return
            af = tk.Frame(outer, bg=BG_BASE)
            af.pack(side="bottom", fill="x", padx=28, pady=(0, 10), before=btn_row)
            tk.Label(af, text="Append:", bg=BG_BASE, fg=TEXT_DIM,
                     font=(FONT_BODY, 10)).pack(side="left", padx=(0, 10))
            entry = tk.Entry(
                af, bg=BG_SURFACE, fg=TEXT, insertbackground=TEXT, bd=0,
                font=(FONT_BODY, 12), relief="flat",
                highlightbackground=HAIRLINE, highlightcolor=BRAND,
                highlightthickness=1,
            )
            entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
            entry.focus_set()
            def _confirm_add(_=None):
                _fire("on_add", entry.get().strip())
            entry.bind("<Return>", _confirm_add)
            entry.bind("<Escape>", lambda e: _fire("on_cancel"))
            _make_primary_btn(af, "OK", _confirm_add).pack(side="left")
            add_holder["frame"] = af

        # =============== BUTTON LAYOUT ===============
        # Left: ghost destructive + ghost secondary.
        # Right: elevated secondary + solid primary (modern OS convention).
        # Each button gets a hover tooltip so first-time users understand what
        # the action does without having to click and discover. Internal
        # callback names (on_refine etc.) stay — only the user-facing label
        # for "Refine" was renamed to "Polish" (clearer for newbies).
        cancel_btn = _make_text_btn(btn_row, "Cancel", DANGER, lambda: _fire("on_cancel"))
        cancel_btn.pack(side="left")
        _Tooltip(cancel_btn, "Discard this prompt and close. Esc works too.",
                 bg=BG_FLOAT, fg=TEXT, outline=HAIRLINE, font=(FONT_BODY, 9))

        add_btn = _make_text_btn(btn_row, "＋  Add", WARN, _show_add_inline)
        add_btn.pack(side="left", padx=(2, 0))
        _Tooltip(add_btn, "Append more text to this prompt before pasting.",
                 bg=BG_FLOAT, fg=TEXT, outline=HAIRLINE, font=(FONT_BODY, 9))

        paste_btn = _make_primary_btn(btn_row, "Paste", lambda: _fire("on_confirm"))
        paste_btn.pack(side="right")
        _Tooltip(paste_btn, "Insert this prompt into the active window. Enter works too.",
                 bg=BG_FLOAT, fg=TEXT, outline=HAIRLINE, font=(FONT_BODY, 9))

        polish_btn = _make_elevated_btn(btn_row, "Polish", INFO, lambda: _fire("on_refine"))
        polish_btn.pack(side="right", padx=(0, 10))
        _Tooltip(polish_btn,
                 "Rewrite this prompt with AI for clarity. "
                 "Uses your configured backend (Ollama, API, or template-only).",
                 bg=BG_FLOAT, fg=TEXT, outline=HAIRLINE, font=(FONT_BODY, 9))

        # =============== BINDINGS ===============
        root.bind("<Escape>", lambda e: _fire("on_cancel"))
        root.bind("<Return>", lambda e: _fire("on_confirm"))
        root.protocol("WM_DELETE_WINDOW", lambda: _fire("on_cancel"))

        root.lift()
        try:
            root.focus_force()
        except Exception:
            pass

        # Fade in over ~150ms — softens modal appearance, no animation feels abrupt
        def _fade(alpha=0.0):
            alpha = min(1.0, alpha + 0.12)
            try:
                root.attributes("-alpha", alpha)
            except Exception:
                return
            if alpha < 1.0:
                root.after(15, _fade, alpha)
        _fade()

        try:
            root.mainloop()
        except Exception as e:
            logger.error("prompt_preview mainloop crashed: %s", e, exc_info=True)
        finally:
            if not decided["v"]:
                try:
                    cb = callbacks.get("on_cancel")
                    if cb:
                        cb()
                except Exception:
                    pass

    threading.Thread(target=_run, daemon=True).start()
