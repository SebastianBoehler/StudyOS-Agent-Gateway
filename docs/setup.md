# Setup Guide

## Discord

1. Create an application in the Discord Developer Portal.
2. Add a bot user and copy the bot token into `DISCORD_TOKEN`.
3. Invite the bot with `bot` and `applications.commands` scopes.
4. Copy the target PR channel ID into `DISCORD_PR_CHANNEL_ID`.
5. Optionally copy the server ID into `DISCORD_GUILD_ID` for faster slash command sync.

The bot does not need the privileged message-content intent for slash commands. Enable message content in the Discord Developer Portal only if `DISCORD_MESSAGE_AGENT_ENABLED=true` and you want `@bot please inspect this PR` style messages.

## GitHub

1. Create a webhook on the monorepo.
2. Set the payload URL to `https://<host>/webhooks/github`.
3. Set content type to `application/json`.
4. Generate a random secret and put it in both GitHub and `GITHUB_WEBHOOK_SECRET`.
5. Subscribe to pull request and issue events.

For the agent-server flow, prefer `gh auth login` in the deployment container. Keep `GITHUB_TOKEN` only as a non-interactive fallback.

## Deployment

Run locally:

```bash
studyos-discord-agent
```

Run with Docker Compose:

```bash
docker compose up --build -d
```

Expose port `8080` through a reverse proxy or tunnel for GitHub webhooks.

## Agent Runtime On The Server

The recommended StudyOS setup is:

1. Provision a small server or VM.
2. Clone the StudyOS course monorepo onto that server.
3. Deploy the agent image, which includes `gh`, `git`, SSH, Node/npm, and Codex.
4. Authenticate `gh` and Codex inside the running container.
5. Deploy this bot with `AGENT_COMMAND` pointing to the authenticated runtime.
6. Keep GitHub write permissions behind role checks and branch protection.

This lets the course share a few authenticated coding-agent instances instead of requiring every participant to own and configure one. Discord and GitHub become the common StudyOS interface.

The image contains tooling, but authentication belongs in Docker volumes, mounted config directories, or runtime environment variables. Never build tokens into the image.

For Codex and GitHub CLI auth inside the container:

```bash
export COURSE_REPO_PATH=/srv/studyos-monorepo
AGENT_COMMAND="codex exec --full-auto --cd /workspace -"
AGENT_WORKDIR=/workspace
docker compose -f docker-compose.agent.yml up --build -d
docker compose -f docker-compose.agent.yml exec studyos-discord-agent gh auth login
docker compose -f docker-compose.agent.yml exec studyos-discord-agent codex login
```

The provided agent image installs Node from the official Node image, GitHub CLI from GitHub's apt repository, and `@openai/codex` through npm. If your agent needs compilers, CUDA tools, or course-specific system packages, extend `Dockerfile.agent` for that course environment.

For Claude Code, run it directly on the host or build a sibling image with the Claude CLI installed:

```bash
AGENT_COMMAND="claude -p --permission-mode acceptEdits"
AGENT_WORKDIR=/srv/studyos-monorepo
```

Use `AGENT_AUTO_REVIEW_ENABLED=true` only after slash-command agent usage works reliably.

## Periodic GitHub Triage

Set:

```bash
GITHUB_POLL_ENABLED=true
GITHUB_POLL_INTERVAL_SECONDS=1800
GITHUB_POLL_LIMIT=20
```

The bot will periodically list open PRs and issues, build one prompt, and invoke the agent. This is the safest shape for "every 15 or 30 minutes, check comments/issues/PRs and act" because scheduling remains outside Discord message handling and can be disabled independently.

When `GITHUB_TOKEN` is not set, the poller and write helpers use `gh auth token`, so the container's `gh auth login` session is enough.

## External Agent Runtime

Set `AGENT_WEBHOOK_URL` to a service that accepts:

```json
{
  "prompt": "summarize open PRs",
  "source": "discord",
  "user": "name#0000",
  "channel_id": 123
}
```

The service must respond with:

```json
{"message": "agent response"}
```
