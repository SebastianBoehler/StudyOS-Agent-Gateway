from pathlib import Path

from study_discord_agent.session_store import ChannelSessionStore, default_session_store_path


def test_channel_session_store_round_trips(tmp_path: Path) -> None:
    store = ChannelSessionStore(tmp_path / "sessions.json")

    assert store.get(123) is None

    store.set(123, "session-a")

    assert store.get(123) == "session-a"
    assert ChannelSessionStore(tmp_path / "sessions.json").get(123) == "session-a"


def test_default_session_store_lives_under_codex_home(tmp_path: Path) -> None:
    assert default_session_store_path(str(tmp_path)) == (
        tmp_path / "gateway" / "discord-channel-sessions.json"
    )
