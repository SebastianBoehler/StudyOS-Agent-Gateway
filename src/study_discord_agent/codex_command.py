import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast


@dataclass(frozen=True)
class AgentCommandResult:
    message: str
    session_id: str | None


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


def is_codex_exec_command(args: list[str]) -> bool:
    if len(args) < 2:
        return False
    return Path(args[0]).name == "codex" and args[1] == "exec"


def add_codex_image_args(args: list[str], image_paths: tuple[Path, ...]) -> list[str]:
    if not image_paths:
        return args
    image_args = _codex_image_args(image_paths)
    if "-" not in args:
        return [*args, *image_args]
    prompt_index = args.index("-")
    return [*args[:prompt_index], *image_args, *args[prompt_index:]]


def build_codex_resume_args(
    args: list[str],
    session_id: str | None,
    image_paths: tuple[Path, ...] = (),
) -> list[str]:
    if not session_id:
        return add_codex_image_args(args, image_paths)

    resume_args = [args[0], "exec", "resume"]
    resume_args.extend(_codex_resume_options(args[2:]))
    resume_args.extend(_codex_image_args(image_paths))
    resume_args.extend([session_id, "-"])
    return resume_args


def _codex_image_args(image_paths: tuple[Path, ...]) -> list[str]:
    args: list[str] = []
    for path in image_paths:
        args.extend(["-i", str(path)])
    return args


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
