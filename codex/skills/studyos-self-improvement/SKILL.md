---
name: studyos-self-improvement
description: Preserve durable StudyOS agent learnings as memory or reusable Codex skills. Use after substantial StudyOS work, repeated workflows, user corrections, non-obvious tool errors, runtime/deployment discoveries, or explicit requests to remember, self-improve, create skills, update skills, or refine agent procedures.
---

# StudyOS Self Improvement

## Overview

Use this skill to turn one-off StudyOS agent experience into durable, reviewable
procedure. Treat memory as facts and preferences; treat skills as repeatable
workflows.

## Decision

Before writing anything, decide whether the learning is durable:

- Skip noisy one-off details, transient logs, secrets, credentials, personal
  data, and conclusions that are not likely to recur.
- Write memory for stable facts: repo layout, runtime paths, user preferences,
  deployment quirks, or project decisions.
- Write or patch a skill for reusable procedure: multi-step workflows, repeated
  debugging paths, validation commands, artifact handling, or review checklists.
  Use `$studyos-skill-expansion` for StudyOS skill creation or refinement.
- Prefer patching an existing skill over creating a near-duplicate skill.

## Storage Targets

Choose the narrowest durable surface:

- Course/gateway memory: add dated "Runtime Learnings" notes to
  `$CODEX_HOME/memories/studyos-course.md` for StudyOS-wide facts.
- Target repository memory: use gitignored `.learnings/` or `.journal/`
  Markdown files for repo-specific facts that should not become a workflow.
- Target repository skills: use `.agents/skills/<skill-name>/SKILL.md` for
  team-shared workflows that should travel with that repo.
- Gateway-seeded runtime skills: use `codex/skills/<skill-name>/SKILL.md` in
  this gateway repo for StudyOS-wide skills that should be exposed to the
  shared Codex container through `/etc/codex/skills`.
- Personal or host-local skills: use `$HOME/.agents/skills/<skill-name>/` only
  for local experiments that should not be checked into a project.

## Skill Update Workflow

When creating or updating a Codex skill:

1. Search existing skills before creating a new one.
2. Use `$skill-creator` guidance for structure, naming, frontmatter, and
   validation.
3. Keep `SKILL.md` concise and procedural. Move long reference material to
   `references/` only when it is actually needed.
4. Use lowercase hyphen-case names under 64 characters.
5. Include only `name` and `description` in YAML frontmatter.
6. Make the description trigger-rich because Codex sees it before the body.
7. Avoid fallbacks, mock workflows, speculative features, or broad preferences.
8. Never store secrets, raw tokens, private user data, or noisy conversation
   details.
9. Validate the skill with `quick_validate.py` when available; otherwise check
   the folder shape and frontmatter manually.
10. Mention the memory or skill update in the final response.

## Refinement Triggers

Patch a skill after a task when any of these occurred:

- The agent took a wrong path, then found a reliable correction.
- A user corrected the expected process or acceptance check.
- A command, API, deployment path, or auth profile behaved differently than
  expected.
- A workflow required several tool calls and is likely to recur.
- A validation step prevented a bad answer or caught a regression.

Keep the update surgical: add the smallest rule, command, or decision branch
that would have prevented the wasted step.

## Verification

For checked-in StudyOS skill changes:

- Run the narrowest relevant validation, typically
  `python3 <skill-creator>/scripts/quick_validate.py <skill-folder>` and the
  repository test that checks seeded skill files.
- If changing container skill seeding, verify the image copies
  `codex/skills/` to a Codex discovery path such as `/etc/codex/skills`.
- If validation cannot run, report the exact missing command, tool, or
  permission.
