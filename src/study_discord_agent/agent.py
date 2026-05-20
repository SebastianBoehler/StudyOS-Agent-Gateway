import asyncio
import json
import logging
import os
import shlex
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import httpx

from study_discord_agent.prompt_context import build_agent_prompt
from study_discord_agent.session_store import ChannelSessionStore, default_session_store_path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentReply:
    message: str
    session_id: str | None = None


@dataclass(frozen=True)
class AgentCommandResult:
    message: str
    session_id: str | None


class AgentGateway:
    def __init__(
        self,
        webhook_url: str | None,
        command: str | None,
        workdir: str | None,
        timeout_seconds: int,
        channel_sessions_enabled: bool = True,
        session_store_path: str | None = None,
        codex_home: str | None = None,
    ) -> None:
        self._webhook_url = webhook_url
        self._command = command
        self._workdir = workdir
        self._timeout_seconds = timeout_seconds
        self._channel_sessions_enabled = channel_sessions_enabled
        self._channel_locks: dict[int, asyncio.Lock] = {}
        store_path = session_store_path or str(default_session_store_path(codex_home))
        self._session_store = ChannelSessionStore(store_path)

    async def ask(
        self,
        prompt: str,
        user: str,
        channel_id: int,
        source_message_id: int | None = None,
    ) -> AgentReply:
        started_at = time.monotonic()
        logger.info("agent request started source_user=%s channel_id=%s", user, channel_id)
        if self._webhook_url:
            reply = await self._ask_webhook(prompt, user, channel_id, source_message_id)
        elif self._command:
            reply = await self._ask_command(prompt, user, channel_id, source_message_id)
        else:
            raise RuntimeError("Configure AGENT_WEBHOOK_URL or AGENT_COMMAND")

        elapsed = time.monotonic() - started_at
        logger.info(
            "agent request completed source_user=%s channel_id=%s elapsed_seconds=%.2f",
            user,
            channel_id,
            elapsed,
        )
        return reply

    async def _ask_webhook(
        self,
        prompt: str,
        user: str,
        channel_id: int,
        source_message_id: int | None,
    ) -> AgentReply:
        if not self._webhook_url:
            raise RuntimeError("AGENT_WEBHOOK_URL is not configured")

        payload = {
            "prompt": prompt,
            "source": "discord",
            "user": user,
            "channel_id": channel_id,
            "source_message_id": source_message_id,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self._webhook_url, json=payload)
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())

        message = data.get("message")
        if not isinstance(message, str) or not message.strip():
            raise RuntimeError("Agent response must contain a non-empty message")
        return AgentReply(message=message)

    async def _ask_command(
        self,
        prompt: str,
        user: str,
        channel_id: int,
        source_message_id: int | None,
    ) -> AgentReply:
        if not self._command:
            raise RuntimeError("AGENT_COMMAND is not configured")

        args = shlex.split(self._command)
        full_prompt = build_agent_prompt(
            prompt,
            user,
            channel_id,
            os.environ.get("CODEX_HOME"),
            source_message_id,
        )
        if self._uses_channel_sessions(args, source_message_id):
            lock = self._channel_locks.setdefault(channel_id, asyncio.Lock())
            async with lock:
                return await self._ask_codex_channel_session(args, full_prompt, channel_id)

        result = await self._run_command(args, full_prompt)
        return AgentReply(message=result.message, session_id=result.session_id)

    async def _ask_codex_channel_session(
        self,
        args: list[str],
        full_prompt: str,
        channel_id: int,
    ) -> AgentReply:
        session_id = self._session_store.get(channel_id)
        run_args = build_codex_resume_args(args, session_id) if session_id else args
        result = await self._run_command(run_args, full_prompt)
        if result.session_id:
            self._session_store.set(channel_id, result.session_id)
        return AgentReply(message=result.message, session_id=result.session_id)

    async def _run_command(self, args: list[str], full_prompt: str) -> AgentCommandResult:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self._workdir,
        )
        logger.info("agent command spawned pid=%s command=%s", process.pid, shlex.join(args))
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(full_prompt.encode("utf-8")),
                timeout=self._timeout_seconds,
            )
        except TimeoutError:
            process.kill()
            await process.wait()
            raise RuntimeError("Agent command timed out") from None

        if process.returncode != 0:
            error = stderr.decode("utf-8", errors="replace").strip()
            logger.warning("agent command failed returncode=%s error=%s", process.returncode, error)
            raise RuntimeError(f"Agent command failed: {error[:1000]}")

        output = stdout.decode("utf-8", errors="replace").strip()
        result = extract_agent_result(output)
        if not result.message:
            raise RuntimeError("Agent command produced no output")
        return result

    def _uses_channel_sessions(self, args: list[str], source_message_id: int | None) -> bool:
        return (
            self._channel_sessions_enabled
            and source_message_id is not None
            and _is_codex_exec_command(args)
        )


def extract_agent_result(output: str) -> AgentCommandResult:
    messages: list[str] = []
    session_id: str | None = None
    for line in output.splitlines():
        try:
            parsed: object = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue
        event = cast(dict[str, object], parsed)
        if event.get("type") == "session_meta":
            payload_obj = event.get("payload")
            if isinstance(payload_obj, dict):
                payload = cast(dict[str, object], payload_obj)
                value = payload.get("id")
                if isinstance(value, str) and value:
                    session_id = value
        item_obj = event.get("item")
        if not isinstance(item_obj, dict):
            continue
        item = cast(dict[str, object], item_obj)
        text = item.get("text")
        if item.get("type") == "agent_message" and isinstance(text, str):
            messages.append(text)

    if messages:
        return AgentCommandResult(message=messages[-1].strip(), session_id=session_id)
    return AgentCommandResult(message=output, session_id=session_id)


def _is_codex_exec_command(args: list[str]) -> bool:
    if len(args) < 2:
        return False
    return Path(args[0]).name == "codex" and args[1] == "exec"


def build_codex_resume_args(args: list[str], session_id: str | None) -> list[str]:
    if not session_id:
        return args

    resume_args = [args[0], "exec", "resume"]
    resume_args.extend(_codex_resume_options(args[2:]))
    resume_args.extend([session_id, "-"])
    return resume_args


def _codex_resume_options(options: list[str]) -> list[str]:
    copied: list[str] = []
    takes_value = {
        "-c",
        "--config",
        "--enable",
        "--disable",
        "-i",
        "--image",
        "-m",
        "--model",
        "-o",
        "--output-last-message",
        "--output-schema",
    }
    skip_with_value = {"-C", "--cd", "--add-dir", "-s", "--sandbox", "-a", "--ask-for-approval"}
    flag_options = {
        "--strict-config",
        "--dangerously-bypass-approvals-and-sandbox",
        "--dangerously-bypass-hook-trust",
        "--skip-git-repo-check",
        "--ignore-user-config",
        "--ignore-rules",
        "--json",
    }

    index = 0
    while index < len(options):
        value = options[index]
        if value == "-":
            index += 1
            continue
        if value in takes_value and index + 1 < len(options):
            copied.extend([value, options[index + 1]])
            index += 2
            continue
        if any(value.startswith(prefix + "=") for prefix in takes_value if prefix.startswith("--")):
            copied.append(value)
            index += 1
            continue
        if value in skip_with_value:
            index += 2
            continue
        if any(
            value.startswith(prefix + "=")
            for prefix in skip_with_value
            if prefix.startswith("--")
        ):
            index += 1
            continue
        if value in flag_options:
            copied.append(value)
        index += 1
    return copied
