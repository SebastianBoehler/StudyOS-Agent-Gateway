from dataclasses import dataclass
from pathlib import Path

STUDYOS_GITHUB_TRIAGE_ID = "studyos-github-triage"
STUDYOS_PR_REVIEW_NUDGE_ID = "studyos-pr-review-nudge"
STUDYOS_ISSUE_REFINEMENT_ID = "studyos-issue-refinement"
STUDYOS_IMPLEMENTATION_CANDIDATES_ID = "studyos-implementation-candidates"
STUDYOS_COORDINATOR_THREAD_ID = "studyos-coordinator-thread"
STUDYOS_WEEKLY_DIGEST_ID = "studyos-weekly-digest"

@dataclass(frozen=True)
class AutomationSpec:
    id: str
    kind: str
    name: str
    prompt: str
    rrule: str
    memory: str
    target_thread_id: str | None = None


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
- Do not start implementation, create branches, or create PRs from this
  unattended triage run.
- Treat implementation as human-gated: a student must explicitly ask the agent
  to implement an issue in Discord or in a GitHub issue comment.
- Never merge PRs. Humans approve and merge.

Output:
- If there is actionable work, summarize the concrete items, issue/PR numbers,
  and recommended next step.
- If there is nothing useful to report, say so briefly and do not invent work.
""".strip()

STUDYOS_PR_REVIEW_NUDGE_PROMPT = """
Inspect open StudyOS pull requests with the authenticated GitHub CLI.

Find PRs that are new, stale, missing reviewers, blocked by review comments, or
waiting for CI. Recommend reviewer attention without shaming anyone. Prefer
inviting 2 student reviewers for feature PRs and 1 reviewer for docs or small
maintenance PRs. Prefer channel nudges over direct pings unless reviewers are
already assigned or the PR is blocked. Never merge PRs.

Output a Discord-friendly summary with PR numbers, review status, suggested
reviewers if visible from GitHub metadata, and the smallest next action.
""".strip()

STUDYOS_ISSUE_REFINEMENT_PROMPT = """
Inspect open StudyOS issues with the authenticated GitHub CLI.

Find issues that are vague, duplicated, too broad, missing acceptance criteria,
or blocked on product/UX/API decisions. Ask concise clarifying questions and
suggest issue consolidation when useful. Do not start implementation from this
automation.

Output issue numbers and the exact refinement comment or next question that
would unblock the students.
""".strip()

STUDYOS_IMPLEMENTATION_CANDIDATES_PROMPT = """
Inspect open StudyOS issues and recent discussion with the authenticated GitHub
CLI.

Identify issues that look ready for implementation because scope, acceptance
criteria, and expected behavior are clear. Propose a small PR plan and tests.
Do not implement from this automation. Implementation requires a separate human
trigger such as a Discord mention asking the bot to implement an issue or a
GitHub issue comment that explicitly asks the agent to start. Never merge PRs.

Output ready candidates, why they are ready, and any remaining risks.
""".strip()

STUDYOS_COORDINATOR_THREAD_PROMPT = """
Continue the StudyOS coordinator thread. Review recent GitHub and Discord-facing
project state if available, keep track of blockers, review load, stale issues,
and implementation candidates. Keep context in this same thread. Never merge
PRs.

Only report when there is something actionable: blocked PRs, unclear tickets,
missing reviewers, ready implementation candidates, or a useful course-level
coordination update. Do not start implementation unless a human explicitly asked
the agent to implement a specific issue.
""".strip()

STUDYOS_WEEKLY_DIGEST_PROMPT = """
Create a weekly StudyOS repository digest from GitHub activity.

Summarize merged PRs, open PRs needing review, issues created or refined, stale
or duplicate tickets, blockers, and suggested next milestones for the course.
Keep it constructive and friendly. Never merge PRs.
""".strip()

AUTOMATION_SPECS: tuple[AutomationSpec, ...] = (
    AutomationSpec(
        id=STUDYOS_GITHUB_TRIAGE_ID,
        kind="cron",
        name="StudyOS GitHub triage",
        prompt=STUDYOS_GITHUB_TRIAGE_PROMPT,
        rrule="RRULE:FREQ=MINUTELY;INTERVAL=30",
        memory="Inspect issues, PRs, comments, and review activity. Report actionable changes.",
    ),
    AutomationSpec(
        id=STUDYOS_PR_REVIEW_NUDGE_ID,
        kind="cron",
        name="StudyOS PR review nudge",
        prompt=STUDYOS_PR_REVIEW_NUDGE_PROMPT,
        rrule="RRULE:FREQ=HOURLY;INTERVAL=2",
        memory="Invite review attention without noise. Prefer 2 reviewers for feature PRs.",
    ),
    AutomationSpec(
        id=STUDYOS_ISSUE_REFINEMENT_ID,
        kind="cron",
        name="StudyOS issue refinement",
        prompt=STUDYOS_ISSUE_REFINEMENT_PROMPT,
        rrule="RRULE:FREQ=HOURLY;INTERVAL=6",
        memory="Turn rough ideas into scoped issues before implementation.",
    ),
    AutomationSpec(
        id=STUDYOS_IMPLEMENTATION_CANDIDATES_ID,
        kind="cron",
        name="StudyOS implementation candidates",
        prompt=STUDYOS_IMPLEMENTATION_CANDIDATES_PROMPT,
        rrule="RRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0",
        memory="Find ready-to-implement issues, but do not start without human approval.",
    ),
    AutomationSpec(
        id=STUDYOS_COORDINATOR_THREAD_ID,
        kind="heartbeat",
        name="StudyOS coordinator thread",
        prompt=STUDYOS_COORDINATOR_THREAD_PROMPT,
        rrule="FREQ=MINUTELY;INTERVAL=30",
        memory="Long-lived course coordination thread. Replace target_thread_id before enabling.",
        target_thread_id="REPLACE_WITH_CODEX_THREAD_ID",
    ),
    AutomationSpec(
        id=STUDYOS_WEEKLY_DIGEST_ID,
        kind="cron",
        name="StudyOS weekly digest",
        prompt=STUDYOS_WEEKLY_DIGEST_PROMPT,
        rrule="RRULE:FREQ=WEEKLY;BYDAY=TH;BYHOUR=16;BYMINUTE=0",
        memory="Weekly course-level progress summary and next milestone suggestions.",
    ),
)


def get_template_root(codex_home: str | None) -> Path:
    root = Path(codex_home or "~/.codex").expanduser()
    return root / "automation-templates"


def get_active_root(codex_home: str | None) -> Path:
    root = Path(codex_home or "~/.codex").expanduser()
    return root / "automations"


def render_automation_toml(spec: AutomationSpec, status: str) -> str:
    escaped_prompt = spec.prompt.replace('"""', '\\"\\"\\"')
    body = f'''version = 1
id = "{spec.id}"
kind = "{spec.kind}"
name = "{spec.name}"
prompt = """{escaped_prompt}"""
status = "{status}"
rrule = "{spec.rrule}"
model = "gpt-5.5"
reasoning_effort = "high"
'''
    if spec.kind == "heartbeat":
        body += f'target_thread_id = "{spec.target_thread_id}"\n'
    else:
        body += 'execution_environment = "local"\ncwds = ["/workspace"]\n'
    return body


def render_github_triage_toml(status: str) -> str:
    return render_automation_toml(AUTOMATION_SPECS[0], status)


def render_automation_memory(spec: AutomationSpec) -> str:
    return f"""# {spec.name}

This automation is intended for Codex app automation runners, not plain CLI
startup hooks.

{spec.memory}

Human policy:
- Students approve and merge pull requests.
- Implementation starts only after a human explicitly asks for it in Discord or
  a GitHub issue comment.
- Do not close issues or PRs unless explicitly asked.
- Prefer issue refinement and PR review summaries before implementation.
"""


def seed_automation_templates(codex_home: str | None, install_active: bool = False) -> list[Path]:
    written: list[Path] = []
    written.extend(_write_automations(get_template_root(codex_home), "PAUSED", overwrite=True))
    if install_active:
        written.extend(_write_automations(get_active_root(codex_home), "ACTIVE", overwrite=False))
    return written


def _write_automations(root: Path, status: str, overwrite: bool) -> list[Path]:
    written: list[Path] = []
    for spec in AUTOMATION_SPECS:
        written.extend(_write_automation(root, spec, status, overwrite))
    return written


def _write_automation(
    root: Path,
    spec: AutomationSpec,
    status: str,
    overwrite: bool,
) -> list[Path]:
    directory = root / spec.id
    directory.mkdir(parents=True, exist_ok=True)

    automation_path = directory / "automation.toml"
    memory_path = directory / "memory.md"
    written: list[Path] = []

    if overwrite or not automation_path.exists():
        automation_path.write_text(render_automation_toml(spec, status), encoding="utf-8")
        written.append(automation_path)
    if overwrite or not memory_path.exists():
        memory_path.write_text(render_automation_memory(spec), encoding="utf-8")
        written.append(memory_path)

    return written
