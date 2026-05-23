import subprocess
from collections.abc import Sequence
from typing import Any

import pytest

from study_discord_agent.git_identity import ensure_git_identity_from_gh


def test_ensure_git_identity_from_gh_sets_missing_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(args: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        del kwargs
        command = list(args)
        calls.append(command)
        if command[:4] == ["git", "config", "--global", "--get"]:
            return subprocess.CompletedProcess(command, 1, stdout="")
        if command == ["gh", "api", "/user", "--jq", ".login"]:
            return subprocess.CompletedProcess(command, 0, stdout="SebastianBoehler\n")
        if command == ["gh", "api", "/user", "--jq", ".id"]:
            return subprocess.CompletedProcess(command, 0, stdout="27767932\n")
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    ensure_git_identity_from_gh()

    assert ["git", "config", "--global", "user.name", "SebastianBoehler"] in calls
    assert [
        "git",
        "config",
        "--global",
        "user.email",
        "27767932+SebastianBoehler@users.noreply.github.com",
    ] in calls


def test_ensure_git_identity_from_gh_keeps_human_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(args: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        del kwargs
        command = list(args)
        calls.append(command)
        if command == ["git", "config", "--global", "--get", "user.name"]:
            return subprocess.CompletedProcess(command, 0, stdout="Student Dev\n")
        if command == ["git", "config", "--global", "--get", "user.email"]:
            return subprocess.CompletedProcess(command, 0, stdout="student@example.com\n")
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(subprocess, "run", fake_run)

    ensure_git_identity_from_gh()

    assert calls == [
        ["git", "config", "--global", "--get", "user.name"],
        ["git", "config", "--global", "--get", "user.email"],
    ]


def test_ensure_git_identity_from_gh_replaces_agent_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(args: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        del kwargs
        command = list(args)
        calls.append(command)
        if command == ["git", "config", "--global", "--get", "user.name"]:
            return subprocess.CompletedProcess(command, 0, stdout="Codex\n")
        if command == ["git", "config", "--global", "--get", "user.email"]:
            return subprocess.CompletedProcess(command, 0, stdout="codex@openai.com\n")
        if command == ["gh", "api", "/user", "--jq", ".login"]:
            return subprocess.CompletedProcess(command, 0, stdout="SebastianBoehler\n")
        if command == ["gh", "api", "/user", "--jq", ".id"]:
            return subprocess.CompletedProcess(command, 0, stdout="27767932\n")
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    ensure_git_identity_from_gh()

    assert ["git", "config", "--global", "user.name", "SebastianBoehler"] in calls
    assert [
        "git",
        "config",
        "--global",
        "user.email",
        "27767932+SebastianBoehler@users.noreply.github.com",
    ] in calls
