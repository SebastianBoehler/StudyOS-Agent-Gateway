import json
from pathlib import Path
from typing import Any, cast


class ChannelSessionStore:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path).expanduser()

    def get(self, channel_id: int) -> str | None:
        data = self._read()
        value = data.get(str(channel_id))
        return value if isinstance(value, str) and value else None

    def set(self, channel_id: int, session_id: str) -> None:
        if not session_id:
            raise ValueError("session_id must be non-empty")
        data = self._read()
        data[str(channel_id)] = session_id
        self._write(data)

    def _read(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        parsed: Any = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise RuntimeError(f"Session store must contain a JSON object: {self._path}")
        data = cast(dict[object, object], parsed)
        return {str(key): value for key, value in data.items() if isinstance(value, str)}

    def _write(self, data: dict[str, str]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(self._path)


def default_session_store_path(codex_home: str | None) -> Path:
    root = Path(codex_home or "~/.codex").expanduser()
    return root / "gateway" / "discord-channel-sessions.json"
