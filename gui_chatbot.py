"""
gui_chatbot.py
---------------
A polished, premium desktop chat UI for RuleBot, built with Tkinter
(part of Python's standard library - no extra installs needed).

Design:
- Deep dark glassmorphism-inspired theme with vibrant gradients
- Chat bubbles: bot (left, dark glass) + user (right, gradient amber/orange)
- Animated typing indicator with smooth dot animation
- Quick-reply suggestion chips with hover effects
- Placeholder text in the entry field
- Visual button feedback (press states)
- Smooth auto-scroll and proper layout
- Timestamps, status pill, and clear chat functionality

All actual decision-making lives in chatbot_logic.py.

Run with:
    python gui_chatbot.py
"""

import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime

from chatbot_logic import get_response, is_exit_command

# ---------------------------------------------------------------------------
# THEME / DESIGN TOKENS - Premium Dark Theme with Gradient Accents
# ---------------------------------------------------------------------------
BG              = "#0F1117"   # deep dark background
BG_SECONDARY    = "#161920"   # slightly lighter
PANEL           = "#1A1D27"   # header / input panel
PANEL_BORDER    = "#2A2E3B"   # subtle border color
BUBBLE_BOT      = "#1E2233"   # bot message bubble - dark glass
BUBBLE_BOT_BDR  = "#2A3050"   # bot bubble subtle border
BUBBLE_USER     = "#E8923D"   # user bubble - warm amber/orange
BUBBLE_USER_ALT = "#D4782A"   # user bubble pressed / darker variant
TEXT_LIGHT      = "#EAECF0"   # primary text
TEXT_MEDIUM     = "#B0B8C8"   # secondary text
TEXT_MUTED      = "#6B7280"   # tertiary / timestamps
TEXT_ON_USER    = "#0F1117"   # text on amber user bubble
ACCENT          = "#E8923D"   # primary accent amber
ACCENT_HOVER    = "#F0A050"   # accent hover state
ACCENT_PRESSED  = "#C87828"   # accent pressed state
ONLINE_DOT      = "#34D399"   # green status dot
CHIP_BG         = "#1E2233"   # chip background
CHIP_BG_HOVER   = "#2A3050"   # chip hover
CHIP_BORDER     = "#2E3650"   # chip border
INPUT_BG        = "#1A1E2A"   # input field background
INPUT_BG_FOCUS  = "#202638"   # input focused
SCROLLBAR_BG    = "#1A1D27"   # scrollbar trough
SCROLLBAR_FG    = "#2E3650"   # scrollbar thumb
SEPARATOR       = "#1E2233"   # separator lines
SHADOW          = "#080A10"   # shadow/depth color

# Font stack - use Segoe UI on Windows, Helvetica elsewhere
import platform
FONT_FAMILY = "Segoe UI" if platform.system() == "Windows" else "Helvetica"


class ChatBubble(tk.Frame):
    """A single chat message rendered as a styled bubble with rounded appearance."""

    def __init__(self, parent, text, sender, timestamp, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        is_user = sender == "user"

        bubble_bg = BUBBLE_USER if is_user else BUBBLE_BOT
        text_color = TEXT_ON_USER if is_user else TEXT_LIGHT
        pack_side = "right" if is_user else "left"
        anchor_dir = "e" if is_user else "w"
        ts_color = TEXT_MUTED if not is_user else "#7A6040"

        # Sender label (small, above bubble)
        sender_row = tk.Frame(self, bg=BG)
        sender_row.pack(fill="x", expand=True)
        sender_label_font = tkfont.Font(family=FONT_FAMILY, size=8, weight="bold")
        sender_name = "You" if is_user else "RuleBot"
        sender_label = tk.Label(
            sender_row, text=sender_name, bg=BG,
            fg=ACCENT if not is_user else TEXT_MUTED,
            font=sender_label_font,
        )
        sender_label.pack(anchor=anchor_dir, padx=16, pady=(6, 0))

        # Bubble row
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", expand=True)

        # Outer frame for border effect
        border_frame = tk.Frame(
            row, bg=BUBBLE_BOT_BDR if not is_user else BUBBLE_USER_ALT,
        )
        border_frame.pack(side=pack_side, padx=12, pady=2)

        # Inner bubble
        bubble = tk.Frame(border_frame, bg=bubble_bg)
        bubble.pack(padx=1, pady=1)

        label_font = tkfont.Font(family=FONT_FAMILY, size=11)
        msg_label = tk.Label(
            bubble,
            text=text,
            bg=bubble_bg,
            fg=text_color,
            font=label_font,
            wraplength=320,
            justify="left",
            padx=14,
            pady=10,
        )
        msg_label.pack()

        # Timestamp below bubble
        ts_row = tk.Frame(self, bg=BG)
        ts_row.pack(fill="x", expand=True)
        ts_font = tkfont.Font(family=FONT_FAMILY, size=7)
        ts_label = tk.Label(
            ts_row,
            text=timestamp,
            bg=BG,
            fg=ts_color,
            font=ts_font,
        )
        ts_label.pack(anchor=anchor_dir, padx=18, pady=(0, 2))


class TypingIndicator(tk.Frame):
    """Animated typing indicator with 'RuleBot is typing...' text."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", expand=True)

        # Label saying "RuleBot is typing"
        label_font = tkfont.Font(family=FONT_FAMILY, size=8, slant="italic")
        self.typing_label = tk.Label(
            row, text="RuleBot is typing", bg=BG, fg=TEXT_MUTED,
            font=label_font,
        )
        self.typing_label.pack(side="left", padx=16, pady=(4, 0))

        # Dots row
        dot_row = tk.Frame(self, bg=BG)
        dot_row.pack(fill="x", expand=True)

        self.bubble = tk.Frame(dot_row, bg=BUBBLE_BOT)
        self.bubble.pack(side="left", padx=12, pady=3)

        self.dot_font = tkfont.Font(family=FONT_FAMILY, size=16, weight="bold")
        self.label = tk.Label(
            self.bubble, text="", bg=BUBBLE_BOT, fg=ACCENT,
            font=self.dot_font, padx=14, pady=6, width=4
        )
        self.label.pack()

        self._step = 0
        self._running = True
        self._animate()

    def _animate(self):
        if not self._running:
            return
        frames = ["●  ", "●● ", "●●●", " ●●", "  ●", "   "]
        self.label.config(text=frames[self._step % len(frames)])
        self._step += 1
        self.after(200, self._animate)

    def stop(self):
        self._running = False


class PlaceholderEntry(tk.Entry):
    """Entry widget with placeholder text that disappears on focus."""

    def __init__(self, master, placeholder="Type a message...", **kwargs):
        super().__init__(master, **kwargs)
        self._placeholder = placeholder
        self._placeholder_color = TEXT_MUTED
        self._normal_color = kwargs.get("fg", TEXT_LIGHT)
        self._has_placeholder = False

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        self._show_placeholder()

    def _show_placeholder(self):
        if not self.get():
            self._has_placeholder = True
            self.insert(0, self._placeholder)
            self.config(fg=self._placeholder_color)

    def _on_focus_in(self, event=None):
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.config(fg=self._normal_color)
            self._has_placeholder = False

    def _on_focus_out(self, event=None):
        if not self.get():
            self._show_placeholder()

    def get_text(self):
        """Get text, returning empty string if placeholder is showing."""
        if self._has_placeholder:
            return ""
        return self.get().strip()

    def clear(self):
        """Clear the entry and reset placeholder."""
        self.delete(0, tk.END)
        self.config(fg=self._normal_color)
        self._has_placeholder = False


class ChatbotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RuleBot  —  Smart Rule-Based Chatbot")
        self.geometry("500x720")
        self.minsize(400, 560)
        self.configure(bg=BG)

        # Try to set dark title bar on Windows
        try:
            self.update()
            from ctypes import windll
            hwnd = windll.user32.GetParent(self.winfo_id())
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, byref := (c_int := __import__('ctypes').c_int)(1), 4)
        except Exception:
            pass

        self._typing_widget = None
        self._message_count = 0
        self._build_header()
        self._build_chat_area()
        self._build_quick_replies()
        self._build_input_bar()

        # Welcome message after a short delay
        self.after(400, lambda: self._bot_say(
            "Hi! I'm RuleBot 🤖\n\n"
            "I can chat about lots of things! Try:\n"
            "• Greetings, jokes, facts, riddles\n"
            "• Movies, music, food, sports\n"
            "• Word tricks, tech talk, and more!\n\n"
            "Type 'help' for my full menu."
        ))

    # -- UI construction ----------------------------------------------------
    def _build_header(self):
        # Header shadow line
        shadow = tk.Frame(self, bg=SHADOW, height=2)
        shadow.pack(fill="x", side="top")

        header = tk.Frame(self, bg=PANEL, height=68)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Bottom border
        border = tk.Frame(self, bg=PANEL_BORDER, height=1)
        border.pack(fill="x", side="top")

        # Avatar with accent background
        avatar_frame = tk.Frame(header, bg=ACCENT, width=40, height=40)
        avatar_frame.pack(side="left", padx=(16, 10), pady=14)
        avatar_frame.pack_propagate(False)

        avatar_font = tkfont.Font(family=FONT_FAMILY, size=16, weight="bold")
        avatar_label = tk.Label(
            avatar_frame, text="R", bg=ACCENT, fg=TEXT_ON_USER,
            font=avatar_font,
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        # Title and status
        title_box = tk.Frame(header, bg=PANEL)
        title_box.pack(side="left", pady=10)

        name_font = tkfont.Font(family=FONT_FAMILY, size=14, weight="bold")
        tk.Label(title_box, text="RuleBot", bg=PANEL, fg=TEXT_LIGHT,
                 font=name_font, anchor="w").pack(anchor="w")

        status_row = tk.Frame(title_box, bg=PANEL)
        status_row.pack(anchor="w")
        dot = tk.Canvas(status_row, width=8, height=8, bg=PANEL, highlightthickness=0)
        dot.create_oval(1, 1, 7, 7, fill=ONLINE_DOT, outline="")
        dot.pack(side="left", pady=2)
        status_font = tkfont.Font(family=FONT_FAMILY, size=9)
        tk.Label(status_row, text="  Online  •  Rule-based AI", bg=PANEL, fg=TEXT_MUTED,
                 font=status_font).pack(side="left")

        # Clear button
        clear_font = tkfont.Font(family=FONT_FAMILY, size=9)
        clear_btn = tk.Label(
            header, text="⟲ Clear", bg=PANEL, fg=TEXT_MUTED,
            font=clear_font, cursor="hand2", padx=8, pady=4,
        )
        clear_btn.pack(side="right", padx=16)
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(fg=ACCENT))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(fg=TEXT_MUTED))
        clear_btn.bind("<Button-1>", lambda e: self._clear_chat())

    def _build_chat_area(self):
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(
            container, orient="vertical", command=self.canvas.yview,
            troughcolor=SCROLLBAR_BG, bg=SCROLLBAR_FG, width=6,
            relief="flat", bd=0, highlightthickness=0,
        )
        self.scroll_frame = tk.Frame(self.canvas, bg=BG)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_quick_replies(self):
        """Build the quick-reply chip bar. Safe to call multiple times."""
        # Create chip_bar only if it doesn't exist yet
        if not hasattr(self, 'chip_bar') or not self.chip_bar.winfo_exists():
            self.chip_bar = tk.Frame(self, bg=BG)
            self.chip_bar.pack(fill="x", padx=8, pady=(4, 4))

        # Clear existing chips
        for widget in self.chip_bar.winfo_children():
            widget.destroy()

        # Top border line above chips
        separator = tk.Frame(self.chip_bar, bg=SEPARATOR, height=1)
        separator.pack(fill="x", pady=(0, 6))

        # Chip container with wrapping
        chip_container = tk.Frame(self.chip_bar, bg=BG)
        chip_container.pack(fill="x")

        suggestions = [
            ("👋 Hello", "Hello"),
            ("😊 How are you?", "How are you?"),
            ("😂 Joke", "Tell me a joke"),
            ("🧠 Riddle", "Tell me a riddle"),
            ("💡 Fact", "Tell me a fact"),
            ("📋 Help", "Help"),
        ]
        for display_text, send_text in suggestions:
            self._make_chip(chip_container, display_text, send_text)

    def _make_chip(self, parent, display_text, send_text):
        chip_font = tkfont.Font(family=FONT_FAMILY, size=9)

        # Border frame
        chip_border = tk.Frame(parent, bg=CHIP_BORDER)
        chip_border.pack(side="left", padx=3, pady=2)

        chip = tk.Label(
            chip_border, text=display_text, bg=CHIP_BG, fg=TEXT_MEDIUM,
            font=chip_font, padx=10, pady=5, cursor="hand2",
        )
        chip.pack(padx=1, pady=1)

        chip.bind("<Enter>", lambda e: (
            chip.config(bg=CHIP_BG_HOVER, fg=TEXT_LIGHT),
            chip_border.config(bg=ACCENT),
        ))
        chip.bind("<Leave>", lambda e: (
            chip.config(bg=CHIP_BG, fg=TEXT_MEDIUM),
            chip_border.config(bg=CHIP_BORDER),
        ))
        chip.bind("<Button-1>", lambda e, t=send_text: self._send_quick(t))

    def _send_quick(self, text):
        self._handle_user_message(text)

    def _build_input_bar(self):
        # Top border
        border = tk.Frame(self, bg=PANEL_BORDER, height=1)
        border.pack(fill="x", side="bottom")

        bar = tk.Frame(self, bg=PANEL, height=68)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        # Inner container with padding
        inner = tk.Frame(bar, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        # Entry field with placeholder
        entry_font = tkfont.Font(family=FONT_FAMILY, size=11)
        self.entry = PlaceholderEntry(
            inner,
            placeholder="Type a message...",
            font=entry_font,
            bg=INPUT_BG,
            fg=TEXT_LIGHT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=PANEL_BORDER,
            highlightcolor=ACCENT,
        )
        self.entry.pack(side="left", fill="both", expand=True, ipady=8)
        self.entry.bind("<Return>", lambda e: self._on_send())
        self.entry.focus_set()

        # Spacer
        tk.Frame(inner, bg=PANEL, width=8).pack(side="left")

        # Send button with hover/press states
        send_font = tkfont.Font(family=FONT_FAMILY, size=11, weight="bold")
        self.send_btn = tk.Label(
            inner, text="  Send  ➤  ", bg=ACCENT, fg=TEXT_ON_USER,
            font=send_font, padx=14, pady=8, cursor="hand2",
        )
        self.send_btn.pack(side="right")
        self.send_btn.bind("<Button-1>", lambda e: self._on_send())
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.config(bg=ACCENT_HOVER))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg=ACCENT))
        self.send_btn.bind("<ButtonPress-1>", lambda e: self.send_btn.config(bg=ACCENT_PRESSED))
        self.send_btn.bind("<ButtonRelease-1>", lambda e: self.send_btn.config(bg=ACCENT_HOVER))

    # -- chat behaviour -------------------------------------------------
    def _timestamp(self):
        return datetime.now().strftime("%I:%M %p")

    def _add_bubble(self, text, sender):
        bubble = ChatBubble(self.scroll_frame, text, sender, self._timestamp())
        bubble.pack(fill="x", expand=True, pady=1)
        self._message_count += 1
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _on_send(self):
        text = self.entry.get_text()
        if not text:
            return
        self.entry.clear()
        self._handle_user_message(text)

    def _handle_user_message(self, text):
        self._add_bubble(text, "user")

        # Show animated typing indicator, then reply after a short delay
        self._typing_widget = TypingIndicator(self.scroll_frame)
        self._typing_widget.pack(fill="x", expand=True, pady=2)
        self._scroll_to_bottom()

        should_exit = is_exit_command(text)
        delay = 500 + min(len(text) * 15, 600)  # variable delay based on message length
        self.after(delay, lambda: self._bot_reply(text, should_exit))

    def _bot_reply(self, original_text, should_exit):
        if self._typing_widget is not None:
            self._typing_widget.stop()
            self._typing_widget.destroy()
            self._typing_widget = None

        try:
            reply = get_response(original_text)
        except Exception:
            reply = "Oops! Something went wrong on my end. Try again? 🔧"

        self._bot_say(reply)

        if should_exit:
            self.entry.config(state="disabled")
            self.send_btn.config(bg=TEXT_MUTED, cursor="arrow")
            self.send_btn.unbind("<Button-1>")
            self.send_btn.unbind("<Enter>")
            self.send_btn.unbind("<Leave>")
            self.send_btn.unbind("<ButtonPress-1>")
            self.send_btn.unbind("<ButtonRelease-1>")
            self.after(1200, self._show_restart_chip)

    def _bot_say(self, text):
        self._add_bubble(text, "bot")

    def _show_restart_chip(self):
        for widget in self.chip_bar.winfo_children():
            widget.destroy()
        self._make_restart_chip()

    def _make_restart_chip(self):
        chip_font = tkfont.Font(family=FONT_FAMILY, size=10, weight="bold")

        # Border frame
        chip_border = tk.Frame(self.chip_bar, bg=ACCENT)
        chip_border.pack(side="left", padx=4, pady=6)

        chip = tk.Label(
            chip_border, text="  ⟲  Start New Chat  ", bg=ACCENT, fg=TEXT_ON_USER,
            font=chip_font, padx=12, pady=6, cursor="hand2",
        )
        chip.pack(padx=1, pady=1)
        chip.bind("<Enter>", lambda e: chip.config(bg=ACCENT_HOVER))
        chip.bind("<Leave>", lambda e: chip.config(bg=ACCENT))
        chip.bind("<Button-1>", lambda e: self._clear_chat())

    def _clear_chat(self):
        # Clear all messages from chat area
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Re-enable input
        self.entry.config(state="normal")
        self.entry._has_placeholder = False  # Reset placeholder state

        # Re-enable send button
        self.send_btn.config(bg=ACCENT, cursor="hand2")
        self.send_btn.bind("<Button-1>", lambda e: self._on_send())
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.config(bg=ACCENT_HOVER))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg=ACCENT))
        self.send_btn.bind("<ButtonPress-1>", lambda e: self.send_btn.config(bg=ACCENT_PRESSED))
        self.send_btn.bind("<ButtonRelease-1>", lambda e: self.send_btn.config(bg=ACCENT_HOVER))

        # Reset message count
        self._message_count = 0

        # Rebuild chips (reuses existing chip_bar, no duplicate)
        self._build_quick_replies()

        # Show welcome message
        self.after(200, lambda: self._bot_say("New chat started! Ask me anything 🚀"))


def main():
    app = ChatbotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
