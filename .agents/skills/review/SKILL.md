---
name: review
description: >-
  Review one git commit against repo conventions, fix every tree issue found
  (including nits), report message/trailer hygiene only, then land tree fixes
  as a new follow-up commit. Triggers: `r` or `r <sha-or-ref>` (including
  `r HEAD`); a message that is only a commit SHA/ref; `review <sha-or-ref>`;
  review-and-fix; polish the tip; run the review skill. Do not use for
  PR/issue creation, history rewrite, or show/explain/log of a commit without
  the review-and-fix loop.
---

# Review one commit, then fix

Read [git-commits](../git-commits/SKILL.md) before any commit this skill creates.

## Triggers

Any of these invoke this skill (same workflow):

| Input | Target |
|-------|--------|
| `r` | `HEAD` |
| `r <sha-or-ref>` | that commit (`r HEAD` ok) |
| message that is **only** a SHA / short SHA / ref | that commit |
| `review <sha-or-ref>`, review-and-fix, polish the tip, run the review skill | named or `HEAD` |

Do **not** treat show / explain / `git log` / questions like “what changed in this commit” as this skill.

## Goal

1. Review **one** commit (default: `HEAD`)
2. Fix **all tree** findings, including minor nits; report message hygiene only
3. Land tree fixes as a **new** commit — never amend unless the user explicitly asks

If there are no tree findings, say so and stop (no empty commit). Still report message hygiene when present.

## Select the commit

- Resolve the target from [Triggers](#triggers); default `HEAD` when unset
- If the user names a subject / “the brew commit”, resolve to that one commit
- Review **that commit’s diff only** (`git show <sha>` / `git diff <sha>^!`), not the whole branch
- Do not expand scope to unrelated dirty files from other agents (see [AGENTS.md](../../../AGENTS.md) multi-agent rules)

## Review

Check the commit against [AGENTS.md](../../../AGENTS.md) and surrounding code. Look for:

- Incorrect behavior, edge cases, broken failure propagation (silent fallbacks, swallowed errors)
- Intentional behavior removed or “cleaned up” without asking (aliases, commented skips, platform workarounds)
- Style drift: duplication, parallel defaults, comments that restate the code, vague names
- Python / shell norms in [AGENTS.md](../../../AGENTS.md) (3.10+, `set -e`, no interactive prompts in automation, POSIX/BSD-safe flags)
- Commit message / trailers vs [git-commits](../git-commits/SKILL.md) (wrong gitmoji, agent `Co-authored-by`, missing `Assisted-by` when the diff was agent-helped) — message hygiene, report only
- Plan drift: if the commit touches something covered by [`.agents/plans/`](../../plans/), note plan updates needed

Severity is for the summary only — **fix tree nits too**, not only blockers.

Message or trailer problems on the **reviewed** commit itself (wrong gitmoji, bad `Assisted-by`, etc.) are **report-only**. They need a history rewrite ([message-only rewrite](../git-commits/SKILL.md#message-only-rewrite)), not a tree follow-up — leave the decision to the human. Do not amend or message-only rewrite for hygiene findings as part of this skill.

### Out of scope

- Do not run `script/setup` / `doit` / brew/port/mas mutations
- Do not push, force-push, or rewrite history (including message-only rewrite for hygiene findings)
- Do not add `Acked-by` / `Reviewed-by` (human-only; see [git-commits](../git-commits/SKILL.md))
- Do not invent `ports.txt` / `mas.txt` / `setapp.txt` contents

## Report, then fix

Before editing, give a short review (agree/disagree style not required here):

```
Commit: <short-sha> <subject>

Tree findings (→ fix):
- <finding>
- …

(or: No tree findings.)

Message hygiene (report only; human decides on rewrite):
- <finding>
- …

(or: No message hygiene findings.)
```

Use each section’s `(or: …)` line instead of bullets when that section is empty.

Then apply every **tree** fix in the working tree. Prefer the smallest change that addresses the finding. If a finding needs a product/design choice, ask — do not guess. Do not rewrite the reviewed commit’s message.

When fixes touch code that `script/check` covers, run the relevant checks (or `sh script/check`) before committing.

If a plan file should track the fix, update it in the **same** turn ([AGENTS.md — Plans](../../../AGENTS.md#plans)).

## Commit the fixes

New commit only. Stage **only** files this review-fix changed.

- Message: pick gitmoji from the **primary** nature of the fixes (`:bug:` for real bugs, `:art:` for refactor/clarity, `:memo:` for docs/plans, `:zzz:` for chore). Subject should say it is review follow-up when that helps (e.g. `:art: review follow-up: tighten setup error paths`).
- Body: what landed; optional one line that it follows review of `<short-sha>`.
- Trailers: `Assisted-by` for this session’s model (required when this session produced the fix diff). Do **not** copy review trailers onto the fix commit.
- Report the new commit hash when done.

### Amend (opt-in only)

Amend folds **tree** fixes into the reviewed tip — not message hygiene (still report-only above). Use **only** if the user explicitly asks **and** all of:

- Tip is the reviewed commit
- Not pushed (or user accepts rewrite; still never force-push to `master`)
- Tip has no `Acked-by` / `Reviewed-by` yet
- Working tree changes belong in that same story

Otherwise keep the new-commit path and say why amend was skipped.

## Done

- Summarize what changed (brief)
- Hashes: reviewed commit → fix commit (or “clean, no fix commit”)
