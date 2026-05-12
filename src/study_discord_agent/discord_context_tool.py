import argparse
import asyncio
import os
from typing import Any, NoReturn, cast

import httpx

DISCORD_API_BASE = "https://discord.com/api/v10"


def main() -> None:
    args = _parse_args()
    try:
        output = asyncio.run(
            fetch_context(
                channel_id=args.channel_id,
                limit=args.limit,
                before_message_id=args.before_message_id,
                around_message_id=args.around_message_id,
                token=os.environ.get("DISCORD_TOKEN"),
            )
        )
    except RuntimeError as exc:
        _fail(str(exc))
    print(output)


async def fetch_context(
    channel_id: int,
    limit: int,
    before_message_id: int | None,
    around_message_id: int | None,
    token: str | None,
) -> str:
    if not token:
        raise RuntimeError("DISCORD_TOKEN is required to fetch Discord context")
    if before_message_id and around_message_id:
        raise RuntimeError("Use only one of --before-message-id or --around-message-id")

    params: dict[str, int] = {"limit": limit}
    if before_message_id:
        params["before"] = before_message_id
    if around_message_id:
        params["around"] = around_message_id

    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}"}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, headers=headers, params=params)

    if response.status_code == 403:
        raise RuntimeError("Discord bot lacks permission to read that channel")
    if response.status_code == 404:
        raise RuntimeError("Discord channel or message was not found")
    response.raise_for_status()

    messages = cast(list[dict[str, Any]], response.json())
    messages.sort(key=lambda item: int(str(item.get("id", "0"))))
    return render_messages(channel_id, messages)


def render_messages(channel_id: int, messages: list[dict[str, Any]]) -> str:
    lines = [f"Discord context for channel {channel_id}:"]
    if not messages:
        lines.append("- No messages returned.")
        return "\n".join(lines)

    for message in messages:
        author = cast(dict[str, Any], message.get("author") or {})
        username = str(author.get("global_name") or author.get("username") or "unknown")
        bot_marker = " bot" if author.get("bot") else ""
        timestamp = str(message.get("timestamp") or "unknown-time")
        content = _message_content(message)
        lines.append(f"- [{timestamp}] {username}{bot_marker}: {content}")
    return "\n".join(lines)


def _message_content(message: dict[str, Any]) -> str:
    content = str(message.get("content") or "").strip()
    if not content and message.get("attachments"):
        content = "[attachment]"
    if not content and message.get("embeds"):
        content = "[embed]"
    content = " ".join(content.split())
    if len(content) <= 700:
        return content
    return content[:697].rstrip() + "..."


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch recent Discord channel messages for StudyOS agent context."
    )
    parser.add_argument("--channel-id", type=int, required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--before-message-id", type=int)
    parser.add_argument("--around-message-id", type=int)
    args = parser.parse_args()
    if args.limit < 1 or args.limit > 100:
        parser.error("--limit must be between 1 and 100")
    return args


def _fail(message: str) -> NoReturn:
    raise SystemExit(f"studyos-discord-context failed: {message}")
