---
name: git-commits
description: >-
  Agent commit extras on top of the vibe Contributing contract in
  AGENTS.md: Assisted-by format, amend and squash trailer union,
  message-only rewrite, optional review markers, no agent author.
  Use when committing or writing a commit message.
---

# Git commits and trailers

Message shape, trailer names/order, and no agent `Co-authored-by` follow the
current project's `AGENTS.md` / `CONTRIBUTING.md` when they specify them.
**Read that repo guidance and this skill before every commit.** Everyday agent
rules live in `AGENTS.md`.

## Subject format

- If `AGENTS.md` or `CONTRIBUTING.md` specifies a different subject format, follow that format.
- If they do not specify a format and recent existing git commits in the repo do not use gitmoji, do not use the 13 Short Gitmojis.
- Otherwise (including when recent commits already use gitmoji), use [13 Short Gitmojis](https://mmap.page/dive-into/gitmoji/). Prefer the emoji **code** (e.g. `:bug:`) over the glyph.

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
- `:fire:` is for removing a feature / API surface, not only deleting files
- `:poop:` marks dirty hacks or workarounds that may need cleanup later
- `:100:` is for test code and test suites — not lint, format, typecheck, or CI/check runner changes (`:zzz:`)
- Do not invent other gitmoji codes (including those from the full gitmoji.dev catalogue) when using this format

## Author

- Git `Author` is always the human. Never set the agent as author (breaks blame
  and ownership).
- The human owns what lands on `master`.

## Assisted-by

Required on every commit an AI agent materially helped produce. Follows the
[Linux kernel AI coding assistants guidance](https://docs.kernel.org/process/coding-assistants.html).
Message-only rewrites do not qualify — see [Message-only rewrite](#message-only-rewrite).

```
Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL1] [TOOL2]
```

- `AGENT_NAME` — the AI tool or framework (e.g. `Cursor`, `Claude Code`, `Copilot`)
- `MODEL_VERSION` — the model that helped **this** commit’s tree (e.g. `gpt-5.6`, `cursor-grok-4.5`). For a new commit, take it from the current session identity, not from a different commit. Message-only rewrite and amend union: see below.
- `[TOOL1] [TOOL2]` — optional specialized analysis tools only (e.g. `coccinelle`, `sparse`, `clang-tidy`)

Do not list basic development tools (git, compilers, make, editors).

```
:new:foo: scaffold Deno CLI

Assisted-by: Cursor:cursor-grok-4.5
```

- For a **new** commit this session produced: write `Assisted-by` from this session’s agent/model. Do **not** copy a line from `git log`, a different commit, or examples — those often name a different model.
- [Message-only rewrite](#message-only-rewrite) (same tree): keep the existing lines; do not add this session if absent.
- When **amending** a commit to add tree this session produced: union this session’s `AGENT_NAME:MODEL_VERSION` with that commit’s existing `Assisted-by` lines (one line per pair; dedupe exact duplicates). Do not drop the original model.

`Reported-by` and `Suggested-by` name **humans** only — never an agent. Agent
help (including when the user asks an agent to review code) belongs in
`Assisted-by`.

- `Reported-by`: on a `:bug:` fix for a bug the **user** reported and you confirmed valid. Use the reporter’s usual git identity. Do **not** add it when you found the bug without a user report, or when you disagreed and did not fix it.
- `Suggested-by`: when a **human** suggested the idea or approach. Use their usual git identity. Do **not** add it for generic “please fix / please implement” without a substantive suggestion, or when you invented the approach alone.

Never add `Co-authored-by` (or `Co-Authored-By`) naming an agent or bot, e.g.
`Cursor <cursoragent@cursor.com>`. Leave legitimate human `Co-authored-by`
untouched.

## Review markers (optional)

`Acked-by` (light review) and `Reviewed-by` (full review) record that a human
reviewed **that commit**. Both name **humans** only — never an agent. A marker
certifies that commit only; do not carry it into rewritten history without a
fresh review.

- Agents must not add them on their own judgment. Add one only when the user
  says a human reviewed (and names the reviewer) or asks for the trailer. An
  explicit “LGTM” alongside a commit request counts as that confirmation — add
  the marker naming the user and say you did; weaker signals (“sure, go
  ahead”) do not.
- Identity: the reviewer’s usual git identity; a self-review (reviewer =
  `Author`) is valid review-depth attribution.
- Do not invent other review-depth trailers.

## Squash (N commits → 1)

Only when the user explicitly asks.

- Group by **story**, not only by file. Keep breaking-change commits small —
  only the breaking change; fold in the cleanup the change made unnecessary.
- Order the result for the branch that merges, then for later work that
  rebases on top.
- **Message:** subject from the group’s **primary intent** (often the lead
  ingredient); merge bodies in [body order](#body) and re-pick the subject
  type when that intent is not what the lead subject said.
- **Trailers:**
  - `Suggested-by` / `Reported-by` — preserve from ingredients when still
    true of the result.
  - `Assisted-by` — union distinct `AGENT_NAME:MODEL_VERSION` lines from
    ingredients (dedupe exact duplicates, one line per pair). Do **not**
    substitute the squash session’s model, and do not add the squash session
    for message drafting or rebase mechanics alone.
  - `Acked-by` / `Reviewed-by` — **drop** from ingredients; re-add only after
    the human confirms review of the **whole** squashed commit (a later
    message-only rewrite to append them is fine).
  - Strip agent/bot `Co-authored-by`.
- After regroup, verify the branch tip **tree** matches the pre-rewrite tip
  (`git diff OLD_TIP HEAD` empty) when the goal was regroup-only.

## Message-only rewrite

Same tree, new commit object — polish message or strip bad trailers. The diff to
the parent must stay identical; do not fold staged or working-tree path changes
into the rewrite. No pathspec, so the index is ignored:

```
git commit --amend --only -m "$(cat <<'EOF'
…message…
EOF
)"
```

- Keep existing `Assisted-by` line(s). Do **not** replace with the rewriting session’s model.
- Do **not** add `Assisted-by` for the rewriter when absent — rewriting the message is not producing the diff.
- Strip agent/bot `Co-authored-by`; leave legitimate human `Co-authored-by` untouched.
- Do not drop `Reported-by` / `Suggested-by` when they still apply; correct them when hygiene requires it (see above).
