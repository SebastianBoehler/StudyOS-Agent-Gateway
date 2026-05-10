import tomllib
from pathlib import Path

from study_discord_agent.automation_templates import (
    STUDYOS_GITHUB_TRIAGE_ID,
    render_github_triage_toml,
    seed_automation_templates,
)


def test_seed_automation_templates_writes_paused_template(tmp_path: Path) -> None:
    written = seed_automation_templates(str(tmp_path))
    template_dir = tmp_path / "automation-templates" / STUDYOS_GITHUB_TRIAGE_ID
    automation = template_dir / "automation.toml"
    memory = template_dir / "memory.md"

    assert automation in written
    assert memory in written
    assert 'status = "PAUSED"' in automation.read_text(encoding="utf-8")
    assert 'rrule = "RRULE:FREQ=MINUTELY;INTERVAL=30"' in automation.read_text(encoding="utf-8")
    assert not (tmp_path / "automations" / STUDYOS_GITHUB_TRIAGE_ID).exists()


def test_seed_automation_templates_can_install_active_without_overwrite(tmp_path: Path) -> None:
    active_dir = tmp_path / "automations" / STUDYOS_GITHUB_TRIAGE_ID
    active_dir.mkdir(parents=True)
    automation = active_dir / "automation.toml"
    automation.write_text("custom = true\n", encoding="utf-8")

    seed_automation_templates(str(tmp_path), install_active=True)

    assert automation.read_text(encoding="utf-8") == "custom = true\n"
    assert (active_dir / "memory.md").exists()


def test_github_triage_template_is_valid_toml() -> None:
    data = tomllib.loads(render_github_triage_toml("PAUSED"))

    assert data["id"] == STUDYOS_GITHUB_TRIAGE_ID
    assert data["kind"] == "cron"
    assert data["status"] == "PAUSED"
    assert data["cwds"] == ["/workspace"]
