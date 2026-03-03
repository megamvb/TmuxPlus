"""Command safety guard for TmuxPlus send-keys feature."""

from __future__ import annotations

import re
import shlex


def _normalize(cmd: str) -> str:
    """Collapse whitespace and strip for reliable matching."""
    return re.sub(r"\s+", " ", cmd.strip())


def _split_segments(norm: str) -> list[str]:
    """Split a normalized command line on shell operators (; && || |)."""
    return [s for s in re.split(r"\s*(?:;|&&|\|\||\|)\s*", norm) if s]


def _tokenize(segment: str) -> list[str]:
    """Tokenize a segment, falling back to simple split on bad quoting."""
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def _effective_tokens(tokens: list[str]) -> list[str]:
    """Strip leading 'sudo' to get the actual command tokens."""
    if tokens and tokens[0] == "sudo":
        return tokens[1:]
    return tokens


def _get_targets(tokens: list[str], cmd_name: str) -> list[str]:
    """Return non-flag arguments after cmd_name in a token list."""
    targets: list[str] = []
    past_cmd = False
    for tok in tokens:
        if not past_cmd:
            if tok == cmd_name:
                past_cmd = True
            continue
        if tok.startswith("-"):
            continue
        targets.append(tok)
    return targets


def _get_flag_value(tokens: list[str], flag: str) -> str | None:
    """Return the value of a 'flag=value' or 'flag value' pair."""
    for i, tok in enumerate(tokens):
        if tok == flag and i + 1 < len(tokens):
            return tokens[i + 1]
        if tok.startswith(f"{flag}="):
            return tok.split("=", 1)[1]
    return None


# ── Patterns ────────────────────────────────────────────────────────

# Root filesystem targets — always fatal
_ROOT_TARGETS = re.compile(r"^/\*{0,2}$")  # /  /*  /**

# Fork bomb patterns
_FORK_BOMB = re.compile(r":\(\)\s*\{.*\|.*&\s*\}\s*;?\s*:")

# Commands that are ALWAYS blocked (no arguments needed to be destructive)
_ALWAYS_BLOCKED_CMDS = {"halt", "poweroff", "init"}

# Commands blocked when targeting root (/)
_ROOT_DESTRUCTIVE_CMDS = {"rm", "chmod", "chown", "chattr"}

# Commands that are always dangerous (need confirmation)
_DANGEROUS_CMDS = {
    "rm", "rmdir", "shred",
    "mkfs", "mkfs.ext4", "mkfs.ext3", "mkfs.xfs", "mkfs.btrfs", "mkfs.vfat",
    "mkswap", "wipefs", "fdisk", "parted", "gdisk",
    "dd",
    "shutdown", "reboot", "halt", "poweroff", "init", "systemctl",
    "chmod", "chown", "chattr",
    "kill", "killall", "pkill",
    "iptables", "ip6tables", "nft", "ufw",
    "useradd", "userdel", "usermod", "passwd", "groupdel",
    "crontab",
}

# systemctl subcommands that are dangerous
_DANGEROUS_SYSTEMCTL = {"stop", "disable", "mask", "poweroff", "reboot", "halt"}


def is_blocked(cmd: str) -> bool:
    """Return True if the command must NEVER be sent."""
    norm = _normalize(cmd)

    # Fork bombs
    if _FORK_BOMB.search(norm):
        return True

    # Redirect to block devices:  > /dev/sda, etc.
    if re.search(r">\s*/dev/[a-z]", norm):
        return True

    for segment in _split_segments(norm):
        tokens = _tokenize(segment)
        if not tokens:
            continue
        effective = _effective_tokens(tokens)
        if not effective:
            continue
        cmd_name = effective[0]

        # Always blocked commands (shutdown-type with no safe use)
        if cmd_name in _ALWAYS_BLOCKED_CMDS:
            return True

        # init 0 / init 6
        if cmd_name == "init" and len(effective) > 1 and effective[1] in ("0", "6"):
            return True

        # rm/chmod/chown targeting root
        if cmd_name in _ROOT_DESTRUCTIVE_CMDS:
            targets = _get_targets(effective, cmd_name)
            for target in targets:
                if _ROOT_TARGETS.match(target):
                    return True

        # dd of=/dev/*
        if cmd_name == "dd":
            of_val = _get_flag_value(effective, "of")
            if of_val and of_val.startswith("/dev/"):
                return True

        # mkfs* targeting any device
        if cmd_name.startswith("mkfs"):
            targets = _get_targets(effective, cmd_name)
            for target in targets:
                if target.startswith("/dev/"):
                    return True

    return False


def is_dangerous(cmd: str) -> bool:
    """Return True if the command needs extra confirmation before sending."""
    norm = _normalize(cmd)

    # Fork bomb patterns are blocked, not just dangerous
    if _FORK_BOMB.search(norm):
        return True

    for segment in _split_segments(norm):
        tokens = _tokenize(segment)
        if not tokens:
            continue
        effective = _effective_tokens(tokens)
        if not effective:
            continue
        cmd_name = effective[0]

        if cmd_name in _DANGEROUS_CMDS:
            # systemctl: only flag specific subcommands
            if cmd_name == "systemctl":
                if len(effective) > 1 and effective[1] in _DANGEROUS_SYSTEMCTL:
                    return True
                continue
            return True

        # mkfs variants (mkfs.ext4, etc.)
        if cmd_name.startswith("mkfs"):
            return True

    return False
