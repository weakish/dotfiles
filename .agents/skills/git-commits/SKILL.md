---
name: git-commits
description: >-
  Repo commit message and trailer contract: 13 Short Gitmojis subjects;
  Assisted-by; optional Acked-by / Reviewed-by to record human review;
  Reported-by for user-reported bugs; Suggested-by for human
  ideas and approach; squash and message-only rewrite rules.
  Use when committing, writing a commit message, or adding review trailers.
---

# Git commits and trailers

Everyday agent rules live in [AGENTS.md](../../../AGENTS.md). **Read this skill before every commit** (AGENTS.md requires it).

## Commit messages

Use [13 Short Gitmojis](https://mmap.page/dive-into/gitmoji/). Prefer the emoji **code** (e.g. `:bug:`) over the glyph.

### Format

```
:<type>:[scope:] <summary>
```

- `<type>` — one of the 13 codes below (required)
- `scope` — optional (e.g. `brew`, `port`, `paperwm`, `setup`); omit when it burns subject length without adding clarity
- `<summary>` — short description; imperative mood preferred
- Keep the first line under **50 characters** when practical

### Body

- After the subject, add a short body when motivation is not obvious from the diff.
- Order: **what landed** (change details, not a file list); then **problem or trigger** if the reader needs it; then **technical-decision rationale** (why this option, not that one) in its **own paragraph** — rationale is secondary.
- Do not frame a commit as introducing a mechanism that already existed; say refresh / bump / tighten when that is what happened.
- Put trailers after the body.

Examples:

```
:bug: brew trust tap
:new:paperwm: git pull if repo exists
:zzz: bump versions
```

### Types

| code | usage |
|-----------|------------------|
| `:bug:` | bug fix |
| `:new:` | new feature |
| `:fire:` | remove feature |
| `:boom:` | breaking changes |
| `:lock:` | security fix |
| `:art:` | refactor |
| `:zap:` | performance |
| `:100:` | test |
| `:memo:` | doc |
| `:zzz:` | chore |
| `:tada:` | release |
| `:poop:` | dirty |
| `:egg:` | Easter eggs |

### Notes

- `:lock:` is for security issues (a special kind of bug)
- `:fire:` is for removing a feature / API surface, not only deleting files (e.g. dropping a brew cask or tap)
- `:poop:` marks dirty hacks or workarounds that may need cleanup later
- Do not invent other gitmoji codes (including those from the full gitmoji.dev catalogue) for this repo

## Commit trailers

Trailers record agent help (`Assisted-by` per commit when an agent helped; squash before merge if you prefer). Git `Author` is always the human, for `git blame`. Review depth may be recorded with Linux-style trailers; meanings below are this repo’s contract, not a copy of every kernel trailer rule.

`Acked-by` / `Reviewed-by` are **optional** markers that record which commits a human reviewed.

Trailer order after the subject/body:

1. `Reported-by` (when the user reported a valid bug this commit fixes)
2. `Suggested-by` (when a human suggested the idea or approach this commit implements)
3. `Assisted-by` (when an agent helped)
4. `Acked-by` / `Reviewed-by` (optional human review markers)

`Reported-by`, `Suggested-by`, `Acked-by`, and `Reviewed-by` name **humans** only — never an agent. Agent help (including when the user asks an agent to review code) belongs in `Assisted-by`.

**Never** add `Co-authored-by` (or `Co-Authored-By`) naming an agent, bot, or Cursor (`cursoragent@cursor.com`, etc.). Do not pass `git commit --trailer "Co-authored-by:…"`. If tooling injects it, strip it before finishing (amend / rewrite) rather than leaving it on the branch.

### Author

- Git `Author` is always the human. Never set the agent as author (breaks blame and ownership).
- The human is responsible for what lands on `master`.

### Assisted-by

Required when an AI agent materially helped produce **this commit’s diff** (code, config, docs in the tree). Follows the [Linux kernel AI coding assistants guidance](https://docs.kernel.org/process/coding-assistants.html). Message-only rewrites do not qualify — see [Message-only rewrite](#message-only-rewrite).

```
Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL1] [TOOL2]
```

- `AGENT_NAME` — the AI tool or framework (e.g. `Cursor`, `Claude Code`, `Copilot`)
- `MODEL_VERSION` — the model for **this** commit (e.g. `gpt-5.6`, `cursor-grok-4.5`); take it from the current session identity when this session produced the diff; on squash, union from ingredients instead (see below)
- `[TOOL1] [TOOL2]` — optional specialized analysis tools only (e.g. `coccinelle`, `sparse`, `clang-tidy`)

Do not list basic development tools (git, compilers, make, editors).

```
:bug: brew trust tap

Recent versions of Homebrew require trusting third-party taps.

Assisted-by: Cursor:cursor-grok-4.5
```

- When **this session** produced the diff, write `Assisted-by` from the agent/model that helped. Do **not** copy a line from examples — those often name a different model.
- One `Assisted-by` line per `Agent:model` pair (same agent, different models → separate lines; dedupe exact duplicates). Do **not** comma-join models on one line (`Assisted-by: Cursor:a,b` is wrong — ambiguous and fights trailer tooling).

```
Assisted-by: Cursor:composer-2.5
Assisted-by: Cursor:cursor-grok-4.5
```

- Intermediate commits usually carry only `Assisted-by` (the user may not have bandwidth to review every step). When a human **has** reviewed a commit, it may also carry `Acked-by` or `Reviewed-by` for that commit.

### Reported-by

- On a `:bug:` (or `:lock:`) fix for a bug the **user** reported and you confirmed valid, add `Reported-by: Name <email>`.
- Use the reporter’s usual git identity as `Name <email>` (from `Author`, prior commits, or what they give you in session) — not a bare nickname.
- Do **not** add it when you found the bug without a user report, or when you disagreed and did not fix it.
- Do **not** add it when the commit **only** updates documentation (plans, README, comments, help text, man pages) — even when the user reported the inaccuracy. Put `Reported-by` on the commit that fixes **incorrect behavior**; if you split a code fix from a doc follow-up, only the fix commit gets the trailer.
- When the user reports plan-vs-implementation inconsistency, decide which side is wrong: fix code (`:bug:` + `Reported-by`) if behavior is broken; fix the plan (`:memo:`) if docs are stale — no `Reported-by` on the plan sync.
- Exception: user explicitly asks for `Reported-by` on a non-`:bug:` commit.

```
:bug: skip mas upgrade on Sonoma

Recent mas versions require macOS 15+.

Reported-by: weakish <weakish@gmail.com>
Assisted-by: Cursor:cursor-grok-4.5
```

### Suggested-by

- When a **human** suggested the idea or approach this commit implements, add `Suggested-by: Name <email>`.
- Use their usual git identity as `Name <email>` (from `Author`, prior commits, or what they give you in session) — not a bare nickname.
- Covers design direction, not only bug reports (e.g. “use `port -N`”, “list Setapp apps”). Use `Reported-by` for a confirmed bug report; both may appear when a report also drove the approach.
- Do **not** add it for generic “please fix / please implement” without a substantive suggestion, when you invented the approach alone, or when the human only accepted / asked you to implement a fix you already proposed (e.g. in a review).

```
:new: port upgrade use non-interactive mode

Use port -N so setup does not block on prompts.

Suggested-by: weakish <weakish@gmail.com>
Assisted-by: Cursor:cursor-grok-4.5
```

### Acked-by (light review)

- Means: a human lightly reviewed **that commit**.
- Optional — use when you want to record light review.
- Identity: any human who did the light review (`Acked-by: Name <email>`) — the commit author, the agent's user, or another developer. A self-ack (reviewer = `Author`) is this repo's intentional review-depth attribution, not invalid trailer usage; do not flag it when reviewing commits or polishing messages.
- Agents must not add `Acked-by` on their own judgment; add it only when the user confirms a human did that light check (and names the reviewer), or asks for the trailer.
- Exception: when the user says LGTM (or an equivalent explicit approval) while asking for a commit, treat it as light-review confirmation — add `Acked-by` naming the user without asking, then tell the user the trailer was added. Do not infer acks from weaker signals ("sure, go ahead").

### Reviewed-by (full review)

- Means: a human fully reviewed **that commit**; same *role* as Linux kernel `Reviewed-by`.
- Optional — use when you want to record full review.
- Identity: any human who did the full review; may be the commit author (see the `Acked-by` note on self-review).
- Agents must not add `Reviewed-by` on their own judgment; add it only when the user confirms a human fully reviewed (and names the reviewer), or asks for the trailer.

### Example (lightly reviewed commit)

```
:memo: note port -N may abort setup on prompts

Assisted-by: Cursor:cursor-grok-4.5
Acked-by: weakish <weakish@gmail.com>
```

### Notes

- Do not invent other review trailers for light-vs-full depth.
- A review trailer certifies **that commit only**.

## History rewrite

Only when the user explicitly asks.

- Do **not** delete `refs/original/` or run aggressive `git gc --prune=…` after `filter-branch` / similar rewrites unless the user explicitly asks — those backups are the easy undo path if the rewrite is wrong.

### Squash (N commits → 1)

- Group by **story**, not only by file. Keep `:boom:` commits small — only the breaking change. Forgotten cleanup that belongs to that boom (e.g. drop an obsolete install the boom made unnecessary) folds into the boom; do not invent a separate chore commit for the agent’s omission.
- Order for the branch that will merge to `master`, then for later work that rebases on top: prefer a continuous handoff (e.g. modernize Python floor, then lint tooling that assumes that floor). Setup follow-ups to an existing `master` topic can sit first; docs that a later boom edits must land before that boom.
- **Message:** subject from the group’s **primary intent** (often the lead ingredient); merge bodies in [body order](#body) (what landed, then trigger, then rationale); re-pick gitmoji when that intent is not what the lead subject said.
- **Trailers on the squashed commit:**
  - `Suggested-by` / `Reported-by` — preserve from ingredients when still true of the result.
  - `Assisted-by` — union distinct `Agent:model` lines from ingredients (dedupe exact duplicates; one line per `Agent:model` pair — see [Assisted-by](#assisted-by)). Do **not** substitute the squash-session model. Do **not** add the squash-session agent for message drafting or rebase mechanics alone.
  - `Acked-by` / `Reviewed-by` — **drop** from ingredients. Re-add only after the human confirms review of the **whole** squashed commit (a later message-only rewrite to append `Reviewed-by` is fine when they ask).
  - Strip agent/bot `Co-authored-by` (see the **Never** add `Co-authored-by` rule above).
- After regroup, verify the branch tip **tree** matches the pre-rewrite tip (`git diff OLD_TIP HEAD` empty) when the goal was regroup-only.

### Message-only rewrite

Same tree, new commit object — polish message, strip bad trailers, or append review markers the user requested.

- Keep existing `Assisted-by` line(s). Do **not** replace with the rewriting session’s model.
- Do **not** add `Assisted-by` for the rewriter when absent — rewriting the message is not producing the diff.
- Strip agent/bot `Co-authored-by`; leave legitimate human `Co-authored-by` untouched.
