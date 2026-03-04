"""TmuxPlus main application."""

import subprocess
from pathlib import Path

from textual.app import App
from textual.command import Hit, Hits, Provider

from i18n import t
from screens.home import HomeScreen
from services.tmux_service import TmuxService


class TmuxProvider(Provider):
    """Command palette with TmuxPlus commands."""

    async def search(self, query: str) -> Hits:
        commands = [
            (t("Sessions — Manage tmux sessions"), "go_sessions", t("Open sessions screen")),
            (t("Windows — Manage tmux windows"), "go_windows", t("Open windows screen")),
            (t("Panes — Manage tmux panes"), "go_panes", t("Open panes screen")),
            (t("Create Session"), "create_session", t("Create new tmux session")),
            (t("Help — tmux shortcuts"), "show_help", t("Show help")),
            (t("Toggle Theme"), "toggle_theme", t("Toggle between themes")),
            (t("Quit"), "quit", t("Exit TmuxPlus")),
        ]
        for name, action, help_text in commands:
            if query.lower() in name.lower():
                yield Hit(
                    1 if name.lower().startswith(query.lower()) else 2,
                    name,
                    help=help_text,
                    command=self._make_command(action),
                )

    def _make_command(self, action: str):
        async def command() -> None:
            self.app.action_custom_command(action)
        return command


THEME_CYCLE = ["textual-dark", "monokai", "dracula", "gruvbox", "textual-light", "nord", "solarized-light", "tokyo-night"]


class TmuxPlusApp(App):
    """TmuxPlus — visual manager for tmux."""

    TITLE = "TmuxPlus"
    SUB_TITLE = t("Visual manager for tmux")
    CSS_PATH = "styles/app.tcss"

    COMMANDS = {TmuxProvider}

    BINDINGS = [
        ("ctrl+q", "quit", t("Quit")),
        ("question_mark", "show_help", t("Help")),
        ("ctrl+t", "toggle_theme", t("Theme")),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.tmux = TmuxService()
        self._theme_index = 0

    def action_show_help(self) -> None:
        from screens.help import HelpModal
        self.push_screen(HelpModal())

    def action_toggle_theme(self) -> None:
        self._theme_index = (self._theme_index + 1) % len(THEME_CYCLE)
        self.theme = THEME_CYCLE[self._theme_index]
        self.notify(t("Theme: {theme}").format(theme=self.theme))

    def action_custom_command(self, action: str) -> None:
        if action == "go_sessions":
            from screens.sessions import SessionsScreen
            self.push_screen(SessionsScreen(self.tmux))
        elif action == "go_windows":
            from screens.windows import WindowsScreen
            self.push_screen(WindowsScreen(self.tmux))
        elif action == "go_panes":
            from screens.panes import PanesScreen
            self.push_screen(PanesScreen(self.tmux))
        elif action == "create_session":
            from screens.sessions import SessionsScreen
            self.push_screen(SessionsScreen(self.tmux))
        elif action == "show_help":
            self.action_show_help()
        elif action == "toggle_theme":
            self.action_toggle_theme()
        elif action == "quit":
            self.exit()

    def on_mount(self) -> None:
        self._register_tmux_keybindings()
        self.push_screen(HomeScreen(self.tmux))

    def _register_tmux_keybindings(self) -> None:
        """Register prefix + H/A to open history/alias picker popups."""
        base = Path(__file__).parent.resolve()
        history_script = base / "history_picker.py"
        alias_script = base / "alias_picker.py"
        try:
            # Use run-shell so tmux expands #{pane_id} at key-press time,
            # then passes the resolved value to display-popup.
            subprocess.run(
                [
                    "tmux", "bind-key", "H",
                    "run-shell",
                    f"tmux display-popup -E -w 80% -h 70% "
                    f"'python3 {history_script} #{{pane_id}}'",
                ],
                capture_output=True,
                timeout=5,
            )
            subprocess.run(
                [
                    "tmux", "bind-key", "A",
                    "run-shell",
                    f"tmux display-popup -E -w 80% -h 70% "
                    f"'python3 {alias_script} #{{pane_id}}'",
                ],
                capture_output=True,
                timeout=5,
            )
        except Exception:
            pass
