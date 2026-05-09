import sys

import pytest

from study_discord_agent.agent import AgentGateway


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
