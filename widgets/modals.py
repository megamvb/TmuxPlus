"""Reusable modal dialogs for TmuxPlus."""

import re
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, OptionList
from textual.widgets.option_list import Option

from i18n import t


class InputModal(ModalScreen[str]):
    """Text input modal."""

    def __init__(self, title: str, placeholder: str = "") -> None:
        super().__init__()
        self.title_text = title
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Vertical(id="input-dialog"):
            yield Label(self.title_text, id="input-title")
            yield Input(placeholder=self.placeholder, id="input-field")
            with Horizontal(id="input-buttons"):
                yield Button(t("Confirm"), variant="success", id="confirm")
                yield Button(t("Cancel"), variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            inp = self.query_one("#input-field", Input)
            self.dismiss(inp.value)
        else:
            self.dismiss("")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)


class ConfirmModal(ModalScreen[bool]):
    """Confirmation modal."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button(t("Yes"), variant="error", id="yes")
                yield Button(t("No"), variant="primary", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


class HistoryModal(ModalScreen[str]):
    """Modal that displays bash history for selection."""

    def __init__(self, history_path: str | None = None) -> None:
        super().__init__()
        self._history_path = history_path
        self._commands: list[str] = []
        self._filtered: list[str] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="history-dialog"):
            yield Label(t("Command History"), id="history-title")
            yield Input(placeholder=t("Filter commands..."), id="history-filter")
            yield OptionList(id="history-list")
            with Horizontal(id="history-buttons"):
                yield Button(t("Cancel"), variant="error", id="cancel")

    def on_mount(self) -> None:
        self._commands = self._load_history()
        self._filtered = self._commands
        self._populate_list()

    def _load_history(self) -> list[str]:
        """Load bash history, deduplicated, most recent first."""
        history_path = Path(self._history_path) if self._history_path else Path.home() / ".bash_history"
        if not history_path.exists():
            return []
        try:
            lines = history_path.read_text(errors="replace").splitlines()
        except OSError:
            return []
        seen: set[str] = set()
        result: list[str] = []
        for line in reversed(lines):
            cmd = line.strip()
            if cmd and cmd not in seen:
                seen.add(cmd)
                result.append(cmd)
        return result

    def _populate_list(self) -> None:
        option_list = self.query_one("#history-list", OptionList)
        option_list.clear_options()
        if self._filtered:
            for cmd in self._filtered:
                option_list.add_option(Option(cmd))
        else:
            option_list.add_option(Option(t("No commands found"), disabled=True))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "history-filter":
            query = event.value.lower()
            if query:
                self._filtered = [c for c in self._commands if query in c.lower()]
            else:
                self._filtered = self._commands
            self._populate_list()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.prompt)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss("")


class AliasModal(ModalScreen[str]):
    """Modal that displays shell aliases for selection."""

    _ALIAS_RE = re.compile(r"""^\s*alias\s+([\w.-]+)=(?:'([^']*)'|"([^"]*)"|(\S+))""")
    _SOURCE_RE = re.compile(r"""^\s*(?:source|\\.)\s+["']?([^"'#\s]+)["']?""")
    _SHELL_CONFIGS = [
        ".bashrc", ".zshrc", ".bash_aliases", ".zsh_aliases",
        ".profile", ".bash_profile", ".zprofile",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._aliases: list[tuple[str, str]] = []
        self._filtered: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="alias-dialog"):
            yield Label(t("Shell Aliases"), id="alias-title")
            yield Input(placeholder=t("Filter aliases..."), id="alias-filter")
            yield OptionList(id="alias-list")
            with Horizontal(id="alias-buttons"):
                yield Button(t("Cancel"), variant="error", id="cancel")

    def on_mount(self) -> None:
        self._aliases = self._load_aliases()
        self._filtered = self._aliases
        self._populate_list()

    def _expand_path(self, raw: str) -> Path | None:
        """Expand ~ and $HOME in a path."""
        expanded = raw.replace("$HOME", str(Path.home())).replace("~", str(Path.home()))
        p = Path(expanded)
        return p if p.is_file() else None

    def _parse_aliases_from_file(self, filepath: Path, visited: set[Path]) -> list[tuple[str, str]]:
        """Parse alias definitions from a file, following source directives."""
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
            m = self._ALIAS_RE.match(line)
            if m:
                name = m.group(1)
                command = m.group(2) or m.group(3) or m.group(4) or ""
                result.append((name, command))
                continue
            m = self._SOURCE_RE.match(line)
            if m:
                sourced = self._expand_path(m.group(1))
                if sourced:
                    result.extend(self._parse_aliases_from_file(sourced, visited))
        return result

    def _load_aliases(self) -> list[tuple[str, str]]:
        """Load shell aliases from config files, deduplicated."""
        visited: set[Path] = set()
        all_aliases: list[tuple[str, str]] = []
        for name in self._SHELL_CONFIGS:
            all_aliases.extend(self._parse_aliases_from_file(Path.home() / name, visited))
        seen: set[str] = set()
        deduplicated: list[tuple[str, str]] = []
        for alias_name, cmd in all_aliases:
            if alias_name not in seen:
                seen.add(alias_name)
                deduplicated.append((alias_name, cmd))
        return deduplicated

    def _populate_list(self) -> None:
        option_list = self.query_one("#alias-list", OptionList)
        option_list.clear_options()
        if self._filtered:
            for name, cmd in self._filtered:
                option_list.add_option(Option(f"{name} → {cmd}"))
        else:
            option_list.add_option(Option(t("No aliases found"), disabled=True))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "alias-filter":
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
        alias_name = prompt.split(" → ", 1)[0]
        self.dismiss(alias_name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss("")
