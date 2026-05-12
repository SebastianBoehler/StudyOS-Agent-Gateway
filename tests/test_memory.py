from pathlib import Path

from study_discord_agent.memory import ensure_studyos_memory
from study_discord_agent.prompt_context import build_agent_prompt


def test_ensure_studyos_memory_creates_default_entrypoint(tmp_path: Path) -> None:
    path = ensure_studyos_memory(str(tmp_path))
    text = path.read_text()

    assert path.name == "studyos-course.md"
    assert "Build your own StudyOS" in text
    assert "Modern Agentic" in text
    assert "Codex Runtime And Automations" in text
    assert "Python heartbeat" not in text
    assert "automation templates" in text


def test_build_agent_prompt_points_to_memory(tmp_path: Path) -> None:
    prompt = build_agent_prompt("list tickets", "student", 123, str(tmp_path), 456)

    assert str(tmp_path / "memories" / "studyos-course.md") in prompt
    assert "Discord source message id: 456" in prompt
    assert "studyos-discord-context --channel-id <channel_id>" in prompt
    assert "User request:\nlist tickets" in prompt


def test_ensure_studyos_memory_appends_missing_sections(tmp_path: Path) -> None:
    memory_dir = tmp_path / "memories"
    memory_dir.mkdir()
    path = memory_dir / "studyos-course.md"
    path.write_text("# StudyOS Agent Memory\n\nLocal notes stay here.\n", encoding="utf-8")

    ensured_path = ensure_studyos_memory(str(tmp_path))
    text = ensured_path.read_text(encoding="utf-8")

    assert ensured_path == path
    assert "Local notes stay here." in text
    assert "Codex Runtime And Automations" in text
    assert "Python heartbeat" not in text
