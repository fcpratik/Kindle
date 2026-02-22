# 📖 Kindle AI Explainer

A lightweight Windows desktop tool that explains confusing sentences from your Kindle app instantly — powered by **Groq AI (free)** and **Llama 3**.

---

## ✨ How It Works

1. Select a confusing sentence in the Kindle app
2. Press **Ctrl+C** to copy it
3. Press **Ctrl+Shift+E** (hotkey)
4. A popup appears in the bottom-right corner with a clear, simple explanation!

The app runs silently in your system tray and is always ready while you read.

---

## 🚀 Setup Guide

### Step 1 — Install Python
Make sure you have Python 3.8+ installed. Download from [python.org](https://www.python.org/downloads/) if needed.

### Step 2 — Install Dependencies
Open a terminal and run:
```
pip install groq pyperclip keyboard pystray pillow
```

### Step 3 — Get a Free Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign in with your Google account
3. Click **API Keys → Create API Key**
4. Copy the key

### Step 4 — Add Your API Key
Open `kindle_explainer.py` and find this line near the top:
```python
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_API_KEY_HERE")
```
Replace `YOUR_API_KEY_HERE` with your actual key:
```python
GROQ_API_KEY = "gsk_your_actual_key_here"
```

### Step 5 — Run the App
```
python kindle_explainer.py
```
You'll see a confirmation in the terminal and a small icon in your system tray.

---

## 🎮 Usage

| Action | What to do |
|---|---|
| **Explain a sentence** | Select text in Kindle → Ctrl+C → Ctrl+Shift+E |
| **Close the popup** | Click the ✕ button on the popup |
| **Stop the app** | Right-click system tray icon → Quit |
| **Stop in VS Code** | Click terminal → Ctrl+C |

---

## ⚙️ Configuration

You can customize these settings at the top of `kindle_explainer.py`:

```python
GROQ_API_KEY = "your_key"              # Your Groq API key
HOTKEY = "ctrl+shift+e"               # Change to any hotkey you prefer
GROQ_MODEL = "llama-3.3-70b-versatile" # AI model to use
```

---

## 🆓 Free Tier Limits

Groq's free tier is very generous for reading use:
- **6,000 requests per day**
- Resets every 24 hours
- No credit card required

---

## 🛠️ Tech Stack

- **Python** — core language
- **Groq API** — free AI inference
- **Llama 3.3 70B** — the AI model doing the explaining
- **Tkinter** — popup window UI
- **keyboard** — global hotkey listener
- **pyperclip** — clipboard access
- **pystray** — system tray icon
- **Pillow** — tray icon image

---

## ❓ Troubleshooting

**"API key not valid" error**
→ Double-check you pasted the full key correctly with no extra spaces.

**Hotkey not working**
→ Make sure the script is running (check your system tray). Try running VS Code as Administrator.

**Popup shows old clipboard content**
→ Always press Ctrl+C first to copy the new text, then press the hotkey.

**App won't stop**
→ Right-click the tray icon → Quit, then Ctrl+C in the terminal.

---

## 📌 Notes

- Works with the **Kindle for PC** desktop app
- The popup always stays on top of Kindle so you don't lose your place
- Explanations are kept short and simple (2-3 sentences)