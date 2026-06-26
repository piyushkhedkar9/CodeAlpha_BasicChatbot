# RuleBot — Simple Rule-Based Chatbot

A rule-based chatbot built with core Python concepts: **functions**,
**if/elif/else**, **loops**, and **input/output**. Comes with two front ends:

| File                | What it is                                              |
|---------------------|----------------------------------------------------------|
| `chatbot_logic.py`  | The **backend** — all matching rules and reply logic.   |
| `cli_chatbot.py`    | Plain terminal version (pure `input()` / `print()`).     |
| `gui_chatbot.py`    | Polished desktop **GUI** with chat bubbles, quick replies, typing indicator, and dark theme — built with Tkinter (already included with Python, no installs needed). |

## Requirements
Just Python 3.8+. No pip installs needed — everything used (`tkinter`,
`random`, `re`, `datetime`) ships with the standard library.

> If `tkinter` isn't installed on your system (rare on Windows/macOS, occasionally
> missing on minimal Linux installs), install it with:
> - Ubuntu/Debian: `sudo apt-get install python3-tk`
> - Fedora: `sudo dnf install python3-tkinter`
> - macOS/Windows: comes bundled with the official python.org installer.

## How to run

**Terminal version:**
```bash
python cli_chatbot.py
```

**GUI version (recommended — this is the polished one):**
```bash
python gui_chatbot.py
```

## What you can say
- Greetings: `hello`, `hi`, `hey`
- `how are you`
- `what's your name`
- `tell me a joke`
- `what time is it`
- `help`
- `thanks`
- `bye` / `exit` / `quit` — ends the conversation

Anything that doesn't match a rule gets a friendly fallback reply asking
you to rephrase.

## How the rule-matching works
`chatbot_logic.py` keeps a list of **rules**, each with a tag, a list of
trigger keywords, and a list of possible replies (a random one is picked
each time, so it doesn't sound robotic on repeat runs). Matching uses
word-boundary–aware substring search (via `re`) so short keywords like
"hi" don't accidentally match inside unrelated words like "this" or "your".

```
RULES = [
    {"tag": "greeting", "keywords": ["hello", "hi", "hey", ...], "responses": [...]},
    {"tag": "bye",      "keywords": ["bye", "goodbye", "exit", ...], "responses": [...]},
    ...
]
```

To add a new topic, just add a new dict to `RULES` — no other code changes
needed.

## GUI design notes
The GUI deliberately avoids default Tk gray: it uses a dark slate
background (`#1B1E26`) with a single warm amber accent (`#E8A33D`),
rounded-looking message bubbles (bot on the left, user on the right —
the messaging-app pattern everyone already knows), an animated
"typing…" indicator before each bot reply, and tappable quick-reply chips
so the interface invites interaction immediately. When the user says
bye/exit/quit, the input disables and a "Start new chat" chip appears.
