
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

6. To STOP the app: press Ctrl+Shift+Q  OR  right-click tray icon → Quit
"""

import os
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext, font, messagebox
import keyboard
import pyperclip
from groq import Groq
from PIL import Image, ImageDraw
import pystray

# ─────────────────────────────────────────
#  CONFIGURATION — paste your Groq API key here
# ─────────────────────────────────────────

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_API_KEY_HERE")
HOTKEY = "ctrl+shift+e"                    # Hotkey to explain selected text
KILL_HOTKEY = "ctrl+shift+q"              # Hotkey to stop the app
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
#  Queue — hotkey thread sends tasks to main thread
# ─────────────────────────────────────────
task_queue = queue.Queue()


# ─────────────────────────────────────────
#  Explanation Popup Window (always runs on main thread)
# ─────────────────────────────────────────
class ExplainerPopup:
    def __init__(self):
        self.window = None

    def open(self, selected_text):
        """Open popup window — must be called from main thread."""
        if self.window:
            try:
                self.window.destroy()
            except:
                pass
            self.window = None

        win = tk.Toplevel()
        self.window = win
        win.title("📖 Kindle Explainer")
        win.geometry("520x380")
        win.resizable(True, True)
        win.configure(bg="#1e1e2e")
        win.attributes("-topmost", True)
        win.protocol("WM_DELETE_WINDOW", self.close)

        # Position: bottom-right corner
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        win.geometry(f"520x380+{screen_w - 540}+{screen_h - 420}")

        header_font = font.Font(family="Segoe UI", size=10, weight="bold")
        body_font = font.Font(family="Segoe UI", size=11)
        small_font = font.Font(family="Segoe UI", size=9)

        # Header
        header = tk.Frame(win, bg="#313244", pady=8, padx=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="📖 AI Explainer  •  Groq (Llama 3)",
                 font=header_font, bg="#313244", fg="#cdd6f4").pack(side=tk.LEFT)
        tk.Button(header, text="✕", command=self.close,
                  font=small_font, bg="#313244", fg="#f38ba8",
                  relief=tk.FLAT, cursor="hand2", padx=6).pack(side=tk.RIGHT)

        # Selected text
        tk.Label(win, text="Selected text:", font=small_font,
                 bg="#1e1e2e", fg="#6c7086").pack(anchor=tk.W, padx=12, pady=(10, 2))
        selected_box = tk.Text(win, height=3, wrap=tk.WORD, font=body_font,
                               bg="#181825", fg="#bac2de", relief=tk.FLAT, padx=8, pady=6)
        selected_box.pack(fill=tk.X, padx=12)
        selected_box.insert(tk.END, selected_text.strip())
        selected_box.config(state=tk.DISABLED)

        # Explanation
        tk.Label(win, text="Explanation:", font=small_font,
                 bg="#1e1e2e", fg="#6c7086").pack(anchor=tk.W, padx=12, pady=(12, 2))
        self.explanation_box = scrolledtext.ScrolledText(
            win, wrap=tk.WORD, font=body_font,
            bg="#181825", fg="#cdd6f4", relief=tk.FLAT, padx=10, pady=8)
        self.explanation_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.explanation_box.insert(tk.END, "⏳ Asking Groq...")
        self.explanation_box.config(state=tk.DISABLED)

        # Fetch explanation in background thread
        threading.Thread(target=self._fetch, args=(selected_text,), daemon=True).start()

    def _fetch(self, text):
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
            result = f"❌ Error: {str(e)}"

        # Send result back to main thread via queue
        task_queue.put(("update_explanation", result))

    def update_explanation(self, text):
        if self.window and self.explanation_box:
            self.explanation_box.config(state=tk.NORMAL)
            self.explanation_box.delete("1.0", tk.END)
            self.explanation_box.insert(tk.END, text)
            self.explanation_box.config(state=tk.DISABLED)

    def close(self):
        if self.window:
            try:
                self.window.destroy()
            except:
                pass
            self.window = None


# ─────────────────────────────────────────
#  Hotkey Handlers (run in hotkey thread, push to queue)
# ─────────────────────────────────────────
def on_explain_hotkey():
    import time
    time.sleep(0.1)
    text = pyperclip.paste().strip()
    if not text:
        task_queue.put(("error", "No text copied!\nSelect text in Kindle → Ctrl+C first, then Ctrl+Shift+E."))
        return
    if len(text) > 2000:
        text = text[:2000] + "..."
    task_queue.put(("show_popup", text))


def on_kill_hotkey():
    task_queue.put(("quit", None))


# ─────────────────────────────────────────
#  System Tray
# ─────────────────────────────────────────
def create_tray_icon():
    img = Image.new("RGB", (64, 64), color="#1e1e2e")
    draw = ImageDraw.Draw(img)
    draw.ellipse([6, 6, 58, 58], fill="#a6e3a1")
    draw.text((18, 18), "AI", fill="#1e1e2e")
    return img


def run_tray():
    def on_quit(icon, item):
        task_queue.put(("quit", None))
        icon.stop()

    icon = pystray.Icon(
        "KindleExplainer",
        create_tray_icon(),
        "Kindle AI Explainer",
        pystray.Menu(
            pystray.MenuItem(f"Explain: {HOTKEY.upper()}", lambda: None, enabled=False),
            pystray.MenuItem(f"Quit: {KILL_HOTKEY.upper()}", lambda: None, enabled=False),
            pystray.MenuItem("Quit", on_quit)
        )
    )
    threading.Thread(target=icon.run, daemon=True).start()
    return icon


# ─────────────────────────────────────────
#  Main Loop (tkinter + queue on main thread)
# ─────────────────────────────────────────
if __name__ == "__main__":
    if GROQ_API_KEY == "YOUR_API_KEY_HERE":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "API Key Missing",
            "Please open kindle_explainer.py and set your GROQ_API_KEY.\n\n"
            "Get a FREE key at: https://console.groq.com\n\n"
            "Or set as environment variable:\n"
            "set GROQ_API_KEY=your_key_here"
        )
        root.destroy()
        exit(1)

    # Hidden main tkinter window (needed to host Toplevel popups)
    root = tk.Tk()
    root.withdraw()

    popup = ExplainerPopup()

    # Register hotkeys
    keyboard.add_hotkey(HOTKEY, on_explain_hotkey)
    keyboard.add_hotkey(KILL_HOTKEY, on_kill_hotkey)

    # Start tray icon in background thread
    tray = run_tray()

    print("✅ Kindle Explainer running! (Powered by Groq)")
    print(f"📌 Explain hotkey : {HOTKEY.upper()}")
    print(f"🔴 Quit hotkey    : {KILL_HOTKEY.upper()}")
    print("📋 Steps: Select text in Kindle → Ctrl+C → Ctrl+Shift+E\n")

    # Main loop — process tasks from queue, keep tkinter alive
    def process_queue():
        try:
            while True:
                task, data = task_queue.get_nowait()
                if task == "show_popup":
                    popup.open(data)
                elif task == "update_explanation":
                    popup.update_explanation(data)
                elif task == "error":
                    messagebox.showwarning("Kindle Explainer", data)
                elif task == "quit":
                    print("🔴 Shutting down Kindle Explainer...")
                    root.destroy()
                    os._exit(0)
        except queue.Empty:
            pass
        root.after(100, process_queue)  # Check queue every 100ms

    root.after(100, process_queue)
    root.mainloop()