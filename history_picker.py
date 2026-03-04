"""Standalone history picker for use inside tmux display-popup."""

import subprocess
import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option

from services.tmux_service import TmuxService


class HistoryPickerApp(App):
    """Mini app that shows filterable command history inside a tmux popup."""

    CSS_PATH = "styles/history_picker.tcss"

    BINDINGS = [
        ("escape", "quit", "Close"),
    ]

    def __init__(self, pane_id: str) -> None:
        super().__init__()
        self.pane_id = pane_id
        self.selected_command: str | None = None
        self._commands: list[str] = []
        self._filtered: list[str] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-container"):
            yield Input(placeholder="Filter commands...", id="picker-filter")
            yield OptionList(id="picker-list")

    def on_mount(self) -> None:
        svc = TmuxService()
        svc.flush_pane_history(self.pane_id)
        histfile = svc.get_pane_histfile(self.pane_id)
        self._commands = self._load_history(histfile)
        self._filtered = self._commands
        self._populate_list()

    def _load_history(self, history_path: str) -> list[str]:
        """Load bash history, deduplicated, most recent first."""
        path = Path(history_path)
        if not path.exists():
            return []
        try:
            lines = path.read_text(errors="replace").splitlines()
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
        option_list = self.query_one("#picker-list", OptionList)
        option_list.clear_options()
        self._option_to_cmd = {}
        if self._filtered:
            for i, cmd in enumerate(self._filtered, 1):
                opt_id = f"cmd_{i}"
                self._option_to_cmd[opt_id] = cmd
                option_list.add_option(Option(f"{i:>4}  {cmd}", id=opt_id))
        else:
            option_list.add_option(Option("No commands found", disabled=True))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "picker-filter":
            query = event.value.lower()
            if query:
                self._filtered = [c for c in self._commands if query in c.lower()]
            else:
                self._filtered = self._commands
            self._populate_list()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        opt_id = str(event.option.id)
        self.selected_command = self._option_to_cmd.get(opt_id, "")
        self.exit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: history_picker.py <pane_id>")
        sys.exit(1)
    pane_id = sys.argv[1]
    app = HistoryPickerApp(pane_id)
    app.run()
    # Send keys AFTER the app exits (popup closes), so they reach the real pane
    if app.selected_command:
        subprocess.run(
            ["tmux", "send-keys", "-t", pane_id, app.selected_command, "Enter"],
            timeout=5,
        )
