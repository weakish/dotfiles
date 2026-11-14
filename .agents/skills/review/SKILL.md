---
name: review
description: >-
  Review one git commit; letter-label tree findings; wait for `r` / `r <sha>` /
  `review <sha>` / a bare SHA, then fix selected labels (`all`, `y`, `fix b,d`,
  `h`/`help`). Bare `t` amends HEAD when amend is allowed and there is
  work (tree fixes and/or message hygiene). After a tree amend, hand off `t`
  to another agent pane in the same Herdr tab when one is available; if not,
  only a Cursor/Grok pane may create the default review pair. Do not wait.
  They prompt this pane with `t` after their own tree amend until either side
  has no tree findings. Without Herdr, use headless ping-pong
  (`REVIEW_T_HEADLESS=1`, see Headless ping-pong).
  `review-and-fix` / polish the tip still lands a new follow-up commit
  when there are tree findings.
  Not for PR/issue creation or history rewrite (except bare `t` /
  explicit amend).
---

# Review one commit; fix after selection

Read the Contributing section of `AGENTS.md` and [git-commits](../git-commits/SKILL.md) before any
commit this skill creates (or amends).

## Triggers

Any of these invoke this skill. After a lettered report, how to parse `y` / `all` / labels / `help` is only in [Select items to fix](#select-items-to-fix).

| Input | Target / behavior |
|-------|-------------------|
| `r` | `HEAD` — report with letter labels; **wait** (do not fix yet) |
| `r <sha-or-ref>` | that commit — report; **wait** (`r HEAD` ok) |
| `t` | `HEAD` (the tip) — report, then [Bare t](#bare-t) (amend when allowed; if blocked, keep the report and stop with no edits). After a **tree** amend, [Ping-pong](#ping-pong) (handoff `t`; do not wait) |
| message that is **only** a SHA / short SHA / ref | that commit — report; **wait** |
| `review <sha-or-ref>`, run the review skill | named or `HEAD` — report; **wait** |
| `review-and-fix`, `review and fix`, polish the tip | named or `HEAD` — report, then fix **all** tree items in the same turn (same as `all`); land a **new** follow-up commit when there are tree findings (not amend) |
| `yes`, `y`, `continue`, `c`, bare `fix`, `all`, `fix all`, `fix b,d,e` / `b-d` / …, `h` / `help` / `h B,d`, `none`, `skip` | last lettered report — [Select items to fix](#select-items-to-fix) |

Do **not** treat show / explain / `git log` / questions like “what changed in this commit” as this skill.

## Goal

1. Review **one** commit (default: `HEAD`)
2. Report tree findings with **letter labels** (`B`/`b`, `D`/`d`, …; or letter+number when they do not fit — see below); report message hygiene (no letters)
3. Fix tree items: the user’s **selection** ([Select items to fix](#select-items-to-fix)), including nits they select. Same turn with no wait for a user selection:
   - bare `t` (always `HEAD`): when amend is allowed, follow [Bare t](#bare-t); after a tree amend, [Ping-pong](#ping-pong)
   - `review-and-fix` / `review and fix` / polish the tip (named or `HEAD`): fix every tree item (design-choice pause in [Report, then fix](#report-then-fix) still applies); land a new commit when there are tree findings
4. Land fixes:
   - **[Bare t](#bare-t):** amend into `HEAD` when amend is allowed and there is work (tree and/or message hygiene). After a **tree** amend, [Ping-pong](#ping-pong)
   - **Everything else** (`y` / `all` / label picks / `review-and-fix` / …): **new** follow-up commit when there are tree fixes — amend only if the user explicitly asks ([Amend (opt-in)](#amend-opt-in-only))

If a bare-`t` amend guard fails: follow [Bare t](#bare-t) (stop after the report; no tree or message edits). Do **not** add a separate end-of-turn prompt line.

If there are no tree findings:

- On `r` / bare SHA / `review <sha-or-ref>` / selection paths: say so and stop (no empty commit). Still report message hygiene when present (report-only).
- On `review-and-fix` / `review and fix` / polish the tip: say so and stop (no empty commit). Hygiene stays report-only.
- On bare `t` with amend allowed: follow [Bare t](#bare-t) — hygiene-only amend when needed; if neither tree nor hygiene findings, say so and stop. **No tree findings** also ends [Ping-pong](#ping-pong) (do not hand off).

On `r` / bare SHA / `review <sha-or-ref>`, stop after the report — do not fix yet, and do **not** add a separate end-of-turn prompt line (the letter labels in the report are enough). Same turn without waiting for a user selection:

- bare `t` when amend is allowed: follow [Bare t](#bare-t), then [Ping-pong](#ping-pong) after a tree amend
- bare `t` when amend is blocked: report and stop (no tree or message edits; no ping-pong)
- `review-and-fix` / `review and fix` / polish the tip: fix every tree item (design-choice pause still applies), then land a **new** commit when there were tree findings

## Select the commit

- Resolve the target from [Triggers](#triggers); default `HEAD` when unset
- If the user names a subject / “the foo commit”, resolve to that one commit
- Scope: **that commit only** (`git show <sha>` / `git diff <sha>^!` to see which paths changed), not the whole branch
- Read every changed file in full before judging the diff; do not rely on hunks or search snippets (see the current project's AGENTS.md)
- Do not expand scope to unrelated dirty files from other agents (see the current project's AGENTS.md multi-agent rules)

## Review

Check the commit against the current project's AGENTS.md.

If in a monorepo:

- When the diff touches a project directory, also follow that project’s `AGENTS.md` and project-local `.agents/skills/` if present.
- Match the language and conventions of the project you are in — do not impose another project’s stack.

Look for:

- Incorrect behavior, edge cases, broken failure propagation (silent fallbacks, swallowed errors)
- Intentional behavior removed or “cleaned up” without asking (aliases, redirects, platform workarounds, commented skips)
- Style drift: duplication, parallel defaults, comments that restate the code, vague names
- Commit message / trailers vs the Contributing section of `AGENTS.md` and [git-commits](../git-commits/SKILL.md) (wrong gitmoji, agent `Co-authored-by`, missing `Assisted-by` when the diff was agent-helped) — message hygiene

Report tree nits too, not only blockers. Mark case encodes the agent’s recommendation (see below).

Message or trailer problems on the **reviewed** commit:

- **[Bare t](#bare-t):** apply them when amending
- **All other triggers:** **report-only** unless the user explicitly asks to amend ([Amend (opt-in)](#amend-opt-in-only)). Do not rewrite the reviewed commit’s message as part of a new follow-up commit.

### Out of scope

- Do not push, force-push, or push/merge to `master` (even if asked)
- Do not rewrite history except: bare `t` amend (below), or an explicit user-requested amend that passes [Amend (opt-in)](#amend-opt-in-only)
- Do not invent content for other agents’ dirty/untracked files
- If in a monorepo, do not invent a root check/fmt toolchain; use each project’s documented tasks/scripts only

## Report, then fix

Before editing, give a short review (agree/disagree style not required here).
Default hygiene header below is for `r` / selection / `review-and-fix`. On bare `t`, check amend guards first and use the header in the next subsection — do not copy this default when amend is allowed.

```
Commit: <short-sha> <subject>

Tree findings:
- B. <finding>
- d. <finding>
- …

(or when letter+number — e.g. `- B1. <finding>`, `- b2. <finding>`, `- D1. <finding>`)

(or: No tree findings.)

Message hygiene (report only unless user asks to amend):
- <finding>
- …

(or: No message hygiene findings.)
```

On bare `t`, check amend guards before choosing the hygiene header (findings still unlettered). Do not copy the default `report only` header when amend is allowed:

- Amend allowed:

```
Message hygiene (will apply on amend):
- <finding>
- …

(or: No message hygiene findings.)
```

- Amend blocked: keep `Message hygiene (report only unless user asks to amend):`, then after the report say why amend is blocked (do not edit)

**Letter labels:** assign labels to tree findings only; keep the mapping stable for the session. Message-hygiene bullets are not lettered (not tree-fixable via label selection).

**Mark case (report only; selection ignores case):**
- **Uppercase** (`B`, `D1`, …): agent **recommends** a fix
- **Lowercase** (`b`, `d1`, …): fine to **keep as is** (still selectable if the user wants it fixed)

**Reserved letters** (never use as single-letter labels or as letter+number category letters): `a`, `c`, `f`, `h`, `n`, `r`, `s`, `t`, `y` — collide with `all`, `yes`/`y`/`continue`/`c`, `h`/`help`, `skip`/`none`, review (`r`), bare `t`, fix-ish replies, and similar one-letter inputs. Assign from the remaining alphabet in order: `b`, `d`, `e`, `g`, `i`, `j`, `k`, `l`, `m`, `o`, `p`, `q`, `u`, `v`, `w`, `x`, `z` (17 letters). Write each mark upper or lower for recommendation; letter **identity** for ordering, spans, and categories ignores case. Selection examples use assignable letters only (not reserved).

Use **one** label scheme per report — never mix single-letter and letter+number labels in the same report:

| Count | Scheme | Examples |
|-------|--------|----------|
| ≤ 17 | single letter (non-reserved; case = recommendation) | the 17-letter list above, in order (`B`/`b`, `D`/`d`, `E`/`e`, …) |
| > 17 | letter + number | `B1`, `b2`, `D1`, `d2`, `D3`, … |

When a report has more than 17 tree findings, label **all** of them in letter+number form (do not use single letters for the first 17 and switch partway). **Categorize when possible:** the letter identity (case-insensitive) groups related findings (non-reserved only); numbers are sequential within that category (`B1`, `b2`, … then `D1`, …). When findings do not group naturally (e.g. 19 unrelated items), a single category is fine (`B1` … `b19`).

Use each section’s `(or: …)` line instead of bullets when that section is empty.

The `No tree findings.` and `Need user decision.` lines are **load-bearing**: headless ping-pong stop detection (see [Headless ping-pong](#headless-ping-pong)) scans each pass’s output for those literal strings. Keep that exact wording, and do not rephrase it when editing this report format.

When applying tree fixes — from [Select items to fix](#select-items-to-fix), bare `t` when amend is allowed, or `review-and-fix` / polish the tip — prefer the smallest change that addresses the finding. On selection paths, apply only the chosen labels; on those same-turn fix paths, fix every tree item. If a finding needs a product/design choice, ask — do not guess; stop with no commit or amend until the user replies. Do not rewrite the reviewed commit’s message on selection / `review-and-fix` paths (report-only hygiene) unless the user explicitly asks to amend ([Amend (opt-in)](#amend-opt-in-only)).

In a headless pass (`REVIEW_T_HEADLESS=1`) there is nobody to ask: do not call interactive input tools. Print the report, then the literal line `Need user decision.` followed by the questions, and exit 0 with no edits and no amend. The driver stops and the invoking agent relays the questions to the human.

### Select items to fix

Parse the user’s selection from the latest lettered report in this session. Syntax depends on which label scheme that report used.

**Single-letter reports** (≤ 17 findings):

| Form | Meaning |
|------|---------|
| `b`, `fix d` | one item (case-insensitive) |
| `b,d,e` | items b, d, and e |
| `fix b,d,e` | same (`fix` prefix optional) |
| `b-d` | letter hyphen span (single-letter labels; see Both schemes) |
| `b,d-g,i` | mix of singles and ranges |

**Letter+number reports** (> 17 findings):

| Form | Meaning |
|------|---------|
| `b1`, `fix d2` | one item (case-insensitive) |
| `b1,b3,d2` | listed items |
| `b1-4` | same-prefix numeric range (see Both schemes) |
| `b` | every label with prefix `b`/`B` (b1, B2, …) |
| `b-e` | letter hyphen span (category prefixes; see Both schemes) |

Cross-prefix numbered ranges (e.g. `d3-g4`) are **not** supported — ask the user to confirm before guessing.

**Both schemes:**

- Selection matching is **case-insensitive** (`B,d` = `b,D` = findings marked `B`/`b` and `D`/`d`). Mark case in the report still encodes recommendation.
- Ignore spaces around commas and hyphens.
- **Parse order:** keyword forms first (`t`, `y`, bare `fix`, `fix y`, `help`, `h B,d`, `all`, …). Bare `t` is always a new review of `HEAD` ([Bare t](#bare-t)), never a label selection. The phrase **polish the tip** is the `review-and-fix` path (new commit), not `t`. Reserved-letter **pause** (below) applies only when a reserved letter is a **label** token in a list or scoped argument (e.g. `b,h,d`, `help h`), not when it is consumed as part of a keyword form (including bare `fix` / bare `t`).
- No prior lettered report in session: say so; do not invent findings.
- `yes`, `y`, `continue`, `c`, bare `fix` (`fix` prefix optional on the others): every **recommended** tree finding (uppercase marks only). Bare `fix` (message is **only** this word) is the same as `y`. If none are recommended, say so and do not fix.
- `h`, `help` (message is **only** this word): explain **more detail** on **every** tree finding (upper and lower marks) — do **not** fix; then wait for selection as after the original report. If there are no tree findings, say so.
- `h <labels>`, `help <labels>`: explain more detail on the listed labels / spans only (same selection syntax as fix forms, case-insensitive; upper or lower marks). Span/range pause rules apply. Unknown labels: say which, explain the rest. Do **not** fix; then wait for selection.
- `all`, `fix all`: every tree finding (upper and lower).
- `none`, `skip`: no tree edits, no fix commit.
- Empty message (nothing else): ask which labels to fix (briefly; no end-of-turn prompt line).
- Other instructions, no letter selection: implicit `none`/`skip` for review fixes.
- **Letter hyphen spans** (`b-d`, `b-e`) are **inclusive**. Skip **reserved** letters inside the span; match labels or prefixes **assigned in this report** (letter identity, ignoring case) — e.g. single-letter `b-d` → `b`/`B` and `d`/`D` (not `c`); letter+number `b-e` → prefixes `b`/`B`, `d`/`D`, `e`/`E`. If a non-reserved letter in the span was never assigned in this report, **pause** — say which and ask for confirmation; do not apply any part of the selection until the user replies.
- **Same-prefix numeric ranges** (`b1-4`) are **inclusive** over sequential numbers within that prefix (case-insensitive). Labeling assigns `1`, `2`, … without gaps for that letter identity, so a missing number inside the range should not occur when the report followed this skill. If the range runs past the highest assigned number for that prefix (e.g. `b1-4` when only `b1`–`B3` exist), **pause** — say which and ask for confirmation; do not apply any part of the selection until the user replies.
- Unknown or out-of-range labels (not part of a letter span or numeric range token): say which, continue with the rest.
- A **reserved** letter used as a **label** token in a list or scoped argument (e.g. `b,h,d`, `help h`) is **invalid** — **pause**, say which, and ask for confirmation; do not apply or explain until the user replies.

When fixes touch code a project documents checks/tests for, run those project-local tasks before committing. After creating or modifying a test, run that test until it passes. If in a monorepo, do not invent repo-wide check/fmt commands.

## Commit the fixes

Default path (selection / `review-and-fix` / polish the tip): **new commit only**. Leave other agents’ staged/unstaged/untracked paths untouched. Do not `git add -A` / `git add .`. For new untracked paths this pass created, `git add -- <those-paths>` first (pathspec only; required before `--only` will accept them). Then commit so unrelated staged paths stay out (do not `git commit` the whole index). Put `-m` / HEREDOC / other commit options **before** `--`; after `--`, git treats words as pathspecs:

```
git commit --only -m "$(cat <<'EOF'
…message…
EOF
)" -- <paths-this-pass-changed>
```

- Message: pick gitmoji from the **primary** nature of the fixes (`:bug:` for real bugs, `:art:` for refactor/clarity, `:memo:` for docs, `:zzz:` for chore). Scope is optional; in a monorepo prefer the project directory. Subject should say it is review follow-up when that helps (e.g. `:art:foo: review follow-up: tighten error paths`).
- Body: what landed; optional one line that it follows review of `<short-sha>`.
- Trailers: `Assisted-by` for this session’s model (required when this session produced the fix diff). Do **not** copy review trailers onto the fix commit. Do **not** add agent `Co-authored-by` (see [git-commits](../git-commits/SKILL.md)).
- Report the new commit hash when done.

### Bare t

Bare `t` always targets `HEAD`. In the same turn: check amend guards; report (hygiene header per [Report, then fix](#report-then-fix)); if amend is allowed, fix **every** tree finding (upper and lower), **apply message hygiene**, then **amend** into `HEAD` when there is work (not a new follow-up commit). After a **tree** amend, [Ping-pong](#ping-pong). The design-choice pause in [Report, then fix](#report-then-fix) still applies (ask — do not guess; no amend and no handoff until the user replies). The phrase **polish the tip** does not use this path.

**Amend is allowed only if all of:**

- Reviewed commit **is** `HEAD`
- Tip is **not** on any remote-tracking ref (`git branch -r --contains HEAD` is empty). If it is, stop and say so — do not amend published history (never force-push, including to `master`)

If a guard fails, stop after the report, say why — do not edit the tree and do not amend. Tree fixes can still land via selection on that report (`all` / `y` / labels) or `review-and-fix` / polish the tip (new commit).

**Amend when any of:** tree fixes landed, and/or message hygiene needs a rewrite. If neither, stop (clean tip). Working tree changes from this pass must belong in that same commit story.

**Index (multi-agent):** Check `git status` before amend. Leave other agents’ staged/unstaged/untracked paths untouched. Do not `git add -A` / `git add .`. For new untracked paths this pass created, `git add -- <those-paths>` first (pathspec only). Fold this pass with the `--only` forms below — never a plain `git commit --amend` that commits the whole index (that would pick up unrelated staged paths).

**Message on amend** (read the Contributing section of `AGENTS.md` and [git-commits](../git-commits/SKILL.md)):

- Keep the tip’s **story** (same feature/fix subject intent) — do **not** retitle to “review follow-up”
- Apply every reported hygiene finding: wrong/missing gitmoji, subject/body shape, trailer order, strip agent `Co-authored-by`, fix `Reported-by` / `Suggested-by` per AGENTS.md Contributing and git-commits
- `Assisted-by` (do **not** copy a line from an unrelated commit in `git log`):
  - **Hygiene-only** (message rewrite, same tree): keep the tip’s existing `Assisted-by` line(s). Do **not** replace with this session’s model; do **not** add this session if absent (see [message-only rewrite](../git-commits/SKILL.md#message-only-rewrite)).
  - **This session landed tree fixes:** union this session’s `AGENT_NAME:MODEL_VERSION` with the tip’s existing `Assisted-by` lines (one line per pair; dedupe exact duplicates). Do **not** drop the original model.
- Hygiene-only (no pathspec so the index is ignored; do not use `--no-edit`):

```
git commit --amend --only -m "$(cat <<'EOF'
…message…
EOF
)"
```

- With tree fixes (working tree of those paths; unrelated staged paths stay out). Put `-m` / HEREDOC **before** `--`:

```
git commit --amend --only -m "$(cat <<'EOF'
…message…
EOF
)" -- <paths-this-pass-changed>
```

- Prefer `git commit --amend --only --no-edit -- <paths-this-pass-changed>` only when the existing message is already clean, `Assisted-by` already includes this session (no missing union), and you have tree-only changes with no hygiene work

Report the new `HEAD` hash when done (note it replaced the reviewed tip). Then, if this pass landed **tree** fixes, follow [Ping-pong](#ping-pong). Hygiene-only amend does **not** start or continue ping-pong.

### Ping-pong

Bare `t` only. Two agents take turns on the **same tip** until **either** side has **no tree findings**. Message hygiene does not keep the loop alive. After a tree amend, **handoff and end the turn** — do not wait for the other agent, poll `HEAD`, or poll their status.

If `REVIEW_T_HEADLESS=1` is set, skip the handoff steps below and end the turn after this pass — a headless driver launches the other agent (see [Headless ping-pong](#headless-ping-pong)).

**Handoff target (same Herdr tab, same cwd):** prefer an existing **other** pane that is already running an agent (any agent kind, any model). If there is no such pane, a new pane/agent may be created only when this pane is one of the default review pair kinds (`cursor` or `grok`) — then create the complementary default pair member. If this pane is **not** `cursor` or `grok` and no existing other agent pane is available, do **not** split a pane and do **not** start a new agent; stop after this pass and say handoff was skipped (no suitable other agent pane).

Default pair (used only when this pane is `cursor` or `grok` and no existing other agent pane is available):

| Side | Herdr `--kind` | Args after `--` on `agent start` |
|------|----------------|----------------------------------|
| Cursor CLI, Grok 4.6 Medium | `cursor` | `--model cursor-grok-4.6-medium --trust --yolo` |
| Grok Build, Grok 4.7 256K High | `grok` | `--model grok-4.7 --reasoning-effort high --yolo` |

`grok-4.7` already uses a 256K context window; do not add a separate window flag. Grok’s `--yolo` is an unlisted alias of `--always-approve`. Determine this pane’s kind from `herdr pane current --current` → `.result.pane.agent`.

After **this** agent’s tree amend:

1. Require `HERDR_ENV=1`. If unset or not `1`, stop after this pass and say you are not inside Herdr (do not spawn). Follow [herdr](../herdr/SKILL.md) for CLI, IDs, split geometry, `--cwd`, and `--no-focus`. If a Herdr command fails, stop and report the error (do not claim handoff).
2. Find an **other** agent pane in **this tab**, same cwd: `herdr agent list`, then keep entries whose `tab_id` is `$HERDR_TAB_ID`, whose `cwd` matches this pane’s `cwd`, and whose `pane_id` is not this pane’s `pane_id`. Ignore `agent_session.kind` (it is `id`, not the agent kind). If several remain, prefer an `idle` entry, then one whose `agent` differs from this pane’s `agent` (or any other pane when this pane has no agent), otherwise take the first. Reuse that entry’s pane (any agent kind, any model).
3. If none and this pane’s agent is `cursor` or `grok`: split a sibling pane with `herdr pane split --current --cwd "$PWD" --no-focus` and `--direction right` or `down` per the herdr layout rule (wide → right, tall → down). Then start the **complementary** default pair member with `herdr agent start <name> --kind <other-kind> --pane <new-pane-id> -- <start-args>` from the table above. Prefer names `review-cursor` / `review-grok` when free; otherwise a unique `[a-z][a-z0-9_-]{0,31}` name. Do not close panes you did not create.
4. If none and this pane’s agent is neither `cursor` nor `grok` (or unknown): do **not** split or start a new agent; stop after this pass and say handoff was skipped because no existing other agent pane was found.
5. If the chosen other agent is already `working`, do not double-prompt; **end the turn**.
6. If the chosen other agent is idle (or just started), `herdr agent prompt <pane_id> t` using the reused entry’s `pane_id` or, after a spawn, the new pane’s `pane_id` from `agent start` (`name` may be absent). Do **not** pass `--wait`. Then **end the turn**.

The next pass on this pane is a later `t` (from them after their tree amend, or from the user). If they have no tree findings, they stop in their pane and do not prompt you. Do not stay `working` to observe that.

Stop without handing off when **this** pass has **no tree findings** (clean, or hygiene-only amend only).

Re-check amend guards each pass. Design-choice pause still applies (ask — do not guess; no amend and no handoff until the user replies).

### Headless ping-pong

Use when there is no Herdr, or you prefer an unattended terminal run over panes. The Herdr handoff stays the default for interactive passes.

Setup: copy `pair.example.json` to `pair.json` next to this skill and edit it (the real `pair.json` is gitignored; a missing or invalid config is a hard error). Schema:

- `agents` — a list of exactly two argv lists. Each is the full non-interactive invocation, with the `t` prompt as the final argument, e.g. `["grok", "--model", "grok-4.7", "--reasoning-effort", "high", "--always-approve", "-p", "t"]`. Permission bypass is required (nobody is there to approve prompts).
- `max_passes` — cap on agent passes (default `6`). A pass is one agent run; passes alternate A then B, starting with A.
- `timeout_seconds` — per-pass timeout (default `3600`).

Run from the repo to review: `python3 <skill-dir>/pingpong.py` (e.g. `python3 ~/.agents/skills/review/pingpong.py`).

What the driver does: reads `pair.json`, then alternates the agents for up to `max_passes` passes. Each pass runs with `REVIEW_T_HEADLESS=1` (so the bare-`t` flow ends its turn instead of attempting a Herdr handoff) and inherits `HERDR_ENV` harmlessly, since the headless check runs before the Herdr steps. Each pass re-checks the amend guards and amends the evolving tip, exactly like the Herdr ping-pong. Output streams through; the driver stops early when a pass output reports `No tree findings`, and also stops (with exit code 2) when a pass prints `Need user decision.` — then the invoking agent relays the questions to the human, applies the answers out-of-band, and reruns the driver. It exits nonzero when an agent exits nonzero, times out, output cannot be drained after process-group cleanup, or the pass limit is reached without a clean report (the pass's output is already on screen when that happens). At the end it prints the hash chain from the reviewed tip to the final tip.

Stop detection keys off the literal `No tree findings` and `Need user decision.` lines from the bare-`t` report format — contracts defined in [Report, then fix](#report-then-fix); keep those exact strings. If your agents phrase them differently, adjust the driver or accept the `max_passes` cap.

### Amend (opt-in only)

For paths other than bare `t`, amend only if the user explicitly asks **and** all bare-`t` amend guards above hold. Fold **tree** fixes into the reviewed tip; apply message hygiene when the user asked for amend (same message and `--only` rules as [Bare t](#bare-t)).

Otherwise keep the new-commit path and say why amend was skipped.

## Done

- Summarize what changed (brief)
- Hashes:
  - New-commit path: reviewed commit → fix commit (or “clean, no fix commit”)
  - Bare `t` / amend: reviewed tip → new `HEAD` after each amend (or “clean, no amend”). Ping-pong: say whether this pass handed off `t` (reused existing agent pane / spawned default pair pane), skipped handoff (already busy / not in Herdr / no existing other agent pane and this pane is not `cursor` or `grok`), or stopped for no tree findings here. Do not claim the other side’s result unless they already reported it in this pane.
