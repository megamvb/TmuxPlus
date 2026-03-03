#!/usr/bin/env python3
"""TmuxPlus — visual manager for tmux."""

import os
import shlex
import subprocess
import sys


def _configure_locale() -> None:
    """Set locale from TMUXPLUS_LANG env var before any app modules are imported."""
    lang = os.environ.get("TMUXPLUS_LANG", "")
    if lang:
        from i18n import set_locale
        set_locale(lang)


def _parse_flags() -> None:
    """Handle --log flag: enables file logging via TMUXPLUS_LOG env var."""
    if "--log" in sys.argv:
        os.environ["TMUXPLUS_LOG"] = "1"
        sys.argv.remove("--log")


def main() -> None:
    _parse_flags()
    _configure_locale()  # must run before importing app modules
    from app import TmuxPlusApp

    while True:
        app = TmuxPlusApp()
        result = app.run()

        if result and isinstance(result, str) and result.startswith("tmux"):
            # Run tmux attach as a subprocess — on detach (Ctrl+B, D)
            # control returns here and TmuxPlus reopens automatically.
            subprocess.run(shlex.split(result))
            continue

        # Any other exit (quit, Ctrl+Q) ends the loop.
        break


if __name__ == "__main__":
    main()
