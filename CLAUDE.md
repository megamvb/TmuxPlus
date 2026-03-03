# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TmuxPlus is a visual TUI manager for tmux built with Python's **Textual** framework and **libtmux** for tmux control.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
```

There is no test suite, linter, or build system configured.

## Architecture

**Entry flow**: `main.py` → `app.py (TmuxPlusApp)` → `screens/home.py (HomeScreen)`

`main.py` runs the app in a loop — when the user attaches to a tmux session, the app exits with a `tmux attach` command string, executes it via subprocess, and reopens TmuxPlus on detach.

### Layers

- **`app.py`** — Textual `App` subclass. Creates a single `TmuxService` instance shared across all screens.
- **`services/tmux_service.py`** — Stateless service with all tmux operations. Uses lazy `libtmux.Server` initialization. All methods return dataclasses (`SessionInfo`, `WindowInfo`, `PaneInfo`) or `None`/`False` on failure. Persistence saves sessions as JSON to `~/.config/tmuxplus/sessions/`.
- **`screens/`** — Textual `Screen` subclasses. Each screen receives `TmuxService` via constructor. Navigation uses `push_screen`/`pop_screen`. Modals (`InputModal`, `ConfirmModal`) are defined in `sessions.py` and reused.
- **`styles/app.tcss`** — Textual CSS for all screens and widgets.
- **`widgets/`** — Custom widget directory (currently empty).

### Key Patterns

- All `TmuxService` methods wrap operations in `try/except` and return `None`/`False` on error — no exceptions propagate to screens.
- Layout capture/restore uses `subprocess.run(["tmux", ...])` directly (not libtmux) since libtmux doesn't expose layout strings reliably.
- Screen actions map to both keyboard bindings and buttons (e.g., `s` key and `[s] Salvar` button both trigger `action_save_session`).

## Dependencies

- **textual** (>=0.50.0) — TUI framework (screens, widgets, CSS styling, key bindings)
- **libtmux** (>=0.25.0) — Python tmux control (Server, Session, Window, Pane objects)
