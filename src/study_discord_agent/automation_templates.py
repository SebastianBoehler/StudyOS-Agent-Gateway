from pathlib import Path

STUDYOS_GITHUB_TRIAGE_ID = "studyos-github-triage"

STUDYOS_GITHUB_TRIAGE_PROMPT = """
Inspect the StudyOS GitHub repository for new or recently updated issues,
pull requests, review comments, and discussion that needs follow-up.

Use the authenticated GitHub CLI. Start from the repository mounted at
`/workspace`; if needed, resolve the remote with `git remote get-url origin`
or use the configured StudyOS repository.

Goals:
- Identify new issues that need clarification, acceptance criteria, labels, or
  duplicate consolidation.
- Identify pull requests that need reviewer attention, a concise
  Discord-friendly summary, or a response to review comments.
- Suggest next implementation steps only when scope is clear.
- Create or update PRs only for clearly scoped implementation work.
- Never merge PRs. Humans approve and merge.

Output:
- If there is actionable work, summarize the concrete items, issue/PR numbers,
  and recommended next step.
- If there is nothing useful to report, say so briefly and do not invent work.
""".strip()


def get_template_root(codex_home: str | None) -> Path:
    root = Path(codex_home or "~/.codex").expanduser()
    return root / "automation-templates"


def get_active_root(codex_home: str | None) -> Path:
    root = Path(codex_home or "~/.codex").expanduser()
    return root / "automations"


def render_github_triage_toml(status: str) -> str:
    escaped_prompt = STUDYOS_GITHUB_TRIAGE_PROMPT.replace('"""', '\\"\\"\\"')
    return f'''version = 1
id = "{STUDYOS_GITHUB_TRIAGE_ID}"
kind = "cron"
name = "StudyOS GitHub triage"
prompt = """{escaped_prompt}"""
status = "{status}"
rrule = "RRULE:FREQ=MINUTELY;INTERVAL=30"
model = "gpt-5.5"
reasoning_effort = "high"
execution_environment = "local"
cwds = ["/workspace"]
'''


def render_github_triage_memory() -> str:
    return """# StudyOS GitHub Triage Automation

This automation is intended for Codex app automation runners, not plain CLI
startup hooks. It should inspect the StudyOS repository on a recurring cadence
and report only actionable changes.

Human policy:
- Students approve and merge pull requests.
- Do not close issues or PRs unless explicitly asked.
- Prefer issue refinement and PR review summaries before implementation.
"""


def seed_automation_templates(codex_home: str | None, install_active: bool = False) -> list[Path]:
    written: list[Path] = []
    written.extend(_write_automation(get_template_root(codex_home), "PAUSED", overwrite=True))
    if install_active:
        written.extend(_write_automation(get_active_root(codex_home), "ACTIVE", overwrite=False))
    return written


def _write_automation(root: Path, status: str, overwrite: bool) -> list[Path]:
    directory = root / STUDYOS_GITHUB_TRIAGE_ID
    directory.mkdir(parents=True, exist_ok=True)

    automation_path = directory / "automation.toml"
    memory_path = directory / "memory.md"
    written: list[Path] = []

    if overwrite or not automation_path.exists():
        automation_path.write_text(render_github_triage_toml(status), encoding="utf-8")
        written.append(automation_path)
    if overwrite or not memory_path.exists():
        memory_path.write_text(render_github_triage_memory(), encoding="utf-8")
        written.append(memory_path)

    return written
