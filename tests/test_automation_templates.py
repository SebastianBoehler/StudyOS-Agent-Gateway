import tomllib
from pathlib import Path

from study_discord_agent.automation_templates import (
    AUTOMATION_SPECS,
    STUDYOS_COORDINATOR_THREAD_ID,
    STUDYOS_GITHUB_TRIAGE_ID,
    STUDYOS_WEEKLY_DIGEST_ID,
    render_automation_toml,
    render_github_triage_toml,
    seed_automation_templates,
)


def test_seed_automation_templates_writes_paused_template(tmp_path: Path) -> None:
    written = seed_automation_templates(str(tmp_path))
    template_dir = tmp_path / "automation-templates" / STUDYOS_GITHUB_TRIAGE_ID
    weekly_dir = tmp_path / "automation-templates" / STUDYOS_WEEKLY_DIGEST_ID
    coordinator_dir = tmp_path / "automation-templates" / STUDYOS_COORDINATOR_THREAD_ID
    automation = template_dir / "automation.toml"
    memory = template_dir / "memory.md"

    assert automation in written
    assert memory in written
    assert (weekly_dir / "automation.toml") in written
    assert (coordinator_dir / "automation.toml") in written
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


def test_all_automation_templates_are_valid_toml() -> None:
    parsed = [tomllib.loads(render_automation_toml(spec, "PAUSED")) for spec in AUTOMATION_SPECS]

    ids = {item["id"] for item in parsed}
    assert STUDYOS_COORDINATOR_THREAD_ID in ids
    assert STUDYOS_WEEKLY_DIGEST_ID in ids
    for item in parsed:
        if item["kind"] == "heartbeat":
            assert item["target_thread_id"] == "REPLACE_WITH_CODEX_THREAD_ID"
        else:
            assert item["cwds"] == ["/workspace"]


def test_templates_encode_human_gate_and_weekly_digest_schedule() -> None:
    parsed = {
        item["id"]: item
        for item in [
            tomllib.loads(render_automation_toml(spec, "PAUSED")) for spec in AUTOMATION_SPECS
        ]
    }

    triage_prompt = parsed[STUDYOS_GITHUB_TRIAGE_ID]["prompt"]
    assert "Do not start implementation" in triage_prompt
    assert "human-gated" in triage_prompt
    assert parsed[STUDYOS_WEEKLY_DIGEST_ID]["rrule"] == (
        "RRULE:FREQ=WEEKLY;BYDAY=TH;BYHOUR=16;BYMINUTE=0"
    )
