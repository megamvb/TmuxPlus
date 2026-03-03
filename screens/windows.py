"""Tmux window management screen."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    Select,
)
from textual import work

from i18n import t
from services.tmux_service import TmuxService
from widgets.modals import ConfirmModal, InputModal


class WindowsScreen(Screen):
    """Tmux window management."""

    BINDINGS = [
        ("c", "create_window", t("Create")),
        ("r", "rename_window", t("Rename")),
        ("s", "select_window", t("Select")),
        ("k", "kill_window", t("Close")),
        ("escape", "go_back", t("Back")),
        ("f5", "refresh", t("Refresh")),
    ]

    def __init__(self, tmux: TmuxService) -> None:
        super().__init__()
        self.tmux = tmux
        self._selected_session: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="windows-container"):
            yield Label(f"[bold]{t('Tmux Windows')}[/bold]", id="screen-title")
            sessions = self.tmux.list_sessions()
            options = [(s.name, s.name) for s in sessions]
            yield Select(
                options,
                prompt=t("Select a session"),
                id="session-select",
            )
            yield DataTable(id="windows-table")
            with Horizontal(id="action-bar"):
                yield Button(f"[c] {t('Create')}", variant="success", id="btn-create")
                yield Button(f"[r] {t('Rename')}", variant="warning", id="btn-rename")
                yield Button(f"[s] {t('Select')}", variant="primary", id="btn-select")
                yield Button(f"[k] {t('Close')}", variant="error", id="btn-kill")
                yield Button(f"[Esc] {t('Back')}", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#windows-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(t("Index"), t("Name"), t("Panes"), t("Active"), t("ID"))
        sessions = self.tmux.list_sessions()
        if sessions:
            self._selected_session = sessions[0].name
            select_widget = self.query_one("#session-select", Select)
            select_widget.value = sessions[0].name
            self._refresh_data()
        self.set_interval(5, self._refresh_data)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value and event.value != Select.BLANK:
            self._selected_session = str(event.value)
            self._refresh_data()

    @work(thread=True)
    def _refresh_data(self) -> None:
        if not self._selected_session:
            self.app.call_from_thread(self._apply_rows, [])
            return
        windows = self.tmux.list_windows(self._selected_session)
        rows = []
        for w in windows:
            active = f"[green]{t('Yes')}[/]" if w.active else f"[dim]{t('No')}[/]"
            rows.append((w.index, w.name, str(w.panes), active, w.window_id))
        self.app.call_from_thread(self._apply_rows, rows)

    def _apply_rows(self, rows: list[tuple]) -> None:
        table = self.query_one("#windows-table", DataTable)
        table.clear()
        for row in rows:
            table.add_row(*row)

    def _get_selected_window(self) -> tuple[str, str] | None:
        """Return (window_name, window_id) for the selected row."""
        table = self.query_one("#windows-table", DataTable)
        if table.row_count == 0:
            return None
        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            row_data = table.get_row(row_key)
            return (str(row_data[1]), str(row_data[4]))
        except Exception:
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "btn-create": self.action_create_window,
            "btn-rename": self.action_rename_window,
            "btn-select": self.action_select_window,
            "btn-kill": self.action_kill_window,
            "btn-back": self.action_go_back,
        }
        action = actions.get(event.button.id or "")
        if action:
            action()

    def action_create_window(self) -> None:
        if not self._selected_session:
            self.notify(t("Select a session first"), severity="warning")
            return

        def on_result(name: str | None) -> None:
            if name:
                result = self.tmux.create_window(self._selected_session, name)
                if result:
                    self.notify(t("Window '{name}' created!").format(name=name))
                else:
                    self.notify(t("Error creating window"), severity="error")
                self._refresh_data()

        self.app.push_screen(
            InputModal(t("New window name:"), t("my-window")), on_result
        )

    def action_rename_window(self) -> None:
        selected = self._get_selected_window()
        if not selected:
            self.notify(t("Select a window first"), severity="warning")
            return
        win_name, win_id = selected

        def on_result(new_name: str | None) -> None:
            if new_name:
                if self.tmux.rename_window(self._selected_session, win_id, new_name):
                    self.notify(t("Window renamed to '{name}'").format(name=new_name))
                else:
                    self.notify(t("Error renaming window"), severity="error")
                self._refresh_data()

        self.app.push_screen(
            InputModal(t("New name for '{name}':").format(name=win_name), win_name), on_result
        )

    def action_select_window(self) -> None:
        selected = self._get_selected_window()
        if not selected:
            self.notify(t("Select a window first"), severity="warning")
            return
        win_name, win_id = selected
        if self.tmux.select_window(self._selected_session, win_id):
            self.notify(t("Window '{name}' selected").format(name=win_name))
        else:
            self.notify(t("Error selecting window"), severity="error")

    def action_kill_window(self) -> None:
        selected = self._get_selected_window()
        if not selected:
            self.notify(t("Select a window first"), severity="warning")
            return
        win_name, win_id = selected

        def on_confirm(confirmed: bool | None) -> None:
            if confirmed:
                if self.tmux.kill_window(self._selected_session, win_id):
                    self.notify(t("Window '{name}' closed").format(name=win_name))
                else:
                    self.notify(t("Error closing window"), severity="error")
                self._refresh_data()

        self.app.push_screen(
            ConfirmModal(t("Close window '{name}'?").format(name=f"[bold]{win_name}[/bold]")),
            on_confirm,
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self._refresh_data()
        self.notify(t("List refreshed"))
