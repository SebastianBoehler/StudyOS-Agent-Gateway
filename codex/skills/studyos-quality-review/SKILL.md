---
name: studyos-quality-review
description: Review StudyOS code changes for security, privacy, reliability, dead code, duplicate logic, regressions, missing validation, and maintainability. Use for PR reviews, pre-merge checks, "review this", "security review", "quality review", cleanup audits, or before claiming substantial StudyOS implementation work is ready.
---

# StudyOS Quality Review

## Overview

Use this skill to review StudyOS changes like a senior engineer. Lead with
actionable findings, prioritize real risk, and verify with the narrowest useful
commands.

## Review Stance

Start from the diff and surrounding contracts:

- Identify the changed files and any existing unrelated worktree changes.
- Read nearby code before judging intent or style.
- Check tests, docs, config, deployment paths, and runtime prompts when behavior
  crosses those boundaries.
- Prefer concrete bugs over broad style opinions.
- Do not invent issues. If a concern is speculative, label it as such and say
  what would verify it.

## Risk Checklist

For each changed area, check:

- Security and privacy: tokens, webhook secrets, Discord/GitHub IDs, auth
  profile routing, command execution, file upload roots, logs, and prompts.
- Reliability: explicit errors, retry behavior, race conditions, persistence,
  deployment volume behavior, and restart safety.
- Behavior: broken API contracts, changed prompt semantics, incorrect Discord
  thread/channel routing, artifact upload mistakes, or GitHub actor confusion.
- Code health: dead branches, unused helpers, duplicate logic, over-large files,
  unclear boundaries, hidden fallback behavior, and mock production data.
- Validation: missing tests for changed behavior, stale docs, or commands that
  should have been run before handoff.

## Review Procedure

1. Inspect `git status --short` and separate unrelated changes from the review
   target.
2. Inspect the relevant diff with line context.
3. Read the local implementation, tests, docs, and config that define the
   touched behavior.
4. Run focused checks when practical. For this gateway, prefer `ruff check .`,
   `pyright`, and `pytest`; for target repos, use their own documented checks.
5. Report findings first, ordered by severity, with file and line references.
6. Include open questions only when an answer changes the recommendation.
7. Keep summary secondary and short.

## Finding Format

Use this shape:

- Severity: `Critical`, `High`, `Medium`, or `Low`.
- Reference: clickable file path with the most relevant line.
- Issue: what can go wrong and under which condition.
- Fix direction: the smallest change likely to address it.

If there are no findings, say that clearly and mention remaining test gaps or
residual risk.

## Non-Goals

- Do not rewrite code during a pure review unless the user asked for fixes.
- Do not demand unrelated cleanup.
- Do not collapse separate concerns into one vague issue.
- Do not expose secrets or personal data in review output.
