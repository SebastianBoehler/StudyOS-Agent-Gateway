from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import discord

DISCORD_MESSAGE_LIMIT = 1900


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return cleaned or "attachment"


async def save_message_attachments(message: discord.Message, root: Path) -> tuple[Path, ...]:
    if not message.attachments:
        return ()

    target_dir = root / str(message.id)
    target_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for index, attachment in enumerate(message.attachments, start=1):
        filename = f"{index}_{sanitize_filename(attachment.filename)}"
        path = target_dir / filename
        await attachment.save(path)
        saved.append(path)
    return tuple(saved)


def validate_artifact_files(
    files: tuple[Path, ...],
    allowed_roots: tuple[Path, ...],
    max_bytes: int,
) -> tuple[Path, ...]:
    validated: list[Path] = []
    resolved_roots = tuple(root.expanduser().resolve() for root in allowed_roots)
    for path in files:
        resolved = path.expanduser().resolve()
        if not resolved.exists() or not resolved.is_file():
            raise RuntimeError(f"Agent artifact file does not exist: {path}")
        if resolved_roots and not any(resolved.is_relative_to(root) for root in resolved_roots):
            roots = ", ".join(str(root) for root in resolved_roots)
            raise RuntimeError(f"Agent artifact file is outside allowed roots: {path} ({roots})")
        if resolved.stat().st_size > max_bytes:
            raise RuntimeError(
                f"Agent artifact file is larger than the configured Discord limit: {path}"
            )
        validated.append(resolved)
    return tuple(validated)
