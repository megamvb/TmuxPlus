"""Standalone alias picker for use inside tmux display-popup."""

import re
import subprocess
import sys
from pathlib import Path


_ALIAS_RE = re.compile(r"""^\s*alias\s+([\w.-]+)=(?:'([^']*)'|"([^"]*)"|(\S+))""")
_SOURCE_RE = re.compile(r"""^\s*(?:source|\\.)\s+["']?([^"'#\s]+)["']?""")
_SHELL_CONFIGS = [
    ".bashrc", ".zshrc", ".bash_aliases", ".zsh_aliases",
    ".profile", ".bash_profile", ".zprofile",
]


def _expand_path(raw: str) -> Path | None:
    expanded = raw.replace("$HOME", str(Path.home())).replace("~", str(Path.home()))
    p = Path(expanded)
    return p if p.is_file() else None


def _parse_aliases_from_file(filepath: Path, visited: set[Path]) -> list[tuple[str, str]]:
    resolved = filepath.resolve()
    if resolved in visited:
        return []
    visited.add(resolved)
    if not filepath.exists():
        return []
    try:
        lines = filepath.read_text(errors="replace").splitlines()
    except OSError:
        return []
    result: list[tuple[str, str]] = []
    for line in lines:
        m = _ALIAS_RE.match(line)
        if m:
            name = m.group(1)
            command = m.group(2) or m.group(3) or m.group(4) or ""
            result.append((name, command))
            continue
        m = _SOURCE_RE.match(line)
        if m:
            sourced = _expand_path(m.group(1))
            if sourced:
                result.extend(_parse_aliases_from_file(sourced, visited))
    return result


def load_aliases() -> list[tuple[str, str]]:
    visited: set[Path] = set()
    all_aliases: list[tuple[str, str]] = []
    for name in _SHELL_CONFIGS:
        all_aliases.extend(_parse_aliases_from_file(Path.home() / name, visited))
    seen: set[str] = set()
    deduplicated: list[tuple[str, str]] = []
    for alias_name, cmd in all_aliases:
        if alias_name not in seen:
            seen.add(alias_name)
            deduplicated.append((alias_name, cmd))
    return deduplicated


from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option


class AliasPickerApp(App):
    """Mini app that shows filterable shell aliases inside a tmux popup."""

    CSS_PATH = "styles/alias_picker.tcss"

    BINDINGS = [
        ("escape", "quit", "Close"),
    ]

    def __init__(self, pane_id: str) -> None:
        super().__init__()
        self.pane_id = pane_id
        self.selected_alias: str | None = None
        self._aliases: list[tuple[str, str]] = []
        self._filtered: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-container"):
            yield Input(placeholder="Filter aliases...", id="picker-filter")
            yield OptionList(id="picker-list")

    def on_mount(self) -> None:
        self._aliases = load_aliases()
        self._filtered = self._aliases
        self._populate_list()

    def _populate_list(self) -> None:
        option_list = self.query_one("#picker-list", OptionList)
        option_list.clear_options()
        if self._filtered:
            for name, cmd in self._filtered:
                option_list.add_option(Option(f"{name} → {cmd}"))
        else:
            option_list.add_option(Option("No aliases found", disabled=True))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "picker-filter":
            query = event.value.lower()
            if query:
                self._filtered = [
                    (n, c) for n, c in self._aliases
                    if query in n.lower() or query in c.lower()
                ]
            else:
                self._filtered = self._aliases
            self._populate_list()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        prompt = str(event.option.prompt)
        self.selected_alias = prompt.split(" → ", 1)[0]
        self.exit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: alias_picker.py <pane_id>")
        sys.exit(1)
    pane_id = sys.argv[1]
    app = AliasPickerApp(pane_id)
    app.run()
    if app.selected_alias:
        subprocess.run(
            ["tmux", "send-keys", "-t", pane_id, app.selected_alias, "Enter"],
            timeout=5,
        )
