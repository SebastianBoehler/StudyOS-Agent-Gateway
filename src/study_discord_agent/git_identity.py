import logging
import subprocess

logger = logging.getLogger(__name__)

AGENT_IDENTITY_MARKERS = ("codex", "studyos agent", "agent gateway", "openai")


def ensure_git_identity_from_gh() -> None:
    """Configure Git author from authenticated gh user when unset or agent-like."""
    current_name = _git_config("user.name")
    current_email = _git_config("user.email")
    if (
        current_name
        and current_email
        and not _looks_like_agent_identity(current_name, current_email)
    ):
        return

    login = _gh_user_field(".login")
    user_id = _gh_user_field(".id")
    if not login or not user_id:
        logger.warning("git identity not configured and authenticated gh user is unavailable")
        return

    _set_git_config("user.name", login)
    _set_git_config("user.email", f"{user_id}+{login}@users.noreply.github.com")
    logger.info("configured git author identity from authenticated GitHub user")


def _git_config(key: str) -> str | None:
    result = subprocess.run(
        ["git", "config", "--global", "--get", key],
        capture_output=True,
        check=False,
        text=True,
    )
    value = result.stdout.strip()
    return value or None


def _set_git_config(key: str, value: str) -> None:
    subprocess.run(
        ["git", "config", "--global", key, value],
        check=True,
        text=True,
    )


def _gh_user_field(jq: str) -> str | None:
    result = subprocess.run(
        ["gh", "api", "/user", "--jq", jq],
        capture_output=True,
        check=False,
        text=True,
    )
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def _looks_like_agent_identity(name: str, email: str) -> bool:
    identity = f"{name} {email}".lower()
    return any(marker in identity for marker in AGENT_IDENTITY_MARKERS)
