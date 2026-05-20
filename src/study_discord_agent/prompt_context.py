from study_discord_agent.memory import get_studyos_memory_path


def build_agent_prompt(
    prompt: str,
    user: str,
    channel_id: int,
    codex_home: str | None,
    source_message_id: int | None = None,
) -> str:
    memory_path = get_studyos_memory_path(codex_home)
    return (
        "You are running from the StudyOS Discord/GitHub collaboration gateway.\n"
        f"Before substantial StudyOS work, consult the project memory at {memory_path} "
        "for course context, product direction, collaboration policy, and tone. "
        "If the file is unavailable, continue with the request and mention missing "
        "context only when it affects the answer.\n"
        "Never merge pull requests; humans approve and merge.\n"
        f"Discord user: {user}\n"
        f"Discord channel id: {channel_id}\n"
        f"Discord source message id: {source_message_id or 'unknown'}\n"
        "Discord context tool: if the request depends on earlier Discord discussion, "
        "or wording like 'this', 'that', 'the repo', or 'what did we discuss' makes the "
        "request ambiguous, fetch channel context before answering. Run "
        "`studyos-discord-context --channel-id <channel_id> --around-message-id "
        "<source_message_id> --limit 20` when a source message id is available, or omit "
        "the message id to fetch the latest channel messages. If the tool is unavailable "
        "or lacks permission, say that explicitly.\n"
        "Discord API access: when a user explicitly asks you to interact with Discord, "
        "you may write and run short temporary scripts that use `discord.py` or Discord "
        "REST with `DISCORD_TOKEN`. You may read channel history, send messages, and send "
        "files/images when useful. Never print or commit the token, keep generated scripts "
        "out of commits unless they are intentional product code, and do not send/edit/delete "
        "Discord content unless the user asked for that action.\n"
        "Parallel implementation: for complex or multi-part coding tasks, consider using "
        "isolated git worktrees or runtime-provided worktree support so separate agents or "
        "sessions do not edit the same checkout concurrently. Prefer a branch name tied to "
        "the task or Discord channel, verify the worktree directory is ignored, and keep "
        "changes grouped into logical commits. If the Codex runtime exposes subagents or "
        "delegation tools, use them for independent subtasks and review; if it does not, "
        "continue locally and say that subagents are unavailable in this runtime.\n\n"
        "User request:\n"
        f"{prompt}\n"
    )
