# TmuxPlus

Visual TUI manager for **tmux**, built with [Textual](https://textual.textualize.io/) and [libtmux](https://libtmux.git-pull.com/).

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)

![TmuxPlus](TmuxPlus.png)

> **[Leia em Português](README-PT.md)**

## Features

- Full management of tmux **sessions**, **windows**, and **panes**
- Save and restore session layouts (JSON persistence)
- Command palette (Ctrl+P) for quick access
- Switchable themes (Ctrl+T) — Dracula, Monokai, Gruvbox, Nord, Tokyo Night and more
- Portuguese (pt-BR) interface with internationalization support
- Auto-reconnect — after detaching (Ctrl+B, D), TmuxPlus reopens automatically

## Installation

### Quick

```bash
bash install.sh
```

### Manual

```bash
git clone https://github.com/megamvb/TmuxPlus.git
cd TmuxPlus
pip install -r requirements.txt
python3 main.py
```

## Dependencies

- Python 3.10+
- tmux
- [textual](https://pypi.org/project/textual/) >= 0.50.0
- [libtmux](https://pypi.org/project/libtmux/) >= 0.25.0

## Usage

```bash
python3 main.py          # start
python3 main.py --log    # start with file logging
```

### Key Bindings

| Key        | Action                  |
|------------|-------------------------|
| `Ctrl+Q`   | Quit                   |
| `Ctrl+T`   | Toggle theme           |
| `?`         | Help                   |
| `Ctrl+P`   | Command palette        |

## Project Structure

```
TmuxPlus/
├── main.py                # Entry point — attach/detach loop
├── app.py                 # Textual App, command palette, themes
├── screens/               # Screens (Home, Sessions, Windows, Panes, Help)
├── services/              # TmuxService — tmux operations via libtmux
├── widgets/               # Custom widgets
├── styles/app.tcss        # Textual CSS
├── i18n/                  # Internationalization
├── install.sh             # Install script
└── requirements.txt
```

## License

[MIT](LICENSE)
