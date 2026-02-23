"""
Kindle AI Explainer — Powered by Groq (Free)
----------------------------------------------
HOW TO USE:
1. Install dependencies:
   pip install groq pyperclip keyboard pystray pillow

2. Get a FREE Groq API key at: https://console.groq.com
   (Sign in with Google → API Keys → Create API Key)

3. Paste your key below where it says YOUR_API_KEY_HERE

4. Run: python kindle_explainer.py

5. In Kindle, select any confusing sentence → Ctrl+C → Ctrl+Shift+E
   A popup will appear with the explanation!
"""

import os
import threading
import tkinter as tk
from tkinter import scrolledtext, font
import keyboard
import pyperclip
from groq import Groq
from PIL import Image, ImageDraw
import pystray

# ─────────────────────────────────────────
#  CONFIGURATION — paste your Groq API key here
# ─────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_API")
HOTKEY = "ctrl+shift+e"                   
GROQ_MODEL = "llama-3.3-70b-versatile"    # Best free model on Groq

# ─────────────────────────────────────────
#  Groq Setup
# ─────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a reading assistant helping someone understand a sentence from a book.

When given a sentence or passage:
1. Explain it in simple, clear language (2-3 sentences max)
2. If there are difficult words, briefly define them
3. Give context if the meaning is figurative or idiomatic
4. Keep it concise — the reader just wants a quick understanding

Do NOT start with "This sentence means..." — just explain naturally."""


# ─────────────────────────────────────────
#  Explanation Popup Window
# ─────────────────────────────────────────
class ExplainerPopup:
    def __init__(self):
        self.root = None
        self.is_open = False

    def show(self, selected_text):
        """Show popup and fetch explanation in background."""
        if self.is_open:
            self.close()

        self.root = tk.Tk()
        self.root.title("📖 Kindle Explainer")
        self.root.geometry("520x380")
        self.root.resizable(True, True)
        self.root.configure(bg="#1e1e2e")
        self.root.attributes("-topmost", True)  # Always on top of Kindle
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # Position: bottom-right corner of screen
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"520x380+{screen_w - 540}+{screen_h - 420}")

        self._build_ui(selected_text)
        self.is_open = True
        self.root.mainloop()

    def _build_ui(self, selected_text):
        header_font = font.Font(family="Segoe UI", size=10, weight="bold")
        body_font = font.Font(family="Segoe UI", size=11)
        small_font = font.Font(family="Segoe UI", size=9)

        # Header
        header = tk.Frame(self.root, bg="#313244", pady=8, padx=12)
        header.pack(fill=tk.X)

        tk.Label(header, text="📖 AI Explainer  •  Groq (Llama 3)",
                 font=header_font, bg="#313244", fg="#cdd6f4").pack(side=tk.LEFT)

        tk.Button(header, text="✕", command=self.close,
                  font=small_font, bg="#313244", fg="#f38ba8",
                  relief=tk.FLAT, cursor="hand2", padx=6).pack(side=tk.RIGHT)

        # Selected sentence box
        tk.Label(self.root, text="Selected text:", font=small_font,
                 bg="#1e1e2e", fg="#6c7086").pack(anchor=tk.W, padx=12, pady=(10, 2))

        selected_box = tk.Text(self.root, height=3, wrap=tk.WORD,
                               font=body_font, bg="#181825", fg="#bac2de",
                               relief=tk.FLAT, padx=8, pady=6, state=tk.NORMAL)
        selected_box.pack(fill=tk.X, padx=12)
        selected_box.insert(tk.END, selected_text.strip())
        selected_box.config(state=tk.DISABLED)

        # Explanation label
        tk.Label(self.root, text="Explanation:", font=small_font,
                 bg="#1e1e2e", fg="#6c7086").pack(anchor=tk.W, padx=12, pady=(12, 2))

        # Explanation text area
        self.explanation_box = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=body_font,
            bg="#181825", fg="#cdd6f4", relief=tk.FLAT,
            padx=10, pady=8, state=tk.NORMAL
        )
        self.explanation_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.explanation_box.insert(tk.END, "⏳ Asking Groq...")
        self.explanation_box.config(state=tk.DISABLED)

        # Fetch in background so UI doesn't freeze
        thread = threading.Thread(target=self._fetch_explanation, args=(selected_text,), daemon=True)
        thread.start()

    def _fetch_explanation(self, text):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Sentence to explain:\n\"{text}\""}
                ],
                max_tokens=300,
                temperature=0.5,
            )
            result = response.choices[0].message.content.strip()
        except Exception as e:
            result = f"❌ Error: {str(e)}\n\nMake sure your GROQ_API_KEY is set correctly."

        # Update UI on main thread
        if self.root and self.is_open:
            self.root.after(0, self._update_explanation, result)

    def _update_explanation(self, text):
        self.explanation_box.config(state=tk.NORMAL)
        self.explanation_box.delete("1.0", tk.END)
        self.explanation_box.insert(tk.END, text)
        self.explanation_box.config(state=tk.DISABLED)

    def close(self):
        self.is_open = False
        if self.root:
            self.root.destroy()
            self.root = None


# ─────────────────────────────────────────
#  Hotkey Handler
# ─────────────────────────────────────────
popup = ExplainerPopup()

def on_hotkey():
    """Called when the user presses the hotkey."""
    import time
    time.sleep(0.1)  # Small delay to ensure clipboard is updated

    text = pyperclip.paste().strip()

    if not text:
        show_error_toast("No text copied!\nSelect text in Kindle → Ctrl+C first, then Ctrl+Shift+E.")
        return

    if len(text) > 2000:
        text = text[:2000] + "..."

    # Run popup in a new thread so hotkey listener doesn't block
    thread = threading.Thread(target=popup.show, args=(text,), daemon=True)
    thread.start()


def show_error_toast(msg):
    """Quick error notification."""
    def _show():
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        tk.messagebox.showwarning("Kindle Explainer", msg, parent=root)
        root.destroy()
    threading.Thread(target=_show, daemon=True).start()


# ─────────────────────────────────────────
#  System Tray Icon
# ─────────────────────────────────────────
def create_tray_icon():
    """Create a simple colored icon for the system tray."""
    img = Image.new("RGB", (64, 64), color="#1e1e2e")
    draw = ImageDraw.Draw(img)
    draw.ellipse([6, 6, 58, 58], fill="#a6e3a1")
    draw.text((18, 18), "AI", fill="#1e1e2e")
    return img


def run_tray():
    icon_image = create_tray_icon()

    def on_quit(icon, item):
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem(f"Hotkey: {HOTKEY.upper()}", lambda: None, enabled=False),
        pystray.MenuItem("Quit", on_quit)
    )

    icon = pystray.Icon("KindleExplainer", icon_image, "Kindle AI Explainer (Groq)", menu)
    icon.run()


# ─────────────────────────────────────────
#  Main
# ─────────────────────────────────────────
if __name__ == "__main__":
    import tkinter.messagebox

    if GROQ_API_KEY == "YOUR_API_KEY_HERE":
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror(
            "API Key Missing",
            "Please open kindle_explainer.py and set your GROQ_API_KEY.\n\n"
            "Get a FREE key at: https://console.groq.com\n\n"
            "Or set it as an environment variable:\n"
            "set GROQ_API_KEY=your_key_here"
        )
        root.destroy()
        exit(1)

    print("✅ Kindle Explainer running! (Powered by Groq)")
    print(f"📌 Hotkey: {HOTKEY.upper()}")
    print("📋 Steps: Select text in Kindle → Ctrl+C → Ctrl+Shift+E")
    print("🟢 Right-click tray icon to quit\n")

    # Register global hotkey
    keyboard.add_hotkey(HOTKEY, on_hotkey)

    def kill_app():
        print("\n🔴 Ctrl+D pressed — shutting down Kindle Explainer...")
        os._exit(0)

    keyboard.add_hotkey("ctrl+d", kill_app)
    print("🔴 Press Ctrl+D anytime to stop the app\n")
    # Run tray icon (blocking)
    run_tray()