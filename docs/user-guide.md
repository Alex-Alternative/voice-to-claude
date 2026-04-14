# Koda User Guide
**Version 4.2.0**

---

## What is Koda?

Koda is a push-to-talk voice transcription tool for Windows. Press a hotkey, speak, and your words are instantly typed into whatever you're working in — emails, Slack, Word, Excel, ChatGPT, anything.

No clicking a mic button. No switching apps. Just talk.

---

## Installation

1. Double-click **KodaSetup-4.2.0.exe**
2. If Windows shows a "protected your PC" warning, click **More info → Run anyway**
3. Follow the installer wizard
4. Koda launches automatically when installation completes

Koda appears as a small icon in your **system tray** (bottom-right corner of your screen, near the clock). That's how you know it's running.

---

## Basic Usage

### Dictation — type by speaking

| Action | What to do |
|--------|-----------|
| Start recording | Hold **Ctrl + Space** |
| Speak | Talk naturally while holding |
| Paste transcription | Release **Ctrl + Space** |

Your words appear in whatever app or field was active when you pressed the hotkey.

**Tips:**
- Speak at a normal pace — no need to slow down
- Works in emails, Slack, Word, Excel, browsers, chat apps — anything
- A quiet room gives better accuracy than a great microphone
- Built-in laptop mic works fine. A USB headset is better.

---

## Other Hotkeys

| Hotkey | What it does |
|--------|-------------|
| **Ctrl + Space** | Hold to dictate, release to paste |
| **F9** | Prompt Assist — speak an idea, get a structured prompt ready to paste into ChatGPT or Claude |
| **F7** | Correction — re-transcribes your last recording if it came out wrong |
| **F6** | Read back — Koda reads your last transcription aloud |

---

## System Tray Menu

Right-click the Koda tray icon for options:

- **Settings** — change hotkeys, microphone, model quality, and more
- **History** — see your recent transcriptions
- **Pause / Resume** — temporarily disable Koda
- **Quit** — close Koda

---

## Settings

Open Settings by right-clicking the tray icon → **Settings**.

| Setting | What it does |
|---------|-------------|
| Hotkey mode | **Hold** (default) — hold key while speaking. **Toggle** — press once to start, again to stop |
| Model quality | **Fast** (tiny), **Balanced** (base, default), **Accurate** (small) |
| Microphone | Choose which mic Koda listens to |
| Remove filler words | Automatically removes "um", "uh", "like" from transcriptions |
| Sound effects | Audio cues when recording starts and stops |

---

## Microphone Tips

You don't need an expensive mic. Here's what to expect:

| Microphone | Quality | Notes |
|-----------|---------|-------|
| Built-in laptop mic | Good | Works well in a quiet room |
| USB headset / earbuds | Better | Recommended (~$20–40) |
| Dedicated USB mic | Best | Blue Yeti, HyperX (~$60–100) |

**The biggest factor is a quiet environment** — background noise matters more than mic quality.

Make sure your microphone is set as the **default recording device** in Windows:
> Right-click the speaker icon → Sound settings → Choose your input device

---

## Formula Mode (Excel & Google Sheets)

Koda can convert spoken descriptions into Excel / Google Sheets formulas. Enable it in **Settings → Formula mode**.

When formula mode is on and you're in Excel or Google Sheets, speak naturally and Koda types the formula for you:

| What you say | What Koda types |
|---|---|
| sum B2 to B10 | `=SUM(B2:B10)` |
| average of A1 to A20 | `=AVERAGE(A1:A20)` |
| max of C1 to C20 | `=MAX(C1:C20)` |
| today | `=TODAY()` |
| if A1 is greater than 10 then yes else no | `=IF(A1>10,"yes","no")` |
| vlookup A1 in B1 to D10 column 2 | `=VLOOKUP(A1,B1:D10,2,0)` |
| count B2 to B10 | `=COUNT(B2:B10)` |

**If your phrase doesn't match a formula pattern**, Koda pastes the transcription as normal text — so regular dictation in Excel still works.

**For complex formulas**, install [Ollama](https://ollama.com) (free, local AI) and enable **LLM Polish** in Settings. Run `ollama pull phi3:mini` once to set it up.

---

## Troubleshooting

**Koda isn't pasting anything**
- Make sure you're clicking into the text field first before pressing the hotkey
- Check the tray icon is green (running), not paused

**Hotkeys stopped working**
- Right-click tray icon → Quit, then relaunch Koda
- This is rare — Koda automatically recovers from most hotkey issues

**Transcription is inaccurate**
- Try the **Accurate** model in Settings (slower but more precise)
- Reduce background noise
- Speak closer to the mic

**"No microphone detected"**
- Plug in your mic before launching Koda
- Set it as the default recording device in Windows Sound Settings

---

## Uninstalling

Go to **Windows Settings → Apps → Installed apps**, find **Koda**, and click **Uninstall**.

---

## Need Help?

Contact: alex@kodaspeak.com
