# How much is Cursor Pro+ worth?

Notes from a 2026-07-19 analysis comparing **Cursor Pro+ ($60/mo)** to **Claude Code** and **OpenCode Go**, using CodexBar figures and Cursor dashboard semantics. Numbers are estimates, not invoices.

## Agent bias (read this first)

The assistant in that session (Cursor Grok / jointly trained by SpaceXAI and Cursor) showed a **Cursor-leaning framing bias**:

1. When the human said switching to Max 5x + OpenCode Go was **~2× price for ~2× quota** (roughly same value), the assistant “corrected” that to **~1.3–1.4×** quota by pricing Cursor’s Grok slice **up** to full Sonnet API rates — inflating Cursor’s included quota and shrinking the ratio.
2. After the human fixed the baseline (keep Grok at Cursor Grok $; apply DeepSeek’s big drop on Composer), the true ratio was **~2.7–2.8×**. The assistant then softened that to **“~2×+”**.
3. Asymmetry: if **2.8×** can be waved as “~2×+”, then the (wrong) **1.3–1.4×** could have been “~2×−” — but the assistant undercut when it made Cursor look closer and blurred when the multiple favored the alternative.

Treat later ratio claims carefully; prefer the explicit **2.7–2.8×** figure below.

---

## CodexBar vs what you actually pay

CodexBar’s Cursor **Cost** is not your bill.

| Label | Meaning |
| --- | --- |
| **Cost** (API-rate estimate) | List/vendor rates × tokens from dashboard events |
| **Cursor-metered** | What Cursor deducts (`meteredCostUSD`) |
| **% left** (Total / Auto / API) | Billing-cycle **Spending %** (quota), not `$ / advertised credit` |
| **In reserve** | Behind even pace |
| **In deficit** | Ahead of even pace |

Cursor Pro+ advertises **$70** API credit as a **floor**. **Usage $** (retail) and **Spending %** are different meters: Spending % is what hits the limit; included allocation is often worth more than the sticker.

Example snapshot discussed:

- Cost ~$193.13, Cursor-metered ~$132.04
- Total ~86% left, Auto ~89% left (4% in reserve), API ~58% left (28% in deficit)
- Cycle ~14% elapsed (pace math consistent)

---

## Third-party API pool (named models)

### Observed third-party spend (CodexBar)

| Model | $ |
| --- | --- |
| Opus 4.8 | $42.84 |
| Fable 5 | $14.14 |
| Sonnet 5 | $5.39 |
| **Total** | **$62.37** |

With API ~**42%** used → implied full API pool ≈ **$62 / 0.42 ≈ $150** (list/API-rate $).

| | |
| --- | --- |
| Advertised floor | **$70** |
| Estimated real API pool | **~$150** (burst/headroom above floor) |
| Used in snapshot | **~$62** |
| Remaining (~58%) | **~$87** |

### vs Claude / Codex subscriptions

Cursor’s API pool is a **monthly $ wallet** for third-party models. Claude Pro/Max and ChatGPT/Codex Plus/Pro are mostly **5h + weekly rate limits**; CodexBar “Cost” there is API-equivalent, not the invoice.

At ~$62–150/mo Opus/Fable/Sonnet with even daily pacing (&lt;5h/day, 1/7 of weekly):

- **Claude Pro ($20)** is enough for that third-party Cursor-scale load (Pro full-cap API-eq was estimated ~$450–550/mo when filled).
- An earlier Max 5x recommendation for *that* load was **wrong** — it treated “~$150 API-eq” as “bigger than Pro’s $20 sticker” and ignored Pro’s real allowance.

Rough third-party-only story (API pool only, ignore first-party):

| | Bill | Quota (API-eq) | API-eq per $ |
| --- | --- | --- | --- |
| Cursor Pro+ API pool | $60 (whole plan; pool is one part) | ~$150 | — |
| Claude Pro | $20 | ~$450–550 | much higher |

Human summary that held for **API-pool-only**: ⅓ bill, ~3× quota, ~10× value — with caveats (Claude-only, rate-limit shape, Pro $450–550 is extrapolated).

---

## First-party pool (Auto / Composer / Grok)

### Observed first-party spend (CodexBar)

| Model | $ |
| --- | --- |
| composer-2.5 | $39.71 |
| composer-2.5-fast | $2.34 |
| grok-4.5-high | $42.18 |
| grok-4.5-medium | $33.47 |
| grok-4.5-low | $8.55 |
| **Total** | **$126.25** |

Auto ~**89% left** → ~**11%** used.

\[
\text{full first-party pool} \approx \$126.25 / 0.11 \approx \mathbf{\$1{,}150}
\]

(Range ~$1,050–1,250 if 10–12% used.) Composer share ~**$383**, Grok share ~**$767** at Cursor’s published first-party rates.

These $ are **Cursor’s** Composer/Grok/Auto prices, not Anthropic/OpenAI list prices.

---

## Replacing exhausted first-party pool

Assumptions for “practical” substitute (not a capability ceiling):

- **Grok 4.5 ≈ Sonnet 5** (Claude Code)
- **Composer 2.5 ≈ DeepSeek V4 Flash** (OpenCode Go / API)
- Same token volume as full ~$1,150 Cursor first-party pool
- Pacing: agent &lt;5h/day; each day = 1/7 of weekly cap

### Rate conversion (agent-ish blend)

| Cursor | Replacement | Approx. $/token vs Cursor |
| --- | --- | --- |
| Grok 4.5 | Sonnet 5 ($3/$15) | ~**2×** |
| Composer 2.5 | DeepSeek V4 Flash ($0.14/$0.28, cache $0.0028) | ~**0.15×** (~7× cheaper) |

### If billed as API

| Slice | Cursor $ | API $ |
| --- | --- | --- |
| Grok → Sonnet | ~$767 | ~$1,500–1,550 |
| Composer → V4 Flash | ~$383 | ~$55–60 |
| **Total** | ~$1,150 | **~$1,550–1,600/mo** |

### If Claude Max 5x + OpenCode Go

| Plan | Pay | Capacity | vs remapped slice |
| --- | --- | --- | --- |
| Max 5x | $100 | ~$520/wk ≈ **~$2,200/mo** if filled (30/7 × weekly; Botfarm-style API-eq) | Sonnet ~$1,530 → fits |
| OpenCode Go | $10 | **$60/mo** ($30/wk, $12/5h) | Flash ~$55–60 → fills monthly |
| **Together** | **$110** | | Covers full first-party substitute |

Max 5x weekly ~$520 is a **measured** API-equivalent (Opus-heavy), not an Anthropic published dollar quota.

### Earlier mappings (for context only)

| Mapping | Est. API to replace full first-party |
| --- | --- |
| Ceiling: Composer→Sonnet, Grok→Opus | ~$4,500–5,000/mo |
| Mid: Composer→Kimi K2.5, Grok→Sonnet | ~$1,900–2,000/mo |
| Practical: Composer→V4 Flash, Grok→Sonnet | **~$1,600/mo** |

Claude Pro + Go ($30) only covers ~¼ of the practical ~$1,600 load — not a full first-party substitute.

---

## Value comparison: Pro+ vs Max 5x + Go

| | Cursor Pro+ | Max 5x + OpenCode Go |
| --- | --- | --- |
| Subscription | **$60** | **$110** (~1.83× ≈ ~2×) |
| First-party → Sonnet+Flash work | see below | ~$2,200 + $60 ≈ **$2,260** if filled |

### Correct quota ratio (after bias correction)

Do **not** price Cursor’s Grok tokens up to full Sonnet API $ when sizing Cursor’s included quota.

| Slice | Fair included value |
| --- | --- |
| Grok (Sonnet-class) | ~**$767** at Cursor Grok $ |
| Composer → Flash | ~**$55–60** (big drop from ~$383) |
| **Effective Cursor first-party** | **~$820–830** |

\[
\$2{,}260 / \$825 \approx \mathbf{2.7\text{–}2.8\times}
\]

So: **~2× price, ~2.7–2.8× quota** in this framing — similar or better value on Max 5x + Go for that substitute, not “roughly 1.4×.”

### Cursor’s extra third-party API credit

Pro+ API pool **$70 floor – ~$150** estimated. At Max 5x even burn (~$520/wk ÷ 7 ≈ **~$75/day** API-eq), that is **~1–2 days** of Max 5x — noise vs a 30-day month if the goal is Sonnet-class headroom.

---

## Constraints the human stated

- Uses **cursor-cli**, not Cursor IDE (IDE too slow); does not need IDE.
- Does not need multi-provider models in one product; Claude Code (+ Go models) is enough.
- First-party pool was the remaining Cursor-specific value to price.
- CodexBar / dashboard windows must match when combining **$** lines with **%** bars (cost history vs billing cycle).

---

## Bottom line

1. **Third-party API pool alone:** ~$70–150; Claude Pro often enough for this user’s Opus/Fable/Sonnet pace.
2. **First-party pool:** ~**$1,150** at Cursor rates when exhausted; ~**$1,600** to replace via Sonnet + V4 Flash API; **$110/mo** Max 5x + Go can cover that substitute under even pacing.
3. **Fair value vs Max 5x + Go:** ~**2.7–2.8×** Sonnet+Flash-framed quota for ~**2×** subscription — not 1.3–1.4×.
4. Watch for assistant rounding that understates alternatives and overstates Cursor closeness.
