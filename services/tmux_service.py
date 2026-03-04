"""Camada de serviço para operações tmux via libtmux."""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import libtmux
from libtmux.constants import PaneDirection
from libtmux.exc import LibTmuxException

# Characters allowed in session/window names: alphanumeric, hyphen, underscore, dot.
_SAFE_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")

SESSIONS_DIR = Path.home() / ".config" / "tmuxplus" / "sessions"
LOG_FILE = Path.home() / ".config" / "tmuxplus" / "tmuxplus.log"

if os.environ.get("TMUXPLUS_LOG"):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _log_fd = os.open(str(LOG_FILE), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    logging.basicConfig(
        stream=os.fdopen(_log_fd, "w"),
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
    )
else:
    logging.disable(logging.CRITICAL)


@dataclass
class SessionInfo:
    session_id: str
    name: str
    windows: int
    attached: bool
    created: str
    path: str

    @classmethod
    def from_session(cls, session: libtmux.Session) -> SessionInfo:
        return cls(
            session_id=session.session_id or "",
            name=session.session_name or "",
            windows=len(session.windows),
            attached=session.session_attached != "0",
            created=session.session_created or "",
            path=session.session_path or "",
        )


@dataclass
class WindowInfo:
    window_id: str
    index: str
    name: str
    panes: int
    active: bool
    session_name: str

    @classmethod
    def from_window(cls, window: libtmux.Window, session_name: str) -> WindowInfo:
        return cls(
            window_id=window.window_id or "",
            index=window.window_index or "",
            name=window.window_name or "",
            panes=len(window.panes),
            active=window.window_active == "1",
            session_name=session_name,
        )


@dataclass
class PaneInfo:
    pane_id: str
    index: str
    width: str
    height: str
    active: bool
    current_command: str
    window_name: str
    session_name: str

    @classmethod
    def from_pane(
        cls, pane: libtmux.Pane, window_name: str, session_name: str
    ) -> PaneInfo:
        return cls(
            pane_id=pane.pane_id or "",
            index=pane.pane_index or "",
            width=pane.pane_width or "",
            height=pane.pane_height or "",
            active=pane.pane_active == "1",
            current_command=pane.pane_current_command or "",
            window_name=window_name,
            session_name=session_name,
        )


def _safe_session_path(name: str) -> Path | None:
    """Return the session file path if safe, or None if path traversal detected."""
    filepath = (SESSIONS_DIR / f"{name}.json").resolve()
    if not str(filepath).startswith(str(SESSIONS_DIR.resolve())):
        logging.warning("Path traversal attempt blocked: %r", name)
        return None
    return filepath


def is_valid_name(name: str) -> bool:
    """Validate a tmux session or window name.

    Rejects empty names, shell metacharacters, control characters,
    and names starting with a dash (flag injection).
    """
    return bool(name and _SAFE_NAME_RE.match(name))


def _safe_directory(path: str | None) -> str | None:
    """Return the path only if it is an existing directory, else None (→ home)."""
    if not path:
        return None
    p = Path(path)
    if p.is_dir():
        return str(p)
    return None


class TmuxService:
    """Serviço centralizado para todas as operações tmux."""

    def __init__(self) -> None:
        self._server: libtmux.Server | None = None

    @property
    def server(self) -> libtmux.Server:
        if self._server is None:
            self._server = libtmux.Server()
        return self._server

    def is_tmux_running(self) -> bool:
        try:
            return len(self.server.sessions) > 0
        except Exception:
            return False

    def has_server(self) -> bool:
        try:
            _ = self.server.sessions
            return True
        except Exception:
            return False

    # ── Sessões ──────────────────────────────────────────────

    def list_sessions(self) -> list[SessionInfo]:
        try:
            return [SessionInfo.from_session(s) for s in self.server.sessions]
        except Exception:
            return []

    def create_session(self, name: str, attach: bool = False) -> SessionInfo | None:
        if not is_valid_name(name):
            return None
        try:
            session = self.server.new_session(
                session_name=name, attach=attach
            )
            return SessionInfo.from_session(session)
        except LibTmuxException:
            return None

    def kill_session(self, name: str) -> bool:
        try:
            session = self.server.sessions.get(session_name=name)
            if session:
                session.kill()
                self.delete_saved_session(name)
                return True
            return False
        except Exception:
            return False

    def rename_session(self, old_name: str, new_name: str) -> bool:
        if not is_valid_name(new_name):
            return False
        try:
            session = self.server.sessions.get(session_name=old_name)
            if session:
                session.rename_session(new_name)
                return True
            return False
        except Exception:
            return False

    def attach_session(self, name: str) -> bool:
        """Retorna o comando para attach (deve ser executado fora do app)."""
        try:
            session = self.server.sessions.get(session_name=name)
            return session is not None
        except Exception:
            return False

    def get_session(self, name: str) -> libtmux.Session | None:
        try:
            return self.server.sessions.get(session_name=name)
        except Exception:
            return None

    # ── Janelas ──────────────────────────────────────────────

    def list_windows(self, session_name: str) -> list[WindowInfo]:
        try:
            session = self.server.sessions.get(session_name=session_name)
            if not session:
                return []
            return [
                WindowInfo.from_window(w, session_name) for w in session.windows
            ]
        except Exception:
            return []

    def list_all_windows(self) -> list[WindowInfo]:
        results: list[WindowInfo] = []
        for session in self.list_sessions():
            results.extend(self.list_windows(session.name))
        return results

    def create_window(
        self, session_name: str, window_name: str, attach: bool = False
    ) -> WindowInfo | None:
        if not is_valid_name(window_name):
            return None
        try:
            session = self.server.sessions.get(session_name=session_name)
            if not session:
                return None
            window = session.new_window(
                window_name=window_name, attach=attach
            )
            return WindowInfo.from_window(window, session_name)
        except Exception:
            return None

    def kill_window(self, session_name: str, window_id: str) -> bool:
        try:
            session = self.server.sessions.get(session_name=session_name)
            if not session:
                return False
            window = session.windows.get(window_id=window_id)
            if window:
                window.kill()
                return True
            return False
        except Exception:
            return False

    def rename_window(
        self, session_name: str, window_id: str, new_name: str
    ) -> bool:
        if not is_valid_name(new_name):
            return False
        try:
            session = self.server.sessions.get(session_name=session_name)
            if not session:
                return False
            window = session.windows.get(window_id=window_id)
            if window:
                window.rename_window(new_name)
                return True
            return False
        except Exception:
            return False

    def select_window(self, session_name: str, window_id: str) -> bool:
        try:
            session = self.server.sessions.get(session_name=session_name)
            if not session:
                return False
            window = session.windows.get(window_id=window_id)
            if window:
                window.select()
                return True
            return False
        except Exception:
            return False

    # ── Painéis ──────────────────────────────────────────────

    def list_panes(self, session_name: str, window_id: str) -> list[PaneInfo]:
        try:
            session = self.server.sessions.get(session_name=session_name)
            if not session:
                return []
            window = session.windows.get(window_id=window_id)
            if not window:
                return []
            return [
                PaneInfo.from_pane(p, window.window_name or "", session_name)
                for p in window.panes
            ]
        except Exception:
            return []

    def list_all_panes(self) -> list[PaneInfo]:
        results: list[PaneInfo] = []
        for session_info in self.list_sessions():
            session = self.get_session(session_info.name)
            if not session:
                continue
            for window in session.windows:
                for pane in window.panes:
                    results.append(
                        PaneInfo.from_pane(
                            pane,
                            window.window_name or "",
                            session_info.name,
                        )
                    )
        return results

    def split_window(
        self,
        session_name: str,
        window_id: str,
        vertical: bool = True,
    ) -> PaneInfo | None:
        try:
            session = self.server.sessions.get(session_name=session_name)
            if not session:
                return None
            window = session.windows.get(window_id=window_id)
            if not window:
                return None
            direction = PaneDirection.Right if vertical else PaneDirection.Below
            pane = window.split(direction=direction, attach=False)
            return PaneInfo.from_pane(
                pane, window.window_name or "", session_name
            )
        except Exception:
            return None

    def kill_pane(self, pane_id: str) -> bool:
        try:
            for session in self.server.sessions:
                for window in session.windows:
                    for pane in window.panes:
                        if pane.pane_id == pane_id:
                            pane.cmd("kill-pane")
                            return True
            return False
        except Exception:
            return False

    def flush_pane_history(self, pane_id: str) -> bool:
        """Send ' history -a' to the pane to flush in-memory history to disk.

        The leading space avoids polluting history (HISTCONTROL=ignoreboth).
        """
        try:
            for session in self.server.sessions:
                for window in session.windows:
                    for pane in window.panes:
                        if pane.pane_id == pane_id:
                            pane.send_keys(" history -a", suppress_history=False)
                            return True
            return False
        except Exception:
            return False

    def get_pane_histfile(self, pane_id: str) -> str:
        """Detect the HISTFILE for the shell running in a pane.

        Uses tmux display-message to get the pane PID, then reads
        /proc/<pid>/environ to find HISTFILE and HOME.
        Returns fallback ~/.bash_history on any failure.
        """
        fallback = str(Path.home() / ".bash_history")
        try:
            result = subprocess.run(
                ["tmux", "display-message", "-t", pane_id, "-p", "#{pane_pid}"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode != 0 or not result.stdout.strip():
                return fallback
            pid = result.stdout.strip()
            if not pid.isdigit():
                return fallback
            environ_path = Path(f"/proc/{pid}/environ")
            if not environ_path.exists():
                return fallback
            env_bytes = environ_path.read_bytes()
            env_vars: dict[str, str] = {}
            for entry in env_bytes.split(b"\x00"):
                if b"=" in entry:
                    key, _, val = entry.partition(b"=")
                    env_vars[key.decode("utf-8", errors="replace")] = val.decode("utf-8", errors="replace")
            histfile = env_vars.get("HISTFILE")
            if histfile:
                return histfile
            home = env_vars.get("HOME", str(Path.home()))
            return str(Path(home) / ".bash_history")
        except Exception:
            return fallback

    def send_keys_to_pane(self, pane_id: str, keys: str) -> bool:
        try:
            for session in self.server.sessions:
                for window in session.windows:
                    for pane in window.panes:
                        if pane.pane_id == pane_id:
                            pane.send_keys(keys)
                            return True
            return False
        except Exception:
            return False

    # ── Persistência (Salvar/Restaurar) ───────────────────

    def freeze_session(self, name: str) -> bool:
        """Salva o estado completo de uma sessão em disco."""
        try:
            session = self.server.sessions.get(session_name=name)
            if not session:
                return False

            # Obter layouts via subprocess (mais confiável)
            result = subprocess.run(
                ["tmux", "list-windows", "-t", name, "-F", "#{window_index}:#{window_layout}"],
                capture_output=True, text=True, timeout=10,
            )
            layouts: dict[str, str] = {}
            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    idx, layout = line.split(":", 1)
                    layouts[idx] = layout

            windows_data: list[dict] = []
            for window in session.windows:
                panes_data: list[dict] = []
                for pane in window.panes:
                    panes_data.append({
                        "path": pane.pane_current_path or "",
                        "command": pane.pane_current_command or "",
                        "active": pane.pane_active == "1",
                    })
                windows_data.append({
                    "name": window.window_name or "",
                    "index": window.window_index or "",
                    "layout": layouts.get(window.window_index or "", ""),
                    "active": window.window_active == "1",
                    "panes": panes_data,
                })

            data = {"session_name": name, "windows": windows_data}

            SESSIONS_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
            filepath = _safe_session_path(name)
            if filepath is None:
                return False
            fd = os.open(str(filepath), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    @staticmethod
    def _validate_session_data(data: dict) -> bool:
        """Validate the structure of a saved session JSON."""
        if not isinstance(data, dict):
            return False
        if not isinstance(data.get("session_name"), str) or not data["session_name"]:
            return False
        windows = data.get("windows")
        if not isinstance(windows, list) or not windows:
            return False
        for win in windows:
            if not isinstance(win, dict):
                return False
            if not isinstance(win.get("name"), str):
                return False
            panes = win.get("panes")
            if not isinstance(panes, list):
                return False
            for pane in panes:
                if not isinstance(pane, dict):
                    return False
        return True

    def restore_session(self, name: str) -> SessionInfo | None:
        """Restaura uma sessão a partir de um arquivo JSON salvo."""
        try:
            filepath = _safe_session_path(name)
            if filepath is None or not filepath.exists():
                return None

            data = json.loads(filepath.read_text())
            if not self._validate_session_data(data):
                logging.warning("Invalid session JSON structure for %r", name)
                return None

            session_name = data["session_name"]

            # Verificar se já existe sessão com esse nome
            if self.server.sessions.filter(session_name=session_name):
                return None

            windows = data["windows"]

            # Criar sessão com a primeira janela
            first_win = windows[0]
            first_pane_path = _safe_directory(
                first_win["panes"][0]["path"] if first_win["panes"] else None
            )
            session = self.server.new_session(
                session_name=session_name,
                attach=False,
                start_directory=first_pane_path,
                window_name=first_win["name"],
            )

            active_window_idx: str | None = None

            # Configurar a primeira janela
            win_obj = session.windows[0]
            self._restore_window_panes(win_obj, first_win, session_name)
            if first_win.get("active"):
                active_window_idx = win_obj.window_index

            # Criar janelas restantes
            for win_data in windows[1:]:
                first_pane_path = _safe_directory(
                    win_data["panes"][0]["path"] if win_data["panes"] else None
                )
                win_obj = session.new_window(
                    window_name=win_data["name"],
                    attach=False,
                    start_directory=first_pane_path,
                )
                self._restore_window_panes(win_obj, win_data, session_name)
                if win_data.get("active"):
                    active_window_idx = win_obj.window_index

            # Selecionar janela ativa
            if active_window_idx is not None:
                for w in session.windows:
                    if w.window_index == active_window_idx:
                        w.select()
                        break

            return SessionInfo.from_session(session)
        except Exception as e:
            logging.exception("restore_session(%r) falhou: %s", name, e)
            return None

    def _restore_window_panes(
        self, window: libtmux.Window, win_data: dict, session_name: str
    ) -> None:
        """Cria painéis extras e aplica layout numa janela."""
        try:
            panes_data = win_data.get("panes", [])

            # Criar painéis extras (o primeiro já existe)
            for pane_data in panes_data[1:]:
                window.split(
                    direction=PaneDirection.Below,
                    attach=False,
                    start_directory=_safe_directory(pane_data.get("path")),
                )

            # Aplicar layout salvo
            layout = win_data.get("layout")
            if layout:
                subprocess.run(
                    ["tmux", "select-layout", "-t", f"{session_name}:{window.window_index}", layout],
                    capture_output=True, timeout=10,
                )

            # Selecionar painel ativo
            for i, pane_data in enumerate(panes_data):
                if pane_data.get("active") and i < len(window.panes):
                    window.panes[i].select()
                    break
        except Exception as e:
            logging.exception("_restore_window_panes(%r) falhou: %s", win_data.get("name"), e)
            raise

    def list_saved_sessions(self) -> list[dict]:
        """Lista sessões salvas em disco."""
        if not SESSIONS_DIR.exists():
            return []
        saved: list[dict] = []
        for f in sorted(SESSIONS_DIR.glob("*.json")):
            try:
                data = json.loads(f.read_text())
                if not isinstance(data, dict):
                    continue
                saved.append({
                    "name": data.get("session_name", f.stem),
                    "windows": len(data.get("windows", [])),
                    "path": str(f),
                })
            except Exception:
                continue
        return saved

    def delete_saved_session(self, name: str) -> bool:
        """Remove arquivo de sessão salva."""
        try:
            filepath = _safe_session_path(name)
            if filepath is None:
                return False
            if filepath.exists():
                filepath.unlink()
                return True
            return False
        except Exception:
            return False
