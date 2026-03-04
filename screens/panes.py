"""Tmux pane management screen."""

import time

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
from services.command_guard import is_blocked, is_dangerous
from services.tmux_service import TmuxService
from widgets.modals import AliasModal, ConfirmModal, HistoryModal, InputModal


class PanesScreen(Screen):
    """Tmux pane management."""

    BINDINGS = [
        ("v", "split_vertical", t("Split V")),
        ("h", "split_horizontal", t("Split H")),
        ("x", "send_command", t("Send Cmd")),
        ("H", "history_command", t("History")),
        ("A", "alias_command", t("Aliases")),
        ("k", "kill_pane", t("Close")),
        ("escape", "go_back", t("Back")),
        ("f5", "refresh", t("Refresh")),
    ]

    def __init__(self, tmux: TmuxService) -> None:
        super().__init__()
        self.tmux = tmux
        self._selected_session: str = ""
        self._selected_window_id: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="panes-container"):
            yield Label(f"[bold]{t('Tmux Panes')}[/bold]", id="screen-title")
            with Horizontal(id="selectors"):
                sessions = self.tmux.list_sessions()
                yield Select(
                    [(s.name, s.name) for s in sessions],
                    prompt=t("Session"),
                    id="session-select",
                )
                yield Select(
                    [],
                    prompt=t("Window"),
                    id="window-select",
                )
            yield DataTable(id="panes-table")
            with Horizontal(id="action-bar"):
                yield Button("[v] Split Vertical", variant="success", id="btn-splitv")
                yield Button("[h] Split Horizontal", variant="success", id="btn-splith")
                yield Button(f"[x] {t('Send Cmd')}", variant="primary", id="btn-send")
                yield Button(f"[H] {t('History')}", variant="primary", id="btn-history")
                yield Button(f"[A] {t('Aliases')}", variant="primary", id="btn-alias")
                yield Button(f"[k] {t('Close')}", variant="error", id="btn-kill")
                yield Button(f"[Esc] {t('Back')}", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#panes-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(t("Index"), t("Size"), t("Command"), t("Active"), t("ID"))
        sessions = self.tmux.list_sessions()
        if sessions:
            self._selected_session = sessions[0].name
            select_widget = self.query_one("#session-select", Select)
            select_widget.value = sessions[0].name
            self._update_windows()
        self.set_interval(5, self._refresh_panes)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "session-select":
            if event.value and event.value != Select.BLANK:
                self._selected_session = str(event.value)
                self._update_windows()
        elif event.select.id == "window-select":
            if event.value and event.value != Select.BLANK:
                self._selected_window_id = str(event.value)
                self._refresh_panes()

    @work(thread=True)
    def _update_windows(self) -> None:
        windows = self.tmux.list_windows(self._selected_session)
        options = [(f"{w.index}: {w.name}", w.window_id) for w in windows]
        first_id = windows[0].window_id if windows else ""
        self.app.call_from_thread(self._apply_windows, options, first_id)

    def _apply_windows(self, options: list[tuple[str, str]], first_id: str) -> None:
        window_select = self.query_one("#window-select", Select)
        window_select.set_options(options)
        if first_id:
            self._selected_window_id = first_id
            window_select.value = first_id
            self._refresh_panes()
        else:
            self._selected_window_id = ""
            table = self.query_one("#panes-table", DataTable)
            table.clear()

    @work(thread=True)
    def _refresh_panes(self) -> None:
        if not self._selected_session or not self._selected_window_id:
            self.app.call_from_thread(self._apply_pane_rows, [])
            return
        panes = self.tmux.list_panes(
            self._selected_session, self._selected_window_id
        )
        rows = []
        for p in panes:
            active = f"[green]{t('Yes')}[/]" if p.active else f"[dim]{t('No')}[/]"
            size = f"{p.width}x{p.height}"
            rows.append((p.index, size, p.current_command, active, p.pane_id))
        self.app.call_from_thread(self._apply_pane_rows, rows)

    def _apply_pane_rows(self, rows: list[tuple]) -> None:
        table = self.query_one("#panes-table", DataTable)
        table.clear()
        for row in rows:
            table.add_row(*row)

    def _get_selected_pane_id(self) -> str | None:
        table = self.query_one("#panes-table", DataTable)
        if table.row_count == 0:
            return None
        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            row_data = table.get_row(row_key)
            return str(row_data[4])
        except Exception:
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "btn-splitv": self.action_split_vertical,
            "btn-splith": self.action_split_horizontal,
            "btn-send": self.action_send_command,
            "btn-history": self.action_history_command,
            "btn-alias": self.action_alias_command,
            "btn-kill": self.action_kill_pane,
            "btn-back": self.action_go_back,
        }
        action = actions.get(event.button.id or "")
        if action:
            action()

    def action_split_vertical(self) -> None:
        if not self._selected_window_id:
            self.notify(t("Select a window first"), severity="warning")
            return
        result = self.tmux.split_window(
            self._selected_session, self._selected_window_id, vertical=True
        )
        if result:
            self.notify(t("Vertical split created!"))
            self._refresh_panes()
        else:
            self.notify(t("Error creating split"), severity="error")

    def action_split_horizontal(self) -> None:
        if not self._selected_window_id:
            self.notify(t("Select a window first"), severity="warning")
            return
        result = self.tmux.split_window(
            self._selected_session, self._selected_window_id, vertical=False
        )
        if result:
            self.notify(t("Horizontal split created!"))
            self._refresh_panes()
        else:
            self.notify(t("Error creating split"), severity="error")

    def action_send_command(self) -> None:
        pane_id = self._get_selected_pane_id()
        if not pane_id:
            self.notify(t("Select a pane first"), severity="warning")
            return

        def _do_send(cmd: str) -> None:
            if self.tmux.send_keys_to_pane(pane_id, cmd):
                self.notify(t("Command sent to pane {id}").format(id=pane_id))
            else:
                self.notify(t("Error sending command"), severity="error")

        def on_result(cmd: str | None) -> None:
            if not cmd:
                return
            if is_blocked(cmd):
                self.notify(
                    t("Command blocked: destructive rm on root is not allowed"),
                    severity="error",
                    timeout=5,
                )
                return
            if is_dangerous(cmd):
                def on_confirm(confirmed: bool | None) -> None:
                    if confirmed:
                        _do_send(cmd)
                self.app.push_screen(
                    ConfirmModal(
                        t("Dangerous command: '{cmd}'\nAre you sure you want to send it?").format(
                            cmd=f"[bold red]{cmd}[/bold red]"
                        )
                    ),
                    on_confirm,
                )
                return
            _do_send(cmd)

        self.app.push_screen(
            InputModal(t("Command to send to pane:"), "ls -la"), on_result
        )

    def action_history_command(self) -> None:
        pane_id = self._get_selected_pane_id()
        if not pane_id:
            self.notify(t("Select a pane first"), severity="warning")
            return

        def _do_send(cmd: str) -> None:
            if self.tmux.send_keys_to_pane(pane_id, cmd):
                self.notify(t("Command sent to pane {id}").format(id=pane_id))
            else:
                self.notify(t("Error sending command"), severity="error")

        def on_result(cmd: str | None) -> None:
            if not cmd:
                return
            if is_blocked(cmd):
                self.notify(
                    t("Command blocked: destructive rm on root is not allowed"),
                    severity="error",
                    timeout=5,
                )
                return
            if is_dangerous(cmd):
                def on_confirm(confirmed: bool | None) -> None:
                    if confirmed:
                        _do_send(cmd)
                self.app.push_screen(
                    ConfirmModal(
                        t("Dangerous command: '{cmd}'\nAre you sure you want to send it?").format(
                            cmd=f"[bold red]{cmd}[/bold red]"
                        )
                    ),
                    on_confirm,
                )
                return
            _do_send(cmd)

        self._open_history_modal(pane_id, on_result)

    @work(thread=True)
    def _open_history_modal(self, pane_id: str, callback) -> None:
        self.tmux.flush_pane_history(pane_id)
        time.sleep(0.3)
        history_path = self.tmux.get_pane_histfile(pane_id)
        self.app.call_from_thread(
            self.app.push_screen, HistoryModal(history_path=history_path), callback
        )

    def action_alias_command(self) -> None:
        pane_id = self._get_selected_pane_id()
        if not pane_id:
            self.notify(t("Select a pane first"), severity="warning")
            return

        def _do_send(cmd: str) -> None:
            if self.tmux.send_keys_to_pane(pane_id, cmd):
                self.notify(t("Command sent to pane {id}").format(id=pane_id))
            else:
                self.notify(t("Error sending command"), severity="error")

        def on_result(cmd: str | None) -> None:
            if not cmd:
                return
            if is_blocked(cmd):
                self.notify(
                    t("Command blocked: destructive rm on root is not allowed"),
                    severity="error",
                    timeout=5,
                )
                return
            if is_dangerous(cmd):
                def on_confirm(confirmed: bool | None) -> None:
                    if confirmed:
                        _do_send(cmd)
                self.app.push_screen(
                    ConfirmModal(
                        t("Dangerous command: '{cmd}'\nAre you sure you want to send it?").format(
                            cmd=f"[bold red]{cmd}[/bold red]"
                        )
                    ),
                    on_confirm,
                )
                return
            _do_send(cmd)

        self.app.push_screen(AliasModal(), on_result)

    def action_kill_pane(self) -> None:
        pane_id = self._get_selected_pane_id()
        if not pane_id:
            self.notify(t("Select a pane first"), severity="warning")
            return

        def on_confirm(confirmed: bool | None) -> None:
            if confirmed:
                if self.tmux.kill_pane(pane_id):
                    self.notify(t("Pane {id} closed").format(id=pane_id))
                    self._refresh_panes()
                else:
                    self.notify(t("Error closing pane"), severity="error")

        self.app.push_screen(
            ConfirmModal(t("Close pane '{id}'?").format(id=f"[bold]{pane_id}[/bold]")),
            on_confirm,
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self._refresh_panes()
        self.notify(t("List refreshed"))
