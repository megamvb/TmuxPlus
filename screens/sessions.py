"""Tmux session management screen."""

import shlex

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
)
from textual import work

from i18n import t
from services.tmux_service import TmuxService
from widgets.modals import ConfirmModal, InputModal


class SessionsScreen(Screen):
    """Tmux session management."""

    BINDINGS = [
        ("c", "create_session", t("Create")),
        ("r", "rename_session", t("Rename")),
        ("a", "attach_session", t("Attach")),
        ("k", "kill_session", t("Kill")),
        ("s", "save_session", t("Save")),
        ("l", "load_session", t("Load")),
        ("escape", "go_back", t("Back")),
        ("f5", "refresh", t("Refresh")),
    ]

    def __init__(self, tmux: TmuxService) -> None:
        super().__init__()
        self.tmux = tmux

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="sessions-container"):
            yield Label(f"[bold]{t('Tmux Sessions')}[/bold]", id="screen-title")
            yield DataTable(id="sessions-table")
            with Horizontal(id="action-bar"):
                yield Button(f"[c] {t('Create')}", variant="success", id="btn-create")
                yield Button(f"[r] {t('Rename')}", variant="warning", id="btn-rename")
                yield Button(f"[a] {t('Attach')}", variant="primary", id="btn-attach")
                yield Button(f"[k] {t('Kill')}", variant="error", id="btn-kill")
                yield Button(f"[s] {t('Save')}", variant="primary", id="btn-save")
                yield Button(f"[l] {t('Load')}", variant="success", id="btn-load")
                yield Button(f"[Esc] {t('Back')}", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        self._setup_table()
        self._refresh_data()
        self.set_interval(5, self._refresh_data)

    def _setup_table(self) -> None:
        table = self.query_one("#sessions-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(t("Name"), t("Windows"), t("Status"), t("Type"), t("Path"))

    @work(thread=True)
    def _refresh_data(self) -> None:
        sessions = self.tmux.list_sessions()
        saved = self.tmux.list_saved_sessions()

        active_names: set[str] = set()
        rows: list[tuple[str, str, str, str, str]] = []
        for s in sessions:
            active_names.add(s.name)
            status = f"[green]{t('Attached')}[/]" if s.attached else f"[dim]{t('Detached')}[/]"
            saved_path = ""
            for sv in saved:
                if sv["name"] == s.name:
                    saved_path = sv["path"]
                    break
            path_display = s.path
            if saved_path:
                path_display += f"  [dim]({saved_path})[/]"
            rows.append((s.name, str(s.windows), status, t("Active"), path_display))

        for sv in saved:
            if sv["name"] not in active_names:
                rows.append((
                    sv["name"],
                    str(sv["windows"]),
                    f"[dim italic]{t('Saved')}[/]",
                    f"[dim]{t('Saved')}[/]",
                    f"[dim]{sv['path']}[/]",
                ))

        self.app.call_from_thread(self._apply_rows, rows)

    def _apply_rows(self, rows: list[tuple[str, str, str, str, str]]) -> None:
        table = self.query_one("#sessions-table", DataTable)
        table.clear()
        for row in rows:
            table.add_row(*row)

    def _get_selected_session_name(self) -> str | None:
        table = self.query_one("#sessions-table", DataTable)
        if table.row_count == 0:
            return None
        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            row_data = table.get_row(row_key)
            return str(row_data[0])
        except Exception:
            return None

    def _get_selected_session_type(self) -> str | None:
        """Return 'saved' or 'active' for the selected session row."""
        table = self.query_one("#sessions-table", DataTable)
        if table.row_count == 0:
            return None
        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            row_data = table.get_row(row_key)
            raw = str(row_data[3])
            return "saved" if t("Saved") in raw else "active"
        except Exception:
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "btn-create": self.action_create_session,
            "btn-rename": self.action_rename_session,
            "btn-attach": self.action_attach_session,
            "btn-kill": self.action_kill_session,
            "btn-save": self.action_save_session,
            "btn-load": self.action_load_session,
            "btn-back": self.action_go_back,
        }
        action = actions.get(event.button.id or "")
        if action:
            action()

    def action_create_session(self) -> None:
        def on_result(name: str | None) -> None:
            if name:
                result = self.tmux.create_session(name)
                if result:
                    self.notify(t("Session '{name}' created!").format(name=name), severity="information")
                else:
                    self.notify(t("Error creating session '{name}'").format(name=name), severity="error")
                self._refresh_data()

        self.app.push_screen(
            InputModal(t("New session name:"), t("my-session")), on_result
        )

    def action_rename_session(self) -> None:
        name = self._get_selected_session_name()
        if not name:
            self.notify(t("Select a session first"), severity="warning")
            return

        def on_result(new_name: str | None) -> None:
            if new_name:
                if self.tmux.rename_session(name, new_name):
                    self.notify(t("Session renamed to '{name}'").format(name=new_name))
                else:
                    self.notify(t("Error renaming session"), severity="error")
                self._refresh_data()

        self.app.push_screen(
            InputModal(t("New name for '{name}':").format(name=name), name), on_result
        )

    def action_attach_session(self) -> None:
        name = self._get_selected_session_name()
        if not name:
            self.notify(t("Select a session first"), severity="warning")
            return

        if self.tmux.attach_session(name):
            self.notify(
                t("Press Ctrl+B, D to detach and return to TmuxPlus"),
                severity="information",
                timeout=3,
            )
            self.app.exit(result=f"tmux attach -t {shlex.quote(name)}")
        else:
            self.notify(t("Session not found"), severity="error")

    def action_kill_session(self) -> None:
        name = self._get_selected_session_name()
        if not name:
            self.notify(t("Select a session first"), severity="warning")
            return

        def on_confirm(confirmed: bool | None) -> None:
            if confirmed:
                if self.tmux.kill_session(name):
                    self.notify(t("Session '{name}' terminated").format(name=name))
                else:
                    self.notify(t("Error terminating session"), severity="error")
                self._refresh_data()

        self.app.push_screen(
            ConfirmModal(t("Kill session '{name}'?").format(name=f"[bold]{name}[/bold]")),
            on_confirm,
        )

    def action_save_session(self) -> None:
        name = self._get_selected_session_name()
        if not name:
            self.notify(t("Select a session first"), severity="warning")
            return
        session_type = self._get_selected_session_type()
        if session_type == "saved":
            self.notify(t("This session is already saved to disk"), severity="warning")
            return
        if self.tmux.freeze_session(name):
            self.notify(t("Session '{name}' saved!").format(name=name), severity="information")
        else:
            self.notify(t("Error saving session '{name}'").format(name=name), severity="error")
        self._refresh_data()

    def action_load_session(self) -> None:
        name = self._get_selected_session_name()
        if not name:
            self.notify(t("Select a saved session first"), severity="warning")
            return
        session_type = self._get_selected_session_type()
        if session_type == "active":
            self.notify(t("This session is already active"), severity="warning")
            return
        result = self.tmux.restore_session(name)
        if result:
            self.notify(t("Session '{name}' restored!").format(name=name), severity="information")
        else:
            self.notify(t("Error restoring session '{name}'").format(name=name), severity="error")
        self._refresh_data()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self._refresh_data()
        self.notify(t("List refreshed"))
