#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arctic Fox GitHub Search v5.0 — GUI Edition (Kali Linux).

A fast, animated desktop GUI for inspecting GitHub accounts and repositories.
Arctic Night theme · English UI · standard library only (Tkinter).

New in v5.0 — "Frost Pro" interface:
  · real fox logo header with living aurora light strip
  · glass cards, segmented search modes, animated tab underline
  · smooth 30 fps tweens everywhere (buttons, focus glow, toasts)
  · skeleton loading, count-up stat tiles, easing spinner
  · toast notifications, hover-highlight tables, refreshed dialogs

Usage:
    python3 arcticfox_gui.py [username]
    af  [username]          (after install.sh)
    af  --cli [username]    terminal edition
"""

import base64
import io
import math
import os
import queue
import sys
import threading
import time
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ---- friendly start-up guard: never crash with a raw traceback -------------
def _gui_unavailable(reason):
    """Explain why the GUI cannot start and offer terminal mode instead."""
    bar = "─" * 58
    print(f"\n  {bar}\n")
    print("   ARCTIC FOX v5.0 — GUI cannot start\n")
    print(f"   Reason: {reason}\n")
    print("   FIX (run these commands, then try again):")
    print("     sudo apt update")
    print("     sudo apt install -y python3 python3-tk")
    print("\n   No desktop available (SSH / headless / Termux)?")
    print("     Use terminal mode instead:  python3 arcticfox-cli.py\n")
    try:
        ans = input("   Start terminal mode now? [Y/n] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        ans = "n"
    if ans in ("", "y", "yes"):
        os.execv(sys.executable,
                 [sys.executable,
                  str(Path(__file__).resolve().parent / "arcticfox-cli.py")]
                 + sys.argv[1:])
    sys.exit(1)


try:
    import tkinter as tk
    import tkinter.font as tkfont
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    # --version / --help still work without tkinter
    if any(a in ("-v", "--version", "-h", "--help") for a in sys.argv[1:]):
        if any(a in ("-v", "--version") for a in sys.argv[1:]):
            print("Arctic Fox GitHub Search 5.0 (GUI edition)")
        else:
            print(__doc__)
        sys.exit(0)
    _gui_unavailable("Tkinter (python3-tk) is not installed.")

import arcticfox_core as core  # noqa: E402


# ------------------------------------------------------------------ theme --
class C:
    """Arctic Night palette — deep, glassy, professional."""
    bg        = "#050611"   # midnight navy
    panel     = "#0B0D20"   # violet-tinted bands
    card      = "#11152B"   # elevated panels
    card2     = "#0B1022"   # inputs / alternating rows
    hover     = "#20234A"   # hover fill
    border    = "#272B55"
    border2   = "#414A8A"
    ice       = "#91A7FF"   # moonlit blue accent
    ice2      = "#C1CBFF"   # accent hover
    indigo    = "#A18BFF"   # violet secondary accent
    deep      = "#30366F"   # solid primary button
    text      = "#E9F2FC"
    muted     = "#8FA6C6"
    faint     = "#566A8E"
    ok        = "#3DDC97"
    warn      = "#F5C044"
    danger    = "#FF6B7A"
    white     = "#FFFFFF"
    selbg     = "#17405F"
    gold      = "#F5C044"


# semantic button kinds: (bg, fg, hover-bg, outline)
C.KINDS = {
    "primary": ("#1E88C7", "#FFFFFF", "#3FA6E3", "#3FA6E3"),
    "ice":     (C.ice,    C.bg,      C.ice2,    C.ice2),
    "soft":    (C.card,   C.ice,     C.hover,   C.border2),
    "ghost":   (C.panel,  C.muted,   C.hover,   C.border),
    "danger":  ("#3A1420", C.danger, "#5A1E30", "#7A2840"),
}


_FAMILIES = None


def _families():
    global _FAMILIES
    if _FAMILIES is None:
        try:
            _FAMILIES = set(tkfont.families())
        except Exception:
            _FAMILIES = set()
    return _FAMILIES


def font_of(family=None, size=10, bold=False, mono=False):
    if family is None:
        try:
            family = tkfont.nametofont("TkFixedFont" if mono else "TkDefaultFont").actual("family")
        except Exception:
            family = "TkFixedFont" if mono else "TkDefaultFont"
        prefs = (("DejaVu Sans Mono", "Liberation Mono", "Noto Sans Mono") if mono
                 else ("DejaVu Sans", "Noto Sans", "Liberation Sans"))
        for c in prefs:
            if c in _families():
                family = c
                break
    return (family, size, "bold" if bold else "normal")


# ------------------------------------------------------------ color math ---
def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(r, g, b):
    return f"#{max(0, min(255, int(r))):02x}{max(0, min(255, int(g))):02x}{max(0, min(255, int(b))):02x}"


def mix(a, b, t):
    """Blend two hex colors; t = 0 → a, t = 1 → b."""
    ar, ag, ab = _rgb(a)
    br, bg_, bb = _rgb(b)
    return _hex(ar + (br - ar) * t, ag + (bg_ - ag) * t, ab + (bb - ab) * t)


def _lighten(hexcolor, f=0.18):
    r, g, b = _rgb(hexcolor)
    return _hex(r + (255 - r) * f, g + (255 - g) * f, b + (255 - b) * f)


# ------------------------------------------------------------- easing ------
def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def ease_out_quart(t):
    return 1 - (1 - t) ** 4


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


# ------------------------------------------------------ rounded shapes -----
def rounded(canvas, x1, y1, x2, y2, r, **kw):
    """Draw a smooth rounded rectangle on a canvas; returns the item id."""
    r = max(1, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


def gradient_strip(width, height, stops, peak=None):
    """Build a PhotoImage gradient bar; optional baked brightness peak."""
    img = tk.PhotoImage(width=width, height=height)
    row = []
    for x in range(width):
        t = x / max(1, width - 1)
        j = min(int(t * (len(stops) - 1)), len(stops) - 2)
        f = t * (len(stops) - 1) - j
        r, g, b = (int(a + (c - a) * f) for a, c in
                   zip(_rgb(stops[j]), _rgb(stops[j + 1])))
        if peak is not None:
            # gaussian brightness bump at `peak` (0..1), width ~90px
            d = (x - peak * width) / 90.0
            k = math.exp(-d * d) * 0.9
            r, g, b = r + (255 - r) * k, g + (255 - g) * k, b + (255 - b) * k
        row.append(_hex(r, g, b))
    line = "{" + " ".join(row) + "}"
    for y in range(height):
        img.put(line, to=(0, y, width, y + 1))
    return img


# ----------------------------------------------------------- animations ----
class Tweens:
    """Central tween registry — one tick() call per animation frame."""

    def __init__(self):
        self._items = []

    def add(self, dur_ms, step, done=None, ease=ease_out_cubic, delay=0):
        tw = {"start": time.monotonic() + delay / 1000.0, "dur": max(1, dur_ms) / 1000.0,
              "step": step, "done": done, "ease": ease, "started": delay <= 0}
        self._items.append(tw)
        return tw

    def color(self, widget, option, c_from, c_to, dur_ms=140, ease=ease_out_cubic):
        if c_from == c_to:
            _safe_cfg(widget, option, c_to)
            return None
        return self.add(dur_ms, lambda k: _safe_cfg(widget, option, mix(c_from, c_to, k)),
                        ease=ease)

    def tick(self):
        now = time.monotonic()
        alive = []
        for tw in self._items:
            if not tw["started"]:
                if now >= tw["start"]:
                    tw["started"] = True
                    tw["start"] = now
                else:
                    alive.append(tw)
                    continue
            p = (now - tw["start"]) / tw["dur"]
            if p >= 1:
                try:
                    tw["step"](1)
                    if tw["done"]:
                        tw["done"]()
                except Exception:
                    pass
            else:
                try:
                    tw["step"](tw["ease"](p))
                    alive.append(tw)
                except Exception:
                    pass
        self._items = alive


def _safe_cfg(widget, option, value):
    try:
        widget[option] = value
    except Exception:
        pass


def _safe_item(canvas, item, **kw):
    try:
        canvas.itemconfigure(item, **kw)
    except Exception:
        pass


def _safe_coord(canvas, item, *args):
    try:
        canvas.coords(item, *args)
    except Exception:
        pass


def _safe_grab(win):
    try:
        win.grab_set()
    except Exception:
        pass


# ================================================================ widgets ==

class Btn(tk.Button):
    """Flat button with a smooth animated hover (color lerp, 130 ms)."""

    def __init__(self, master, text, command=None, kind="ghost", size=10,
                 bold=False, padx=16, app=None, width=None, **kw):
        bg, fg, hbg, outline = C.KINDS[kind]
        super().__init__(master, text=text, command=command, bg=bg, fg=fg,
                         activebackground=hbg, activeforeground=fg,
                         relief="flat", bd=0, font=font_of(size=size, bold=bold),
                         padx=padx, pady=7, cursor="hand2", takefocus=0,
                         disabledforeground=C.faint, width=width, **kw)
        self._app = app
        self._bg, self._fg, self._hbg = bg, fg, hbg
        self._enabled = True
        self.config(highlightthickness=1,
                    highlightbackground=outline, highlightcolor=outline)
        self.bind("<Enter>", self._on_enter, add="+")
        self.bind("<Leave>", self._on_leave, add="+")
        self.bind("<ButtonPress-1>", self._on_press, add="+")
        self.bind("<ButtonRelease-1>", self._on_release, add="+")

    # -- animated hover ------------------------------------------------------
    def _on_enter(self, _=None):
        if not self._enabled:
            return
        if self._app:
            self._app.tweens.color(self, "bg", self["bg"], self._hbg, 130)
        else:
            self.config(bg=self._hbg)

    def _on_leave(self, _=None):
        if self._app:
            self._app.tweens.color(self, "bg", self["bg"], self._bg, 160)
        else:
            self.config(bg=self._bg)

    def _on_press(self, _=None):
        if self._enabled:
            self.config(bg=mix(self._hbg, C.bg, 0.28))

    def _on_release(self, _=None):
        if self._enabled:
            self.config(bg=self._hbg)

    def set_enabled(self, enabled):
        self._enabled = bool(enabled)
        self.config(state="normal" if enabled else "disabled",
                    fg=self._fg if enabled else C.faint,
                    bg=self._bg if enabled else C.card2,
                    highlightbackground=C.border if enabled else C.border)


class Pill(tk.Canvas):
    """Small rounded label chip (static)."""

    def __init__(self, master, text, fg, bg=C.card, outline=C.border,
                 size=8, padx=12, pady=5, bold=True):
        f = font_of(size=size, bold=bold)
        w = int(len(text) * (size * 0.78 if not bold else size * 0.84)) + padx * 2
        h = size * 2 + pady * 2 + 4
        super().__init__(master, width=w, height=h, bg=master["bg"],
                         highlightthickness=0)
        rounded(self, 1, 1, w - 2, h - 2, h // 2, fill=bg, outline=outline)
        self.create_text(w // 2, h // 2 + 1, text=text, fill=fg, font=f)


class Header(tk.Canvas):
    """Brand header: fox logo, wordmark, status pills, aurora light strip."""

    HEIGHT = 92

    def __init__(self, master, app):
        super().__init__(master, height=self.HEIGHT, bg=C.bg, highlightthickness=0)
        self.app = app
        self.pack_propagate(False)
        self._logo_ref = None
        self._strip = None
        self._strip_x = 0
        self._halo = []
        self._token_items = []
        self._built = False
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, _=None):
        self.redraw()

    def redraw(self):
        w = max(self.winfo_width(), 900)
        self.delete("all")
        self._halo = []

        # vertical gradient wash bg→panel (drawn once per resize)
        steps = self.HEIGHT
        for y in range(steps):
            self.create_line(0, y, w, y, fill=mix(C.bg, C.panel, y / steps))

        # --- logo with soft halo -------------------------------------------
        lx, ly = 30, self.HEIGHT // 2
        logo = self.app.logo_img
        if logo is not None:
            for i, rad in enumerate((30, 26, 22)):
                self._halo.append(
                    self.create_oval(lx - rad + 21, ly - rad, lx + rad + 21, ly + rad,
                                     outline=mix(C.bg, C.ice, 0.10 + i * 0.06)))
            self._logo_ref = logo
            self.create_image(lx + 21, ly, image=logo)
        else:                                    # monogram fallback
            rounded(self, lx, ly - 21, lx + 42, ly + 21, 10,
                    fill=C.card, outline=C.border2)
            self.create_text(lx + 21, ly, text="AF", fill=C.ice,
                             font=font_of(size=15, bold=True))

        # --- wordmark -------------------------------------------------------
        tx = lx + 64
        self.create_text(tx, ly - 14, text="ARCTIC FOX", anchor="w",
                         fill=C.white, font=font_of(size=19, bold=True))
        self.create_text(tx + 2, ly + 8, anchor="w",
                         text="G I T H U B   I N S P E C T O R",
                         fill=C.muted, font=font_of(size=8, bold=True))

        # --- right-side pills ------------------------------------------------
        pw, ph = 128, 26
        px = w - 18
        self._pill(px - pw, 22, pw, ph, f"v{core.VERSION}  ·  PRO UI", C.card, C.ice)
        self._pill(px - pw, 56, pw, ph, "KALI LINUX", C.card, C.ok)
        self.app.header_token_pill = (px - pw * 2 - 8, 22, pw, ph)
        self.refresh_token_pill()

        # --- aurora light strip ---------------------------------------------
        if self._strip is None:
            self._strip = gradient_strip(w + 600, 3, (C.border2, C.indigo, C.ice,
                                                      C.ice2, C.ice, C.indigo,
                                                      C.border2),
                                         peak=0.5)
        self._aurora_items = [
            self.create_image(0, self.HEIGHT - 2, image=self._strip, anchor="nw"),
            self.create_image(w + 600, self.HEIGHT - 2, image=self._strip, anchor="nw"),
        ]
        self._strip_w = w + 600
        self._built = True
        self.step()

    def _pill(self, x, y, w, h, text, bg, fg):
        rounded(self, x, y, x + w, y + h, h // 2, fill=bg, outline=C.border)
        self.create_text(x + w // 2, y + h // 2 + 1, text=text, fill=fg,
                         font=font_of(size=8, bold=True))

    def refresh_token_pill(self):
        """Redraw only the TOKEN pill (called when settings change)."""
        for it in self._token_items:
            self.delete(it)
        self._token_items = []
        if not hasattr(self.app, "header_token_pill"):
            return
        x, y, w, h = self.app.header_token_pill
        on = bool(core.CONF["token"])
        r = rounded(self, x, y, x + w, y + h, h // 2, fill=C.card,
                    outline=C.border)
        t = self.create_text(x + w // 2, y + h // 2 + 1,
                             text="TOKEN ON" if on else "TOKEN OFF",
                             fill=C.ok if on else C.faint,
                             font=font_of(size=8, bold=True))
        self._token_items = [r, t]

    def step(self):
        """Aurora drift — two copies of the strip scroll left forever."""
        if not self._built:
            return
        self._strip_x = (self._strip_x + 1.5) % self._strip_w
        _safe_coord(self, self._aurora_items[0], -self._strip_x, self.HEIGHT - 2)
        _safe_coord(self, self._aurora_items[1],
                    -self._strip_x + self._strip_w, self.HEIGHT - 2)


class Segmented(tk.Canvas):
    """Animated segmented control (Username / Full Name / Email)."""

    PAD = 14

    def __init__(self, master, options, on_change, app, h=36, size=9):
        self.opts = list(options)
        self.app = app
        self.on_change = on_change
        self.sel = 0
        self.h = h
        self._widths = [int(len(o) * size * 0.92) + self.PAD * 2 for o in self.opts]
        total = sum(self._widths)
        super().__init__(master, width=total + 8, height=h, bg=master["bg"],
                         highlightthickness=0)
        rounded(self, 1, 1, total + 7, h - 1, (h - 2) // 2,
                fill=C.card2, outline=C.border)
        self._texts, xs = [], 5
        self._xs = []
        for wd, o in zip(self._widths, self.opts):
            self._xs.append(xs)
            self._texts.append(self.create_text(xs + wd // 2, h // 2 + 1, text=o,
                                                fill=C.muted,
                                                font=font_of(size=size, bold=True)))
            xs += wd
        self._knob = rounded(self, 5, 3, 5 + self._widths[0], h - 3, (h - 6) // 2,
                             fill=C.hover, outline="")
        self.tag_lower(self._knob)
        self._paint_sel()
        for i, x in enumerate(self._xs):
            self.tag_bind(self._texts[i], "<Button-1>",
                          lambda e, i=i: self.choose(i))

    def _paint_sel(self):
        for i, t in enumerate(self._texts):
            _safe_item(self, t, fill=C.white if i == self.sel else C.muted)

    def _knob_bounds(self, i):
        x = self._xs[i]
        return x, 3, x + self._widths[i], self.h - 3

    def choose(self, i):
        if i == self.sel:
            return
        old = self._knob_bounds(self.sel)
        self.sel = i
        new = self._knob_bounds(i)
        app = self.app
        app.tweens.add(220, lambda k: _safe_coord(
            self, self._knob,
            *(mix(a, b, k) for a, b in zip(old, new))), ease=ease_in_out)
        self._paint_sel()
        if self.on_change:
            self.on_change(self.opts[i])

    def get(self):
        return self.opts[self.sel]

    def set(self, opt):
        if opt in self.opts:
            self.choose(self.opts.index(opt))


class TabBar(tk.Canvas):
    """Custom notebook header with sliding underline and live counts."""

    def __init__(self, master, app, tabs, h=42):
        self.app = app
        self.tabs = tabs                      # list of (key, label)
        self.counts = {k: 0 for k, _ in tabs}
        self.sel = 0
        self.h = h
        self._hover = None
        super().__init__(master, height=h, bg=master["bg"], highlightthickness=0)
        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<Button-1>", self._click)
        self.bind("<Motion>", self._motion)
        self.bind("<Leave>", lambda e: self._set_hover(None))
        self._base_x = []
        self.redraw()

    def _geom(self):
        w = max(self.winfo_width(), 600)
        n = len(self.tabs)
        seg = w // n
        return w, seg

    def redraw(self):
        w, seg = self._geom()
        self.delete("all")
        self.create_line(0, self.h - 1, w, self.h - 1, fill=C.border)
        self._items = []
        for i, (key, label) in enumerate(self.tabs):
            cx = i * seg
            cnt = self.counts.get(key, 0)
            txt = label if cnt == 0 else f"{label}  ·  {cnt}"
            col = C.white if i == self.sel else (C.muted if i == self._hover else C.faint)
            t = self.create_text(cx + 22, self.h // 2, text=txt.upper(),
                                 anchor="w", fill=col,
                                 font=font_of(size=9, bold=True))
            self._items.append(t)
            self.tag_bind(t, "<Enter>", lambda e, i=i: self._set_hover(i))
            self.tag_bind(t, "<Leave>", lambda e: self._set_hover(None))
        # underline (animated by _slide)
        x0 = self.sel * seg + 14
        self._under = self.create_rectangle(x0, self.h - 2, x0 + 34, self.h,
                                             fill=C.ice, outline="")
        self._seg = seg
        self._x0 = x0

    def _set_hover(self, i):
        if i == self._hover:
            return
        self._hover = i
        for j, item in enumerate(self._items):
            if j != self.sel:
                _safe_item(self, item, fill=C.muted if j == i else C.faint)

    def _click(self, e):
        _, seg = self._geom()
        i = min(int(e.x / seg), len(self.tabs) - 1)
        self.select(i)

    def _motion(self, e):
        _, seg = self._geom()
        i = min(int(e.x / seg), len(self.tabs) - 1)
        self._set_hover(i if 0 <= e.y <= self.h else None)

    def select(self, i, animate=True):
        if i == self.sel and animate:
            return
        self.sel = i
        for j, item in enumerate(self._items):
            _safe_item(self, item, fill=C.white if j == i else
                       (C.muted if j == self._hover else C.faint))
        _, seg = self._geom()
        old_x0 = getattr(self, "_x0", i * seg + 14)
        new_x0 = i * seg + 14
        self._x0 = new_x0
        if animate and self.app:
            self.app.tweens.add(240, lambda k: _safe_coord(
                self, self._under, old_x0 + (new_x0 - old_x0) * k, self.h - 2,
                old_x0 + (new_x0 - old_x0) * k + 34, self.h), ease=ease_in_out)
        else:
            _safe_coord(self, self._under, new_x0, self.h - 2, new_x0 + 34, self.h)
        if self.app and self.app.on_tab_change:
            self.app.on_tab_change(i)

    def set_count(self, key, n):
        self.counts[key] = n
        self.redraw()


class HoverTree(ttk.Treeview):
    """Treeview with mouse-row hover highlight (extra 'hov' tag)."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.tag_configure("hov", background=C.hover)
        self.bind("<Motion>", self._on_motion, add="+")
        self.bind("<Leave>", self._on_leave, add="+")
        self._last = None

    def _on_motion(self, e):
        row = self.identify_row(e.y)
        if row == self._last:
            return
        self._set(self._last, False)
        self._last = row
        if row and row not in self.selection():
            self._set(row, True)

    def _on_leave(self, _=None):
        self._set(self._last, False)
        self._last = None

    def _set(self, row, add):
        if not row:
            return
        try:
            tags = list(self.item(row, "tags"))
        except Exception:
            return
        if add and "hov" not in tags:
            tags.append("hov")
            self.item(row, tags=tags)
        elif not add and "hov" in tags:
            tags.remove("hov")
            self.item(row, tags=tags)


class Skeleton:
    """Pulsing placeholder bars shown inside the profile card while loading."""

    BARS = [(0, 26, 62), (0, 40, 44), (0, 40, 78), (0, 40, 52), (0, 40, 70)]

    def __init__(self, card, app):
        self.app = app
        self.frame = tk.Frame(card, bg=C.card)
        self.cv = tk.Canvas(self.frame, width=296, height=258, bg=C.card,
                            highlightthickness=0)
        self.cv.pack(padx=16, pady=14)
        self.items = []
        x, y = 0, 6
        # avatar circle + two lines
        self.items.append(self.cv.create_oval(0, y, 64, y + 64, fill=C.card2,
                                              outline=""))
        self.items.append(self.cv.create_rectangle(78, y + 12, 200, y + 24,
                                                   fill=C.card2, outline=""))
        self.items.append(self.cv.create_rectangle(78, y + 34, 160, y + 44,
                                                   fill=C.card2, outline=""))
        y += 84
        for _, h, frac in self.BARS:
            self.items.append(self.cv.create_rectangle(
                0, y, int(296 * frac / 100), y + h, fill=C.card2, outline=""))
            y += h + 12
        self._t = 0.0

    def show(self):
        self._alive = True
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def hide(self):
        self._alive = False
        self.frame.place_forget()

    def step(self):
        if not getattr(self, "_alive", False):
            return
        self._t += 0.09
        for i, item in enumerate(self.items):
            k = (math.sin(self._t - i * 0.7) + 1) / 2          # 0..1 pulse
            _safe_item(self.cv, item, fill=mix(C.card2, C.hover, 0.35 + 0.65 * k))


class Toast:
    """Glass toast notification — slides up bottom-right, fades out."""

    ICONS = {"ok": "✓", "info": "i", "warn": "!", "error": "✕"}
    COLORS = {"ok": C.ok, "info": C.ice, "warn": C.warn, "error": C.danger}

    def __init__(self, mgr, msg, kind="info"):
        self.mgr = mgr
        self.kind = kind
        self.win = tk.Toplevel(mgr.app)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        try:
            self.win.attributes("-alpha", 0)
        except Exception:
            pass
        self.win.configure(bg=C.border)
        bar_col = self.COLORS[kind]
        body = tk.Frame(self.win, bg=C.card, highlightthickness=1,
                        highlightbackground=C.border2)
        body.pack(fill="both", expand=True)
        tk.Frame(body, bg=bar_col, width=4).pack(side="left", fill="y")
        inner = tk.Frame(body, bg=C.card)
        inner.pack(side="left", fill="both", expand=True, padx=(10, 14), pady=9)
        tk.Label(inner, text=self.ICONS[kind], bg=C.card, fg=bar_col,
                 font=font_of(size=11, bold=True)).pack(side="left", padx=(0, 8))
        tk.Label(inner, text=msg, bg=C.card, fg=C.text, justify="left",
                 wraplength=360, font=font_of(size=9)).pack(side="left")
        self.win.update_idletasks()
        w = self.win.winfo_reqwidth()
        h = self.win.winfo_reqheight()
        app = mgr.app
        self._tx = app.winfo_rootx() + app.winfo_width() - w - 22
        self._ty_goal = (app.winfo_rooty() + app.winfo_height() - h - 40
                         - mgr.stack_height())
        self.win.geometry(f"+{self._tx}+{self._ty_goal + 26}")
        self.win.deiconify()
        app.tweens.add(240, self._fade_in_step, ease=ease_out_cubic)
        self.win.after(3600, self._fade_out)

    def _fade_in_step(self, k):
        try:
            self.win.attributes("-alpha", k)
            self.win.geometry(f"+{self._tx}+{int(self._ty_goal + 26 * (1 - k))}")
        except Exception:
            pass

    def _fade_out(self):
        self.mgr.app.tweens.add(280, self._fade_out_step,
                                done=lambda: self.mgr.remove(self),
                                ease=ease_out_cubic)

    def _fade_out_step(self, k):
        try:
            self.win.attributes("-alpha", 1 - k)
        except Exception:
            pass

    def close(self):
        try:
            self.win.destroy()
        except Exception:
            pass


class ToastManager:
    def __init__(self, app):
        self.app = app
        self.live = []

    def show(self, msg, kind="info"):
        if len(self.live) >= 4:                    # keep the stack tidy
            self.remove(self.live[0])
        self.live.append(Toast(self, msg, kind))

    def stack_height(self):
        return len(self.live) * 62

    def remove(self, toast):
        if toast in self.live:
            self.live.remove(toast)
        toast.close()
        # slide remaining toasts down smoothly
        for i, t in enumerate(self.live):
            ty = (self.app.winfo_rooty() + self.app.winfo_height()
                  - t.win.winfo_height() - 40 - i * 62)
            tx = t._tx
            self.app.tweens.add(200, lambda k, t=t, ty=ty, tx=tx: _safe_geom(t, tx, ty))


def _safe_geom(win, x, y):
    try:
        win.geometry(f"+{x}+{y}")
    except Exception:
        pass


class Spinner(tk.Canvas):
    """Easing orbital spinner (canvas arc)."""

    def __init__(self, master, size=16):
        super().__init__(master, width=size, height=size, bg=master["bg"],
                         highlightthickness=0)
        self.size = size
        self.arc = self.create_arc(2, 2, size - 2, size - 2, start=0, extent=110,
                                   style="arc", outline=C.ice, width=2)
        self.angle = 0
        self.visible = False
        self.grid_remove()

    def start(self):
        if not self.visible:
            self.visible = True
            self.grid()

    def stop(self):
        if self.visible:
            self.visible = False
            self.grid_remove()

    def step(self):
        if not self.visible:
            return
        self.angle = (self.angle + 13) % 360
        _safe_item(self, self.arc, start=self.angle)


class BusyStrip(tk.Canvas):
    """Thin animated light-bar under the search band while a task runs."""

    def __init__(self, master, app):
        super().__init__(master, height=3, bg=C.panel, highlightthickness=0)
        self.app = app
        self._img = None
        self._item = None
        self._x = -160
        self.pack_propagate(False)
        self.bind("<Configure>", self._on_resize)
        self.pack_forget()

    def _on_resize(self, _=None):
        if self._img is None:
            self._img = gradient_strip(160, 3, (C.ice, C.ice2, C.indigo),
                                       peak=0.5)
            self._item = self.create_image(-160, 0, image=self._img, anchor="nw")

    def start(self):
        self.pack(fill="x", before=self.app.search_band)

    def stop(self):
        self.pack_forget()

    def step(self):
        if not self._item or not self.winfo_ismapped():
            return
        w = max(self.winfo_width(), 200)
        self._x += 7
        if self._x > w + 20:
            self._x = -160
        _safe_coord(self, self._item, self._x, 0)


# =================================================================== app ===

class App(tk.Tk):
    LOGO_SIZE = 42

    def __init__(self):
        super().__init__()
        self.withdraw()
        core.load_conf()
        self.title(f"{core.APP_NAME} — {core.TAGLINE}  ·  v{core.VERSION}")
        # Fit the actual desktop instead of forcing a window larger than
        # smaller laptop / VM screens. Centre it before building the widgets.
        self.update_idletasks()
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        win_w = min(1240, max(960, screen_w - 80))
        win_h = min(780, max(620, screen_h - 100))
        self.geometry(f"{win_w}x{win_h}+{max(0, (screen_w-win_w)//2)}+{max(0, (screen_h-win_h)//2)}")
        self.minsize(min(960, screen_w), min(620, screen_h))
        self.configure(bg=C.bg)
        self.q = queue.Queue()
        self.busy = 0
        self.user = None
        self.repos, self.gists, self.events, self.orgs = [], [], [], []
        self.avatar_ref = None
        self.repo_sel = None
        self.alive = True
        self.tweens = Tweens()
        self.on_tab_change = self._switch_tab
        self.logo_img = self._load_logo()

        self._styles()
        self._build()
        self._icon()
        self.toasts = ToastManager(self)
        # Show the supplied Moonlit Fox wallpaper as a 3-second splash,
        # then reveal the fully-built application.
        self._show_splash()
        self.after(80, self._frame)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Control-f>", lambda e: self.entry.focus_set() or self._ph_clear())
        self.bind("<Control-k>", lambda e: self.entry.focus_set() or self._ph_clear())
        self.bind("<Control-l>", lambda e: self._clear_search())

    # ------------------------------------------------------------ splash --
    def _show_splash(self):
        # Map the main window first: on some X11 window managers a Toplevel
        # whose Tk parent is withdrawn is also left unmapped (blank screen).
        self.deiconify()
        self.update_idletasks()

        self._splash = tk.Toplevel(self)
        self._splash.overrideredirect(True)
        self._splash.configure(bg="#03040B")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self._splash.geometry(f"{sw}x{sh}+0+0")
        try:
            self._splash.attributes("-topmost", True)
        except tk.TclError:
            pass

        self._splash_canvas = tk.Canvas(
            self._splash, bg="#03040B", highlightthickness=0, bd=0
        )
        self._splash_canvas.pack(fill="both", expand=True)

        # GIF is intentionally used here: Tk 8.6 decodes GIF natively,
        # whereas RGBA PNG support varies between Linux/Tk builds.
        p = Path(__file__).resolve().parent / "assets" / "moonlit-fox-splash.gif"
        self._splash_ref = None
        if p.is_file():
            try:
                img = tk.PhotoImage(file=str(p), master=self._splash)
                # Downsample only when the wallpaper is substantially larger
                # than the desktop; keep it crisp and avoid huge canvas blits.
                factor = max(1, math.ceil(max(img.width() / sw, img.height() / sh)))
                if factor > 1:
                    img = img.subsample(factor, factor)
                self._splash_ref = img
                self._splash_canvas.create_image(
                    sw // 2, sh // 2, image=img, anchor="center"
                )
            except (tk.TclError, OSError) as exc:
                # Never leave an unexplained blank splash if an asset is bad.
                self._splash_canvas.create_text(
                    sw // 2, sh // 2, text="ARCTIC FOX",
                    fill="#AAB8FF", font=("TkDefaultFont", 30, "bold")
                )
        else:
            self._splash_canvas.create_text(
                sw // 2, sh // 2, text="ARCTIC FOX",
                fill="#AAB8FF", font=("TkDefaultFont", 30, "bold")
            )

        self._splash.update_idletasks()
        self._splash.lift()
        self._splash.focus_force()
        self.after(3000, self._close_splash)

    def _close_splash(self):
        try:
            if self._splash and self._splash.winfo_exists():
                self._splash.destroy()
        except tk.TclError:
            pass
        self.deiconify()
        self.lift()
        try:
            self.attributes("-alpha", 1.0)
        except tk.TclError:
            pass

    # ------------------------------------------------------------ assets --
    def _load_logo(self):
        p = Path(__file__).resolve().parent / "assets" / "arcticfox-icon.png"
        if not p.exists():
            return None
        try:
            img = tk.PhotoImage(file=str(p))
            f = max(1, math.ceil(img.width() / self.LOGO_SIZE))
            return img.subsample(f, f)
        except Exception:
            return None

    def _icon(self):
        icon = Path(__file__).resolve().parent / "assets" / "arcticfox-icon.png"
        if icon.exists():
            try:
                self.icon_ref = tk.PhotoImage(file=str(icon))
                self.iconphoto(True, self.icon_ref)
            except Exception:
                pass

    def _fade_in(self):
        """Compatibility no-op: never hide the main window during startup."""
        try:
            self.attributes("-alpha", 1.0)
        except tk.TclError:
            pass

    # ------------------------------------------------------------- styles --
    def _styles(self):
        st = ttk.Style(self)
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure(".", background=C.panel, foreground=C.text,
                     fieldbackground=C.card, bordercolor=C.border,
                     lightcolor=C.panel, darkcolor=C.bg, troughcolor=C.bg)
        st.configure("Frost.Vertical.TScrollbar", background=C.panel,
                     troughcolor=C.bg, bordercolor=C.bg, arrowcolor=C.faint,
                     arrowsize=11, relief="flat")
        st.map("Frost.Vertical.TScrollbar",
               background=[("active", C.border2)])
        st.configure("Treeview", background=C.card, foreground=C.text,
                     fieldbackground=C.card, rowheight=34, borderwidth=0,
                     font=font_of(size=10))
        st.map("Treeview",
               background=[("selected", C.selbg)],
               foreground=[("selected", C.white)])
        st.configure("Treeview.Heading", background=C.panel, foreground=C.faint,
                     relief="flat", font=font_of(size=8, bold=True), padding=(10, 9))
        st.map("Treeview.Heading", background=[("active", C.panel)])
        st.configure("TCombobox", fieldbackground=C.card, background=C.card,
                     foreground=C.text, arrowcolor=C.ice, bordercolor=C.border,
                     lightcolor=C.border, darkcolor=C.border, padding=6)
        self.option_add("*TCombobox*Listbox.background", C.card)
        self.option_add("*TCombobox*Listbox.foreground", C.text)
        self.option_add("*TCombobox*Listbox.selectBackground", C.selbg)
        self.option_add("*TCombobox*Listbox.selectForeground", C.white)

    # -------------------------------------------------------------- build --
    def _build(self):
        self.header = Header(self, self)
        self.header.pack(fill="x")

        # ---- search band ---------------------------------------------------
        self.search_band = tk.Frame(self, bg=C.panel, pady=12, padx=18)
        self.search_band.pack(fill="x")

        self.seg = Segmented(self.search_band,
                             ["Username", "Full Name", "Email"],
                             on_change=self._mode_changed, app=self)
        self.seg.pack(side="left", padx=(0, 10))

        entry_wrap = tk.Frame(self.search_band, bg=C.panel)
        entry_wrap.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry = tk.Entry(entry_wrap, bg=C.card2, fg=C.text,
                              insertbackground=C.ice, relief="flat",
                              font=font_of(size=11), highlightthickness=1,
                              highlightbackground=C.border,
                              highlightcolor=C.ice)
        self.entry._ph = True
        self.entry.insert(0, "  Search any GitHub account — username, full name or email…")
        self.entry.config(fg=C.faint)
        self.entry.bind("<FocusIn>", self._ph_clear, add="+")
        self.entry.bind("<FocusOut>", self._ph_set, add="+")
        self.entry.bind("<Return>", lambda e: self.search())
        self.entry.bind("<Control-a>", self._entry_select_all, add="+")
        self.entry.pack(fill="x", ipady=7)
        self.entry.bind("<FocusIn>", self._entry_glow_on, add="+")
        self.entry.bind("<FocusOut>", self._entry_glow_off, add="+")

        self.btn_search = Btn(self.search_band, "SEARCH  ▸", command=self.search,
                              kind="ice", bold=True, size=10, app=self, padx=22)
        self.btn_search.pack(side="left")
        self.btn_settings = Btn(self.search_band, "SETTINGS", command=self.settings_dialog,
                                kind="ghost", size=8, bold=True, app=self, padx=14)
        self.btn_settings.pack(side="left", padx=(10, 0))

        self.busy_strip = BusyStrip(self, self)

        # ---- body: profile card + tabbed tables ----------------------------
        body = tk.Frame(self, bg=C.bg)
        body.pack(fill="both", expand=True)

        self.profile_card = self._build_profile(body)
        self.profile_card.pack(side="left", fill="both", padx=(18, 10), pady=(6, 8))

        right = tk.Frame(body, bg=C.bg)
        right.pack(side="left", fill="both", expand=True, padx=(0, 18), pady=(6, 8))
        self.tabbar = TabBar(right, self,
                             [("repos", "Repositories"), ("gists", "Gists"),
                              ("events", "Activity")])
        self.tabbar.pack(fill="x")
        self.tab_host = tk.Frame(right, bg=C.bg)
        self.tab_host.pack(fill="both", expand=True)
        self.tab_frames = {}
        self._build_repo_tab()
        self._build_gist_tab()
        self._build_event_tab()
        self._build_empty_state()
        self._switch_tab(0, animate=False)

        # ---- stats strip ----------------------------------------------------
        self.stats = self._build_stats()
        self.stats.pack(fill="x", padx=18, pady=(0, 8))

        self._build_statusbar()

    # --------------------------------------------------------- profile card --
    def _build_profile(self, parent):
        card = tk.Frame(parent, bg=C.card, highlightthickness=1,
                        highlightbackground=C.border, width=348, bd=0)
        card.pack_propagate(False)

        top = tk.Frame(card, bg=C.card)
        top.pack(fill="x", padx=18, pady=(18, 4))
        self.avatar = tk.Label(top, bg=C.card2, fg=C.ice, text="?",
                               font=font_of(size=24, bold=True), width=7, height=4)
        self.avatar.config(highlightthickness=2,
                           highlightbackground=C.border2,
                           highlightcolor=C.border2)
        self.avatar.pack(side="left", padx=(0, 14))
        idbox = tk.Frame(top, bg=C.card)
        idbox.pack(side="left", fill="x", expand=True)
        self.p_name = tk.Label(idbox, text="—", bg=C.card, fg=C.white,
                               font=font_of(size=14, bold=True), anchor="w")
        self.p_name.pack(fill="x")
        self.p_login = tk.Label(idbox, text="search to begin", bg=C.card, fg=C.ice,
                                font=font_of(mono=True, size=10), anchor="w")
        self.p_login.pack(fill="x")
        self.p_type = tk.Label(idbox, text="", bg=C.selbg, fg=C.ice,
                               font=font_of(size=7, bold=True), padx=8, pady=2)
        self.p_type.pack(anchor="w", pady=(5, 0))

        self.p_bio = tk.Label(card, text="", bg=C.card, fg=C.text, justify="left",
                              font=font_of(size=10), wraplength=290, anchor="w")
        self.p_bio.pack(fill="x", padx=18, pady=(4, 8))

        tk.Frame(card, bg=C.border, height=1).pack(fill="x", padx=18)
        self.p_rows = tk.Frame(card, bg=C.card)
        self.p_rows.pack(fill="x", padx=18, pady=(8, 0))
        self.p_orgs = tk.Label(card, text="", bg=C.card, fg=C.muted, justify="left",
                               font=font_of(size=9), wraplength=290, anchor="w")
        self.p_orgs.pack(fill="x", padx=18, pady=(8, 4))

        btns = tk.Frame(card, bg=C.card)
        btns.pack(side="bottom", fill="x", padx=18, pady=14)
        self.b_open = Btn(btns, "↗   Open Profile", command=self.open_profile,
                          kind="primary", size=10, app=self)
        self.b_open.pack(fill="x", pady=(0, 7))
        self.b_txt = Btn(btns, "▤   Save Report (.txt)", command=self.save_txt,
                         kind="soft", size=9, app=self)
        self.b_txt.pack(fill="x", pady=(0, 7))
        self.b_json = Btn(btns, "{ }   Export Data (.json)", command=self.export_json,
                          kind="ghost", size=9, app=self)
        self.b_json.pack(fill="x")
        for b in (self.b_open, self.b_txt, self.b_json):
            b.set_enabled(False)

        self.skeleton = Skeleton(card, self)
        return card

    def _prof_row(self, key):
        row = tk.Frame(self.p_rows, bg=C.card)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=key, width=9, anchor="w", bg=C.card, fg=C.faint,
                 font=font_of(size=8, bold=True)).pack(side="left")
        lbl = tk.Label(row, text="—", anchor="w", bg=C.card, fg=C.text,
                       font=font_of(size=9), wraplength=225, justify="left")
        lbl.pack(side="left", fill="x", expand=True)
        return lbl

    # ------------------------------------------------------------- tabs -----
    def _tree(self, parent, cols, widths, anchor="w"):
        wrap = tk.Frame(parent, bg=C.card, highlightthickness=1,
                        highlightbackground=C.border)
        tv = HoverTree(wrap, columns=cols, show="headings", selectmode="browse",
                       style="Treeview")
        for c, w in zip(cols, widths):
            tv.heading(c, text=c.upper())
            tv.column(c, width=w, anchor=anchor, stretch=(w >= 200))
        vs = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview,
                           style="Frost.Vertical.TScrollbar")
        tv.configure(yscrollcommand=vs.set)
        vs.pack(side="right", fill="y")
        tv.pack(fill="both", expand=True)
        tv.tag_configure("odd", background=C.card)
        tv.tag_configure("even", background=C.card2)
        return wrap, tv

    def _build_repo_tab(self):
        f = tk.Frame(self.tab_host, bg=C.bg)
        self.tab_frames[0] = f
        wrap, self.tv_repos = self._tree(
            f, ("#", "Repository", "Language", "STARS", "FORKS", "Updated", "Description"),
            (48, 250, 120, 76, 66, 96, 360))
        wrap.pack(fill="both", expand=True)
        self.tv_repos.bind("<<TreeviewSelect>>", self._on_repo_select)
        self.tv_repos.bind("<Double-1>", lambda e: self.details_selected())

        act = tk.Frame(f, bg=C.panel, padx=12, pady=9)
        act.pack(fill="x", side="bottom")
        self.b_clone = Btn(act, "⤓   CLONE", command=self.clone_selected,
                           kind="ice", bold=True, app=self)
        self.b_clone.pack(side="left", padx=(0, 8))
        self.b_details = Btn(act, "DETAILS", command=self.details_selected,
                             kind="soft", size=9, app=self)
        self.b_details.pack(side="left", padx=(0, 8))
        self.b_gh = Btn(act, "↗   OPEN ON GITHUB", command=self.open_selected,
                        kind="ghost", size=9, app=self)
        self.b_gh.pack(side="left")
        tk.Label(act, text="double-click a row for full details",
                 bg=C.panel, fg=C.faint, font=font_of(size=8)).pack(side="right")
        for b in (self.b_clone, self.b_details, self.b_gh):
            b.set_enabled(False)

    def _build_gist_tab(self):
        f = tk.Frame(self.tab_host, bg=C.bg)
        self.tab_frames[1] = f
        wrap, self.tv_gists = self._tree(f, ("Gist", "URL"), (460, 560))
        wrap.pack(fill="both", expand=True)
        self.tv_gists.bind("<Double-1>", self._open_gist)

    def _build_event_tab(self):
        f = tk.Frame(self.tab_host, bg=C.bg)
        self.tab_frames[2] = f
        wrap, self.tv_events = self._tree(
            f, ("When", "Event", "Repository"), (180, 210, 620))
        wrap.pack(fill="both", expand=True)

    def _switch_tab(self, i, animate=True):
        for j, f in self.tab_frames.items():
            f.pack_forget()
        f = self.tab_frames.get(i)
        if f:
            f.pack(fill="both", expand=True)
        if hasattr(self, "empty") and self.empty.winfo_ismapped():
            self.empty.lift()

    def _build_empty_state(self):
        self.empty = tk.Canvas(self.tab_host, bg=C.bg, highlightthickness=0)
        self.empty.bind("<Configure>", self._paint_empty)
        self.empty.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._empty_shown = True

    def _paint_empty(self, _=None):
        cv = self.empty
        cv.delete("all")
        w = max(cv.winfo_width(), 400)
        h = max(cv.winfo_height(), 260)
        cx, cy = w // 2, h // 2 - 26
        # stylised magnifier
        cv.create_oval(cx - 34, cy - 34, cx + 14, cy + 14, outline=C.border2,
                       width=3)
        cv.create_line(cx + 14, cy + 14, cx + 40, cy + 40, fill=C.border2,
                       width=3, capstyle="round")
        cv.create_text(cx - 10, cy - 10, text="?", fill=C.faint,
                       font=font_of(size=13, bold=True))
        cv.create_text(cx, cy + 66, text="NO DATA YET", fill=C.muted,
                       font=font_of(size=10, bold=True))
        cv.create_text(cx, cy + 88, text="Search any GitHub account to load its"
                       " repositories, gists and activity.",
                       fill=C.faint, font=font_of(size=9))

    def _hide_empty(self):
        if getattr(self, "_empty_shown", False):
            self.empty.place_forget()
            self._empty_shown = False

    # ------------------------------------------------------------ stats -----
    def _build_stats(self):
        bar = tk.Frame(self, bg=C.bg)
        self.chips = {}
        defs = (("REPOS", C.ice), ("STARS", C.gold), ("FORKS", C.indigo),
                ("TOP LANG", "#A78BFA"), ("FOLLOWERS", C.ok))
        for name, color in defs:
            tile = tk.Frame(bar, bg=C.card, highlightthickness=1,
                            highlightbackground=C.border)
            tile.pack(side="left", padx=(0, 10), fill="x", expand=True)
            tk.Frame(tile, bg=color, width=3).pack(side="left", fill="y")
            inner = tk.Frame(tile, bg=C.card)
            inner.pack(side="left", fill="both", expand=True, padx=(10, 12), pady=8)
            tk.Label(inner, text=name, bg=C.card, fg=C.faint,
                     font=font_of(size=7, bold=True)).pack(anchor="w")
            val = tk.Label(inner, text="0", bg=C.card, fg=color,
                           font=font_of(size=14, bold=True, mono=True))
            val.pack(anchor="w")
            self.chips[name] = val
        tk.Label(bar, text="reports → ~/arctic-fox-reports", bg=C.bg, fg=C.faint,
                 font=font_of(size=8)).pack(side="right", padx=(10, 0))
        return bar

    def _count_up(self, label, target):
        """Animate a numeric stat from its current value to target."""
        try:
            cur = int(str(label["text"]).replace(",", "").replace("—", "0") or 0)
        except ValueError:
            cur = 0
        if cur == target:
            label.config(text=core.fmt(target))
            return
        self.tweens.add(850, lambda k: _safe_cfg(
            label, "text", core.fmt(int(round(cur + (target - cur) * k)))),
            ease=ease_out_quart)

    # -------------------------------------------------------- status bar ----
    def _build_statusbar(self):
        bar = tk.Frame(self, bg=C.bg, pady=7, padx=18)
        bar.pack(fill="x", side="bottom")
        bar.columnconfigure(1, weight=1)
        self.spin = Spinner(bar)
        self.spin.grid(row=0, column=0, sticky="w")
        self.spin.grid_remove()          # hidden until a task starts
        self.status = tk.Label(bar, text="Ready — search any GitHub account.",
                               bg=C.bg, fg=C.muted, font=font_of(size=9), anchor="w")
        self.status.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.api_state = tk.Label(bar, text="token: off · api.github.com",
                                  bg=C.bg, fg=C.faint, font=font_of(size=8, mono=True))
        self.api_state.grid(row=0, column=2, sticky="e")
        self._api_state_refresh()

    def _api_state_refresh(self):
        on = bool(core.CONF["token"])
        self.api_state.config(text=f"token: {'on ' if on else 'off'} · api.github.com",
                              fg=C.ok if on else C.faint)
        if hasattr(self, "header"):
            self.header.refresh_token_pill()

    # -------------------------------------------------- search entry glow ---
    def _entry_glow_on(self, _=None):
        self.tweens.color(self.entry, "highlightbackground", C.border, C.ice, 160)
        self.tweens.color(self.entry, "highlightcolor", C.ice, C.ice2, 160)

    def _entry_glow_off(self, _=None):
        self.tweens.color(self.entry, "highlightbackground", C.border, C.border, 220)

    def _mode_changed(self, _mode):
        if not getattr(self.entry, "_ph", False):
            self.entry.focus_set()

    # ------------------------------------------------------ status helpers --
    def set_status(self, msg, busy=False):
        self.status.config(text=msg)

    def _post(self, fn, *a):
        self.q.put((fn, a))

    def _frame(self):
        """Central 30 fps animation tick."""
        if not self.alive:
            return
        try:
            self.tweens.tick()
            self.header.step()
            self.spin.step()
            self.busy_strip.step()
            self.skeleton.step()
            while True:
                try:
                    fn, a = self.q.get_nowait()
                except queue.Empty:
                    break
                try:
                    fn(*a)
                except Exception as e:
                    self.set_status(f"UI error: {e}")
        except Exception:
            pass
        self.after(33, self._frame)

    def _busy_start(self):
        self.busy += 1
        if self.busy == 1:
            self.spin.start()
            self.busy_strip.start()
            self.btn_search.config(state="disabled", fg=C.bg)
            self.skeleton.show()

    def _busy_end(self):
        self.busy = max(0, self.busy - 1)
        if self.busy == 0:
            self.spin.stop()
            self.busy_strip.stop()
            self.btn_search.config(state="normal", fg=C.bg)
            self.skeleton.hide()

    # ----------------------------------------------------------- placeholder --
    def _ph_clear(self, _=None):
        if getattr(self.entry, "_ph", False):
            self.entry.delete(0, "end")
            self.entry.config(fg=C.text)
            self.entry._ph = False

    def _ph_set(self, _=None):
        if not self.entry.get().strip():
            self.entry._ph = True
            self.entry.delete(0, "end")
            self.entry.insert(0, "  Search any GitHub account — username, full name or email…")
            self.entry.config(fg=C.faint)

    def _clear_search(self):
        self.entry.delete(0, "end")
        self.entry.focus_set()

    # ------------------------------------------------------------- dialogs --
    def _dialog(self, title, w, h):
        """Create a centered, modal, Escape-closable dialog window."""
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=C.bg)
        win.transient(self)
        win.resizable(False, False)
        self.update_idletasks()
        x = self.winfo_rootx() + max(0, (self.winfo_width() - w) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - h) // 3)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.bind("<Escape>", lambda e: win.destroy())
        win.protocol("WM_DELETE_WINDOW", win.destroy)
        self.after(120, lambda: _safe_grab(win))
        return win

    # -------------------------------------------------------------- search --
    def search(self):
        if self.busy:
            return
        self._ph_clear()
        text = self.entry.get().strip().lstrip("@")
        if not text or getattr(self.entry, "_ph", False):
            self.set_status("Type a username first.")
            return
        mode = self.seg.get()
        if mode == "Username":
            self.load_profile(text)
        else:
            self.user_search(text, mode)

    def _entry_select_all(self, _=None):
        self.entry.selection_range(0, "end")
        self.entry.icursor("end")
        return "break"

    def load_profile(self, login):
        self._busy_start()
        self.set_status(f"Fetching @{login} …")
        threading.Thread(target=self._t_profile, args=(login,), daemon=True).start()

    def _t_profile(self, login):
        try:
            u = core.gh_api(f"/users/{login}")
        except core.ApiError as e:
            self._post(self._busy_end)
            self._post(self._search_failed, str(e))
            return
        self._post(self._render_profile, u)
        try:
            orgs = core.gh_api(f"/users/{login}/orgs")
        except core.ApiError:
            orgs = []
        self._post(self._render_orgs, orgs)
        self._post(self.set_status, "Fetching repositories …")
        try:
            repos = core.gh_api_all(f"/users/{login}/repos", {"sort": "updated"})
        except core.ApiError as e:
            repos = []
            self._post(self.set_status, f"Repos: {e}")
        self._post(self._render_repos, repos)
        try:
            gists = core.gh_api_all(f"/users/{login}/gists", cap=100)
        except core.ApiError:
            gists = []
        self._post(self._render_gists, gists)
        self._post(self.set_status, "Fetching recent activity …")
        try:
            events = core.gh_api(f"/users/{login}/events/public", {"per_page": 15})
        except core.ApiError:
            events = []
        self._post(self._render_events, events)
        self._post(self._done, f"@{u['login']} loaded — {len(repos)} repositories.")
        self._post(self._fetch_avatar, u)

    def _fetch_avatar(self, u):
        threading.Thread(target=self._t_avatar, args=(u,), daemon=True).start()

    def _t_avatar(self, u):
        try:
            url = u["avatar_url"]
            sep = "&" if "?" in url else "?"
            raw = core.fetch_bytes(url + sep + "size=200")
            b64 = base64.b64encode(raw).decode()
            self._post(self._render_avatar, b64, u.get("name") or u["login"])
        except Exception:
            pass

    def _render_avatar(self, b64, name):
        try:
            raw = base64.b64decode(b64)
            img = None
            # Pillow handles GitHub avatars returned as PNG, JPEG, or WebP.
            try:
                from PIL import Image, ImageTk
                pil = Image.open(io.BytesIO(raw)).convert("RGBA")
                pil.thumbnail((112, 112), Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(pil, master=self)
            except ImportError:
                # Tk's built-in decoder supports PNG/GIF/PPM without extras.
                img = tk.PhotoImage(data=b64)
                factor = max(1, math.ceil(max(img.width(), img.height()) / 112))
                if factor > 1:
                    img = img.subsample(factor, factor)
            self.avatar_ref = img
            self.avatar.config(image=img, text="", width=96, height=96,
                               bg=C.card, compound="center")
        except Exception:
            self._initials(name)

    def _initials(self, name):
        self.avatar.config(image="", text=" ".join((name or "?")[:2]).upper() + " ",
                           bg=C.deep, fg=C.ice)

    def _search_failed(self, msg):
        self.set_status(msg)
        self.toasts.show(msg, "error")

    def _done(self, msg):
        self._busy_end()
        self.set_status(msg)

    # --------------------------------------------------- user search mode --
    def user_search(self, text, mode):
        self._busy_start()
        self.set_status(f"Searching users — {mode.lower()} “{text}” …")
        threading.Thread(target=self._t_user_search, args=(text, mode),
                         daemon=True).start()

    def _t_user_search(self, text, mode):
        try:
            items = core.search_users(text, mode)
        except core.ApiError as e:
            self._post(self._busy_end)
            self._post(self._search_failed, str(e))
            return
        self._post(self._show_user_results, items, text, mode)
        self._post(self._busy_end)

    def _show_user_results(self, items, text, mode):
        if not items:
            self.set_status(f"No users matched “{text}” ({mode.lower()}).")
            self.toasts.show(f"No users matched “{text}”.", "warn")
            return
        win = self._dialog(f"User results — “{text}” ({len(items)})", 660, 440)
        head = tk.Frame(win, bg=C.panel, padx=16, pady=10)
        head.pack(fill="x")
        tk.Label(head, text=f"{len(items)} USERS MATCHED “{text.upper()}”",
                 bg=C.panel, fg=C.white, font=font_of(size=10, bold=True)).pack(side="left")
        wrap, tv = self._tree(win, ("Login", "Type"), (320, 220))
        wrap.pack(fill="both", expand=True, padx=14, pady=12)
        for i, it in enumerate(items):
            tv.insert("", "end", iid=str(i),
                      values=(it.get("login"), it.get("type", "User")),
                      tags=("odd" if i % 2 else "even",))

        def view(_=None):
            sel = tv.selection()
            if sel:
                win.destroy()
                self.seg.set("Username")
                self._ph_clear()
                self.entry.delete(0, "end")
                self.entry.insert(0, tv.item(sel[0], "values")[0])
                self.load_profile(tv.item(sel[0], "values")[0])

        btns = tk.Frame(win, bg=C.bg)
        btns.pack(fill="x", padx=14, pady=(0, 14))
        Btn(btns, "→   VIEW PROFILE", command=view, kind="ice", bold=True,
            app=self).pack(side="left")
        tk.Label(btns, text="double-click a result to open it",
                 bg=C.bg, fg=C.faint, font=font_of(size=8)).pack(side="right")
        tv.bind("<Double-1>", view)
        self.set_status(f"{len(items)} users matched “{text}”.")

    # ----------------------------------------------------------- renderers --
    def _render_profile(self, u):
        self.user = u
        name = u.get("name") or u["login"]
        self._hide_empty()
        self.p_name.config(text=name)
        self.p_login.config(text="@" + u["login"])
        self.p_type.config(text=f"  {u['type']}  ")
        self.p_bio.config(text=u.get("bio") or "")
        for w in self.p_rows.winfo_children():
            w.destroy()
        rows = [("LOCATION", u.get("location")), ("COMPANY", u.get("company")),
                ("WEBSITE", u.get("blog")), ("TWITTER", ("@" + u["twitter_username"])
                        if u.get("twitter_username") else None),
                ("EMAIL", u.get("email")), ("JOINED", u["created_at"][:10]),
                ("UPDATED", u["updated_at"][:10])]
        self._row_labels = [self._prof_row(k) for k, _ in rows]
        for i, (lbl, (_, v)) in enumerate(zip(self._row_labels, rows)):
            lbl.config(text=v or "—", fg=C.faint)
            if v:
                self.tweens.color(lbl, "fg", C.faint, C.text, 320,
                                  ease=ease_out_cubic)
        self._initials(name)
        for b in (self.b_open, self.b_txt, self.b_json):
            b.set_enabled(True)

    def _render_orgs(self, orgs):
        self.orgs = orgs
        if orgs:
            self.p_orgs.config(text="ORGS   " + ", ".join(o["login"] for o in orgs[:8]),
                               fg=C.muted)
        else:
            self.p_orgs.config(text="")

    def _render_repos(self, repos):
        self.repos = repos
        self.tv_repos.delete(*self.tv_repos.get_children())
        for i, r in enumerate(repos):
            desc = (r.get("description") or "")[:64]
            self.tv_repos.insert("", "end", iid=str(i), tags=("odd" if i % 2 else "even"),
                                 values=(f"{i+1:03d}", r["name"], r.get("language") or "—",
                                         core.fmt(r.get("stargazers_count", 0)),
                                         core.fmt(r.get("forks_count", 0)),
                                         r["updated_at"][:10], desc))
        self.tabbar.set_count("repos", len(repos))
        for b in (self.b_clone, self.b_details, self.b_gh):
            b.set_enabled(False)
        self.repo_sel = None
        self._update_stats()

    def _render_gists(self, gists):
        self.gists = gists
        self.tv_gists.delete(*self.tv_gists.get_children())
        for i, g in enumerate(gists):
            self.tv_gists.insert("", "end", tags=("odd" if i % 2 else "even"),
                                 values=(g.get("description") or "(no description)",
                                         g["html_url"]))
        self.tabbar.set_count("gists", len(gists))

    def _render_events(self, events):
        self.events = events
        self.tv_events.delete(*self.tv_events.get_children())
        for i, e in enumerate(events):
            self.tv_events.insert("", "end", tags=("odd" if i % 2 else "even"),
                                  values=(e["created_at"][:16].replace("T", " "),
                                          e.get("type", ""), e["repo"]["name"]))
        self.tabbar.set_count("events", len(events))

    def _update_stats(self):
        if not self.user:
            return
        s = core.stats_summary(self.user, self.repos)
        self._count_up(self.chips["REPOS"], s["repos"])
        self._count_up(self.chips["STARS"], s["stars"])
        self._count_up(self.chips["FORKS"], s["forks"])
        self.chips["TOP LANG"].config(text=str(s["top_language"]))
        self._count_up(self.chips["FOLLOWERS"], s["followers"])

    # --------------------------------------------------------- repo actions --
    def _on_repo_select(self, _=None):
        sel = self.tv_repos.selection()
        if not sel or not self.repos:
            return
        self.repo_sel = self.repos[int(sel[0])]
        for b in (self.b_clone, self.b_details, self.b_gh):
            b.set_enabled(True)

    def _sel_full(self):
        if not self.repo_sel:
            self.toasts.show("Select a repository first.", "warn")
            return None
        return self.repo_sel["full_name"]

    def clone_selected(self):
        full = self._sel_full()
        if not full or self.busy:
            return
        self._busy_start()
        self.set_status(f"Cloning {full} …")

        def on_line(t):
            self._post(self.set_status, f"Cloning {full} — {t}")

        def on_done(ok_, msg):
            self._post(self._clone_done, ok_, msg)

        threading.Thread(target=core.clone_repo,
                         args=(full, core.CONF["clone_dir"], on_line, on_done),
                         daemon=True).start()

    def _clone_done(self, ok_, msg):
        self._busy_end()
        self.set_status(msg)
        self.toasts.show(msg, "ok" if ok_ else "error")

    def details_selected(self):
        full = self._sel_full()
        if not full or self.busy:
            return
        self._busy_start()
        self.set_status(f"Fetching details for {full} …")

        def t():
            try:
                d = core.gh_api(f"/repos/{full}")
            except core.ApiError as e:
                self._post(self._busy_end)
                self._post(self._search_failed, str(e))
                return
            self._post(self._show_repo_details, d)
            self._post(self._busy_end)

        threading.Thread(target=t, daemon=True).start()

    def _show_repo_details(self, d):
        win = self._dialog(f"Repo details — {d['full_name']}", 600, 560)
        head = tk.Frame(win, bg=C.card, padx=18, pady=14, highlightthickness=1,
                        highlightbackground=C.border)
        head.pack(fill="x")
        tk.Label(head, text=d["name"], bg=C.card, fg=C.white,
                 font=font_of(size=15, bold=True)).pack(anchor="w")
        tk.Label(head, text=d.get("description") or "—", bg=C.card, fg=C.muted,
                 font=font_of(size=9), wraplength=540, justify="left").pack(anchor="w")

        # mini stat tiles
        tiles = tk.Frame(win, bg=C.bg)
        tiles.pack(fill="x", padx=16, pady=(12, 0))
        mini = (("STARS", core.fmt(d["stargazers_count"]), C.gold),
                ("FORKS", core.fmt(d["forks_count"]), C.indigo),
                ("WATCHING", core.fmt(d.get("subscribers_count", 0)), C.ice),
                ("ISSUES", core.fmt(d.get("open_issues_count", 0)), C.danger))
        for label, value, color in mini:
            t = tk.Frame(tiles, bg=C.card, highlightthickness=1,
                         highlightbackground=C.border)
            t.pack(side="left", padx=(0, 8), fill="x", expand=True)
            ti = tk.Frame(t, bg=C.card)
            ti.pack(padx=12, pady=7)
            tk.Label(ti, text=value, bg=C.card, fg=color,
                     font=font_of(size=12, bold=True, mono=True)).pack(anchor="w")
            tk.Label(ti, text=label, bg=C.card, fg=C.faint,
                     font=font_of(size=7, bold=True)).pack(anchor="w")

        body = tk.Frame(win, bg=C.bg, padx=18, pady=12)
        body.pack(fill="both", expand=True)
        info = [("Full name", d["full_name"]),
                ("Language", d.get("language") or "—"),
                ("License", (d.get("license") or {}).get("spdx_id") or "none"),
                ("Created", d["created_at"][:10]),
                ("Last push", d["pushed_at"][:10]),
                ("Size", f"{d.get('size', 0)} KB"),
                ("Homepage", d.get("homepage") or "—")]
        for k, v in info:
            row = tk.Frame(body, bg=C.bg)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=k.upper(), width=12, anchor="w", bg=C.bg, fg=C.faint,
                     font=font_of(size=8, bold=True)).pack(side="left")
            tk.Label(row, text=str(v), anchor="w", bg=C.bg, fg=C.text,
                     font=font_of(size=9), wraplength=380,
                     justify="left").pack(side="left", fill="x", expand=True)
        topics = d.get("topics") or []
        if topics:
            tk.Label(body, text="TOPICS", bg=C.bg, fg=C.faint,
                     font=font_of(size=8, bold=True)).pack(anchor="w", pady=(8, 4))
            chips = tk.Frame(body, bg=C.bg)
            chips.pack(anchor="w")
            for t in topics[:10]:
                Pill(chips, t, C.ice, bg=C.card, size=8, padx=10, pady=3
                     ).pack(side="left", padx=3)
        Btn(win, "↗   OPEN ON GITHUB",
            command=lambda: webbrowser.open(d["html_url"]),
            kind="ice", bold=True, app=self).pack(pady=10)

    def open_selected(self):
        full = self._sel_full()
        if full:
            webbrowser.open(f"https://github.com/{full}")

    def open_profile(self):
        if self.user:
            webbrowser.open(self.user["html_url"])

    def _open_gist(self, _=None):
        sel = self.tv_gists.selection()
        if sel:
            url = self.tv_gists.item(sel[0], "values")[1]
            if url.startswith("http"):
                webbrowser.open(url)

    # -------------------------------------------------------------- exports --
    def _need_user(self):
        if not self.user:
            self.toasts.show("Load a profile first.", "warn")
            return False
        return True

    def save_txt(self):
        if not self._need_user():
            return
        try:
            f = core.save_report(self.user, self.repos, self.gists, self.events)
            self.set_status(f"Report saved → {f}")
            self.toasts.show(f"Report saved → {f.name}", "ok")
        except OSError as e:
            self.toasts.show(f"Save failed: {e}", "error")

    def export_json(self):
        if not self._need_user():
            return
        try:
            f = core.save_json(self.user, self.repos, self.gists, self.events)
            self.set_status(f"JSON export → {f}")
            self.toasts.show(f"JSON exported → {f.name}", "ok")
        except OSError as e:
            self.toasts.show(f"Export failed: {e}", "error")

    # -------------------------------------------------------------- settings --
    def settings_dialog(self):
        win = self._dialog("Settings — Arctic Fox", 560, 370)

        def card(parent):
            f = tk.Frame(parent, bg=C.card, highlightthickness=1,
                         highlightbackground=C.border)
            return f

        fr = tk.Frame(win, bg=C.bg, padx=22, pady=18)
        fr.pack(fill="both", expand=True)

        c1 = card(fr)
        c1.pack(fill="x")
        head1 = tk.Frame(c1, bg=C.card)
        head1.pack(fill="x", padx=16, pady=(12, 0))
        tk.Label(head1, text="GITHUB TOKEN", bg=C.card, fg=C.white,
                 font=font_of(size=9, bold=True)).pack(side="left")
        tk.Label(head1, text="optional — higher rate limits", bg=C.card, fg=C.faint,
                 font=font_of(size=8)).pack(side="left", padx=(8, 0))
        tokrow = tk.Frame(c1, bg=C.card)
        tokrow.pack(fill="x", padx=16, pady=(8, 2))
        tok = tk.Entry(tokrow, bg=C.card2, fg=C.text, relief="flat", show="•",
                       insertbackground=C.ice, font=font_of(mono=True, size=10),
                       highlightthickness=1, highlightbackground=C.border)
        tok.pack(side="left", fill="x", expand=True, ipady=6)
        if core.CONF["token"]:
            tok.insert(0, core.CONF["token"])
        tok._show = False

        def toggle_show():
            tok._show = not tok._show
            tok.config(show="" if tok._show else "•")
            show_btn.config(text="HIDE" if tok._show else "SHOW")

        show_btn = Btn(tokrow, "SHOW", command=toggle_show, kind="soft", size=8,
                       app=self, padx=10)
        show_btn.pack(side="left", padx=(8, 0))
        tk.Label(c1, text="github.com/settings/tokens → classic token, no scope needed for public data",
                 bg=C.card, fg=C.faint, font=font_of(size=8)).pack(anchor="w",
                                                                   padx=16, pady=(0, 12))

        c2 = card(fr)
        c2.pack(fill="x", pady=(12, 0))
        tk.Label(c2, text="CLONE DIRECTORY", bg=C.card, fg=C.white,
                 font=font_of(size=9, bold=True)).pack(anchor="w", padx=16,
                                                       pady=(12, 0))
        drow = tk.Frame(c2, bg=C.card)
        drow.pack(fill="x", padx=16, pady=(8, 2))
        d = tk.Entry(drow, bg=C.card2, fg=C.text, relief="flat",
                     insertbackground=C.ice, font=font_of(mono=True, size=10),
                     highlightthickness=1, highlightbackground=C.border)
        d.pack(side="left", fill="x", expand=True, ipady=6)
        d.insert(0, core.CONF["clone_dir"])

        def browse():
            p = filedialog.askdirectory(parent=win)
            if p:
                d.delete(0, "end")
                d.insert(0, p)

        Btn(drow, "BROWSE …", command=browse, kind="soft", size=8, app=self,
            padx=12).pack(side="left", padx=(8, 0))
        tk.Frame(c2, bg=C.card).pack(pady=(0, 12))

        def test_connection():
            def t():
                try:
                    core.gh_api("/rate_limit")
                    msg, kind = "Connection OK — GitHub API reachable.", "ok"
                except core.ApiError as e:
                    msg, kind = f"API problem: {e}", "error"
                self._post(self.toasts.show, msg, kind)
            threading.Thread(target=t, daemon=True).start()

        btns = tk.Frame(fr, bg=C.bg)
        btns.pack(fill="x", pady=(14, 0))

        def save():
            core.CONF["token"] = tok.get().strip()
            if d.get().strip():
                core.CONF["clone_dir"] = d.get().strip()
            core.save_conf()
            self._api_state_refresh()
            self.set_status("Settings saved.")
            self.toasts.show("Settings saved.", "ok")
            win.destroy()

        Btn(btns, "SAVE", command=save, kind="ice", bold=True, app=self,
            padx=22).pack(side="left")
        Btn(btns, "TEST CONNECTION", command=test_connection, kind="soft",
            size=9, app=self).pack(side="left", padx=8)
        Btn(btns, "CANCEL", command=win.destroy, kind="ghost", app=self,
            padx=14).pack(side="left")

    # ----------------------------------------------------------------- misc --
    def on_close(self):
        self.alive = False
        self.destroy()


def main():
    args = [a for a in sys.argv[1:]]
    here = Path(__file__).resolve().parent

    if args and args[0] in ("-v", "--version"):
        print(f"{core.APP_NAME} {core.VERSION} (GUI edition)")
        return
    if args and args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if args and args[0] == "--cli":
        os.execv(sys.executable, [sys.executable, str(here / "arcticfox-cli.py")] + args[1:])

    try:
        app = App()
    except tk.TclError as exc:                       # no X display / broken X
        _gui_unavailable(str(exc))
    target = args[0].lstrip("@").strip() if args else ""
    if target:
        app.entry.delete(0, "end")
        app.entry.insert(0, target)
        app.after(400, app.search)
    app.mainloop()


if __name__ == "__main__":
    main()
