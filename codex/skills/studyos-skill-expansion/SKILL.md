---
name: studyos-skill-expansion
description: Create, update, or refine StudyOS Codex skills for recurring workflows. Use when the user asks for a new skill, skill creator flow, self-expansion, reusable workflow capture, procedure hardening, or when a completed task reveals a repeatable StudyOS workflow that should become or patch a skill.
---

# StudyOS Skill Expansion

## Overview

Use this skill to expand the StudyOS agent through Codex-native skills without
creating duplicate or vague workflow documents. Pair it with `$skill-creator`
for generic skill authoring rules.

## Creation Gate

Create or patch a skill only when the workflow is likely to recur:

- Several tool calls were needed to discover a stable procedure.
- A user corrected the expected workflow or review criteria.
- A deployment, auth, Discord, GitHub, artifact, or validation path was
  non-obvious.
- The same instructions would otherwise be repeated in prompts, comments, or
  memory.

Do not create a skill for one-off facts, noisy logs, secrets, preferences, or
project details that belong in memory.

## Placement

Choose the smallest useful scope:

- Target repo workflow: `.agents/skills/<skill-name>/SKILL.md` in that repo.
- StudyOS-wide workflow: `codex/skills/<skill-name>/SKILL.md` in this gateway
  repo, seeded into `/etc/codex/skills` by the agent image.
- Local-only experiment: `$HOME/.agents/skills/<skill-name>/`.

If a matching skill already exists, patch it instead of creating another skill.

## Authoring Workflow

1. Search existing skills by name, description, and body.
2. Invoke or consult `$skill-creator` for naming, frontmatter, structure, and
   validation rules.
3. Name skills in lowercase hyphen-case, under 64 characters.
4. Use only `name` and `description` in `SKILL.md` frontmatter.
5. Make the description trigger-rich: include task type, phrases users say, and
   boundaries.
6. Keep `SKILL.md` procedural and concise. Add `references/` only when details
   are too long or conditional to keep inline.
7. Add `agents/openai.yaml` with a default prompt that explicitly mentions the
   skill as `$skill-name`.
8. Avoid fallbacks, mock data, broad configurability, and speculative behavior.
9. Validate with `quick_validate.py` and the repo's seeded-skill tests.
10. Explain the new or patched skill and when it will trigger.

## Refinement Workflow

Patch an existing skill when a task exposes a precise improvement:

- Add the smallest missing command, decision branch, risk check, or validation
  step.
- Remove stale or wrong instructions rather than appending contradictory rules.
- Keep memory facts out of skill bodies unless the fact is necessary to execute
  the workflow.
- Update `agents/openai.yaml` only if the user-facing invocation metadata is
  stale.

## Verification

For gateway-seeded skills, run:

```bash
python3 /Users/sebastianboehler/.codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/<skill-name>
pytest tests/test_skill_seed_files.py
```

For broader gateway changes, also run `ruff check .`, `pyright`, and `pytest`.
