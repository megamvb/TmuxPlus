"""Reusable modal dialogs for TmuxPlus."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

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
