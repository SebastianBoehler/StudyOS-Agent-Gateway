import subprocess
from pathlib import Path

import pytest

from study_discord_agent.discord_worktrees import (
    DiscordWorktreeManager,
    extract_org_repo_names,
)


def test_extract_org_repo_names_from_urls_and_full_names() -> None:
    text = (
        "Please inspect https://github.com/Tue-StudyOS/tue-api-wrapper/issues/1 "
        "and Tue-StudyOS/StudyOS-Agent-Gateway."
    )

    assert extract_org_repo_names(text) == ("tue-api-wrapper", "StudyOS-Agent-Gateway")


@pytest.mark.asyncio
async def test_prepare_creates_git_worktree_for_identified_repo(tmp_path: Path) -> None:
    canonical_root = tmp_path / "Tue-StudyOS"
    canonical = canonical_root / "example"
    _create_git_repo(canonical)
    manager = DiscordWorktreeManager(
        worktree_root=str(tmp_path / "discord-worktrees"),
        canonical_root=str(canonical_root),
    )

    workspace = await manager.prepare("work on Tue-StudyOS/example#1", 123)

    assert workspace.repo_name == "example"
    assert workspace.canonical_path == canonical
    assert workspace.path == tmp_path / "discord-worktrees" / "123" / "example"
    assert _git(workspace.path, "rev-parse", "--is-inside-work-tree") == "true"
    assert _git(workspace.path, "status", "--short") == ""


@pytest.mark.asyncio
async def test_prepare_uses_separate_thread_worktrees_for_same_repo(tmp_path: Path) -> None:
    canonical_root = tmp_path / "Tue-StudyOS"
    _create_git_repo(canonical_root / "example")
    manager = DiscordWorktreeManager(
        worktree_root=str(tmp_path / "discord-worktrees"),
        canonical_root=str(canonical_root),
    )

    first = await manager.prepare("work on Tue-StudyOS/example", 111)
    second = await manager.prepare("work on Tue-StudyOS/example", 222)

    assert first.path == tmp_path / "discord-worktrees" / "111" / "example"
    assert second.path == tmp_path / "discord-worktrees" / "222" / "example"
    assert first.path != second.path
    assert _git(first.path, "rev-parse", "--is-inside-work-tree") == "true"
    assert _git(second.path, "rev-parse", "--is-inside-work-tree") == "true"


@pytest.mark.asyncio
async def test_prepare_reuses_thread_repo_worktree_for_followup(
    tmp_path: Path,
) -> None:
    canonical_root = tmp_path / "Tue-StudyOS"
    canonical = canonical_root / "example"
    _create_git_repo(canonical)
    manager = DiscordWorktreeManager(
        worktree_root=str(tmp_path / "discord-worktrees"),
        canonical_root=str(canonical_root),
    )

    first = await manager.prepare("work on Tue-StudyOS/example", 123)
    followup = await manager.prepare("now adjust the same file", 123)

    assert followup.repo_name == "example"
    assert followup.canonical_path == canonical
    assert followup.path == first.path


@pytest.mark.asyncio
async def test_prepare_uses_channel_root_when_repo_is_ambiguous(tmp_path: Path) -> None:
    manager = DiscordWorktreeManager(worktree_root=str(tmp_path / "discord-worktrees"))

    workspace = await manager.prepare("please inspect the repo from the thread", 123)

    assert workspace.repo_name is None
    assert workspace.path == tmp_path / "discord-worktrees" / "123"
    assert workspace.path.is_dir()


def _create_git_repo(path: Path) -> None:
    path.mkdir(parents=True)
    _run(path, "git", "init")
    _run(path, "git", "config", "user.email", "test@example.invalid")
    _run(path, "git", "config", "user.name", "Test User")
    (path / "README.md").write_text("# Example\n", encoding="utf-8")
    _run(path, "git", "add", "README.md")
    _run(path, "git", "commit", "-m", "init")


def _git(path: Path, *args: str) -> str:
    return _run(path, "git", *args)


def _run(path: Path, *args: str) -> str:
    result = subprocess.run(
        args,
        cwd=path,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()
