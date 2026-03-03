"""Help modal with essential tmux commands."""

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from i18n import t


TMUX_HELP_TEXT_EN = """\
[bold cyan]═══ Essential Tmux Commands ═══[/]

[bold yellow]Default prefix:[/] [bold white]Ctrl+B[/]  (all commands below use this prefix)

[bold green]── Sessions ─────────────────────────────────────[/]
[bold]Ctrl+B  s[/]       List sessions
[bold]Ctrl+B  $[/]       Rename current session
[bold]Ctrl+B  d[/]       Detach from session
[bold]Ctrl+B  ([/]       Previous session
[bold]Ctrl+B  )[/]       Next session

[bold green]── Windows ──────────────────────────────────────[/]
[bold]Ctrl+B  c[/]       Create new window
[bold]Ctrl+B  ,[/]       Rename current window
[bold]Ctrl+B  w[/]       List windows
[bold]Ctrl+B  n[/]       Next window
[bold]Ctrl+B  p[/]       Previous window
[bold]Ctrl+B  0-9[/]     Go to window by number
[bold]Ctrl+B  &[/]       Close current window

[bold green]── Panes ─────────────────────────────────────────[/]
[bold]Ctrl+B  %[/]       Split vertically
[bold]Ctrl+B  "[/]       Split horizontally
[bold]Ctrl+B  ←↑↓→[/]   Navigate between panes
[bold]Ctrl+B  x[/]       Close current pane
[bold]Ctrl+B  z[/]       Zoom (maximize/restore) pane
[bold]Ctrl+B  {[/]       Move pane left
[bold]Ctrl+B  }[/]       Move pane right
[bold]Ctrl+B  ![/]       Convert pane to window
[bold]Ctrl+B  Space[/]   Cycle pane layouts

[bold green]── Copy & Paste ──────────────────────────────────[/]
[bold]Ctrl+B  [[/]       Enter copy mode
[bold]Ctrl+B  ][/]       Paste buffer

[bold green]── Resize Panes ──────────────────────────────────[/]
[bold]Ctrl+B  Ctrl+←↑↓→[/]   Resize pane

[bold green]── Miscellaneous ─────────────────────────────────[/]
[bold]Ctrl+B  t[/]       Show clock
[bold]Ctrl+B  ?[/]       List all tmux shortcuts
[bold]Ctrl+B  :[/]       tmux command prompt
[bold]Ctrl+B  ~[/]       Show previous messages\
"""


class HelpModal(ModalScreen):
    """Full-size help modal with tmux command reference."""

    BINDINGS = [
        ("escape", "close", t("Close")),
        ("question_mark", "close", t("Close")),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="help-dialog"):
            yield Label(f"[bold cyan]{t('Help — Tmux Commands')}[/]", id="help-title")
            with VerticalScroll(id="help-scroll"):
                yield Static(t("TMUX_HELP_TEXT", TMUX_HELP_TEXT_EN), id="help-content")
            yield Button(f"[Esc] {t('Close')}", variant="primary", id="btn-help-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-help-close":
            self.dismiss()

    def action_close(self) -> None:
        self.dismiss()
