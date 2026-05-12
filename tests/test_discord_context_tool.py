import pytest

from study_discord_agent.discord_context_tool import fetch_context, render_messages


def test_render_messages_formats_context_for_agent_reading() -> None:
    output = render_messages(
        123,
        [
            {
                "id": "1",
                "timestamp": "2026-05-09T18:07:00+00:00",
                "author": {"username": "Sebastian"},
                "content": "Can you brainstorm?",
            },
            {
                "id": "2",
                "timestamp": "2026-05-09T18:08:00+00:00",
                "author": {"username": "StudyOS Bot", "bot": True},
                "content": "Here are feature directions.",
            },
        ],
    )

    assert "Discord context for channel 123" in output
    assert "Sebastian: Can you brainstorm?" in output
    assert "StudyOS Bot bot: Here are feature directions." in output


@pytest.mark.asyncio
async def test_fetch_context_requires_token() -> None:
    with pytest.raises(RuntimeError, match="DISCORD_TOKEN"):
        await fetch_context(
            channel_id=123,
            limit=20,
            before_message_id=None,
            around_message_id=None,
            token=None,
        )
