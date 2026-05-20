import sys
from pathlib import Path

import pytest

from study_discord_agent.agent import AgentGateway, build_codex_resume_args, extract_agent_result


@pytest.mark.asyncio
async def test_agent_command_receives_prompt_on_stdin() -> None:
    agent = AgentGateway(
        webhook_url=None,
        command=f"{sys.executable} -c \"import sys; print(sys.stdin.read().upper())\"",
        workdir=None,
        timeout_seconds=10,
    )

    reply = await agent.ask("hello course", user="student", channel_id=123)

    assert "HELLO COURSE" in reply.message


@pytest.mark.asyncio
async def test_agent_command_extracts_final_json_message() -> None:
    command = (
        f"{sys.executable} -c "
        "\"print('{\\\"type\\\":\\\"item.completed\\\",\\\"item\\\":{\\\"type\\\":"
        "\\\"agent_message\\\",\\\"text\\\":\\\"final answer\\\"}}')\""
    )
    agent = AgentGateway(
        webhook_url=None,
        command=command,
        workdir=None,
        timeout_seconds=10,
    )

    reply = await agent.ask("hello course", user="student", channel_id=123)

    assert reply.message == "final answer"


def test_extract_agent_result_reads_session_id() -> None:
    output = "\n".join(
        [
            '{"type":"session_meta","payload":{"id":"session-123"}}',
            '{"type":"item.completed","item":{"type":"agent_message","text":"done"}}',
        ]
    )

    result = extract_agent_result(output)

    assert result.session_id == "session-123"
    assert result.message == "done"


def test_build_codex_resume_args_keeps_supported_options() -> None:
    args = [
        "codex",
        "exec",
        "--json",
        "--dangerously-bypass-approvals-and-sandbox",
        "--cd",
        "/workspace",
        "-",
    ]

    resume_args = build_codex_resume_args(args, "session-123")

    assert resume_args == [
        "codex",
        "exec",
        "resume",
        "--json",
        "--dangerously-bypass-approvals-and-sandbox",
        "session-123",
        "-",
    ]


@pytest.mark.asyncio
async def test_codex_channel_session_resumes_after_first_turn(tmp_path: Path) -> None:
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import sys",
                "session = 'stored-session'",
                "if 'resume' in sys.argv:",
                "    text = 'resumed:' + ('stored-session' if session in sys.argv else 'missing')",
                "else:",
                "    text = 'started'",
                "print(json.dumps({'type': 'session_meta', 'payload': {'id': session}}))",
                "print(json.dumps({'item': {'type': 'agent_message', 'text': text}}))",
            ]
        ),
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    agent = AgentGateway(
        webhook_url=None,
        command=f"{fake_codex} exec --json --cd /workspace -",
        workdir=None,
        timeout_seconds=10,
        session_store_path=str(tmp_path / "sessions.json"),
    )

    first = await agent.ask("hello", user="student", channel_id=123, source_message_id=1)
    second = await agent.ask("again", user="student", channel_id=123, source_message_id=2)

    assert first.message == "started"
    assert first.session_id == "stored-session"
    assert second.message == "resumed:stored-session"
