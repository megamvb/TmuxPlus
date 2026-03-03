"""TmuxPlus home screen."""

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static
from textual import work

from i18n import t
from services.tmux_service import TmuxService


class StatusBar(Static):
    """Status bar showing live tmux info."""

    def __init__(self, tmux: TmuxService) -> None:
        super().__init__()
        self.tmux = tmux

    def on_mount(self) -> None:
        self.update_status()

    @work(thread=True)
    def update_status(self) -> None:
        sessions = self.tmux.list_sessions()
        total_windows = sum(s.windows for s in sessions)
        attached = sum(1 for s in sessions if s.attached)
        saved = self.tmux.list_saved_sessions()
        saved_count = len(saved)
        saved_part = f"  |  {t('Saved:')} [bold magenta]{saved_count}[/]" if saved_count else ""
        text = (
            f" {t('Sessions:')} [bold cyan]{len(sessions)}[/]  |"
            f"  {t('Attached:')} [bold green]{attached}[/]  |"
            f"  {t('Windows:')} [bold yellow]{total_windows}[/]"
            f"{saved_part} "
        )
        self.app.call_from_thread(self.update, text)


class HomeScreen(Screen):
    """Main menu screen."""

    BINDINGS = [
        ("1", "go_sessions", t("Sessions")),
        ("2", "go_windows", t("Windows")),
        ("3", "go_panes", t("Panes")),
        ("q", "quit_app", t("Quit")),
    ]

    def __init__(self, tmux: TmuxService) -> None:
        super().__init__()
        self.tmux = tmux

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Vertical(id="menu-container"):
                yield Label(
                    "[bold cyan]TmuxPlus[/bold cyan]", id="app-title"
                )
                yield Label(
                    t("Visual manager for tmux"),
                    id="app-subtitle",
                )
                yield Button(
                    f"[1]  {t('Sessions')}",
                    id="btn-sessions",
                    variant="primary",
                )
                yield Button(
                    f"[2]  {t('Windows')}",
                    id="btn-windows",
                    variant="primary",
                )
                yield Button(
                    f"[3]  {t('Panes')}",
                    id="btn-panes",
                    variant="primary",
                )
                yield Button(
                    f"[?]  {t('Help')}",
                    id="btn-help",
                    variant="default",
                )
                yield Button(
                    f"[q]  {t('Quit')}",
                    id="btn-quit",
                    variant="error",
                )
                yield StatusBar(self.tmux)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_actions = {
            "btn-sessions": self.action_go_sessions,
            "btn-windows": self.action_go_windows,
            "btn-panes": self.action_go_panes,
            "btn-help": self.action_show_help,
            "btn-quit": self.action_quit_app,
        }
        action = button_actions.get(event.button.id or "")
        if action:
            action()

    def action_go_sessions(self) -> None:
        from screens.sessions import SessionsScreen
        self.app.push_screen(SessionsScreen(self.tmux))

    def action_go_windows(self) -> None:
        from screens.windows import WindowsScreen
        self.app.push_screen(WindowsScreen(self.tmux))

    def action_go_panes(self) -> None:
        from screens.panes import PanesScreen
        self.app.push_screen(PanesScreen(self.tmux))

    def action_show_help(self) -> None:
        from screens.help import HelpModal
        self.app.push_screen(HelpModal())

    def action_quit_app(self) -> None:
        self.app.exit()
