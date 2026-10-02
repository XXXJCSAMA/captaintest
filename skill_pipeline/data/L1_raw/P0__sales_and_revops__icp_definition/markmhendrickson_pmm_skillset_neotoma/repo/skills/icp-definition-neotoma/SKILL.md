---
name: icp-definition-neotoma
description: "Run icp-definition with persistent memory. Reads any prior ICP, positioning, and evaluator language for the client out of Neotoma before the run, then writes the finished ICP back as structured entities. Trigger on: 'define our ICP with memory', 'icp-definition with neotoma', 'resume our ICP', 'what changed in our ICP', 'icp-definition grounded in our data', or whenever you would run icp-definition for a client already in Neotoma."
metadata:
  version: 0.1.0
  author: Mark Hendrickson
  category: product-marketing
  wraps: Fearofsnakes/pmm-skillset · skills/tier-1/icp-definition
---

# ICP Definition (Neotoma-backed)

You orchestrate Gab Bujold's `icp-definition` skill with a persistent memory layer. You do NOT replace or rewrite that skill — you run it, with two adapter calls bracketing it, so the run starts from stored context and ends by persisting its result.

**Key idea:** the original skill already has a "Re-entry" mode (Mode D) that "accepts the previous ICP layers as inputs." That is the seam. This wrapper fills that input from Neotoma instead of from the user's memory, and saves the output back so the next run (and the next skill) inherits it.

## Prerequisites

- Gab's skills installed: `npx skills add Fearofsnakes/pmm-skillset`.
- This bridge's adapter built: `npm --prefix adapter install` then `npm --prefix adapter run build`.
- `NEOTOMA_BASE_URL` pointing at the user's Neotoma instance.
- A `--client` handle (a name or slug) that identifies whose ICP this is.

## Act 1 — Read context from Neotoma (before the skill)

Run the adapter to pull prior state for this client:

```bash
node adapter/dist/cli.js read-context --client "<client>"
```

It returns, if present:
- the latest `icp_profile` for the client (all four layers + anti-ICP),
- any linked `positioning` entity (so the audience layer is consistent),
- a sorted bank of real evaluator quotes (`problem` / `objection` / `win` / `product_feedback`) drawn from the store's feedback-type entities for Layer 4.

**Branch on the result:**
- **Prior ICP found →** invoke `icp-definition` in **Mode D (Re-entry)**. Paste the prior layers as the established input, and ask only "what changed?" — new customers, win/loss, fresh evaluator data. Do not re-interview layers that are unchanged.
- **No prior ICP, but evaluator quotes found →** invoke `icp-definition` in **Mode A (Full build)**, but when the skill reaches **Layer 4 (Language)**, supply the real quote bank from the adapter instead of telling the skill you have none. Never fabricate quotes; only use what the adapter returned.
- **Nothing found →** run `icp-definition` Mode A normally. The artifact still gets written back in Act 3, so the next run is warm.

## Act 2 — Run icp-definition (unmodified)

Hand control to the original skill with the context from Act 1 as its input. Follow its three acts exactly as written. Your only addition is that its inputs are pre-filled from Neotoma where available, and that you must keep the Layer 4 quotes verbatim and attributed.

## Act 3 — Write the artifact back to Neotoma (after the skill)

When the skill produces the final ICP profile, persist it:

```bash
node adapter/dist/cli.js write-artifact --client "<client>" --file <icp-output.md>
```

This stores an `icp_profile` entity (the four layers + anti-ICP as fields), links it to the client entity and to any prior `icp_profile` it supersedes, and links the evaluator quotes it used. Confirm to the user: "Stored as icp_profile <id>; positioning-audit will read this directly."

## Anti-patterns

1. **Don't edit Gab's skill.** This wrapper only brackets it. If the skill's behavior needs to change, that's an issue on his repo, not a fork here.
2. **Don't fabricate Layer 4.** If the adapter returns no quotes, the skill flags the gap, exactly as it does today. The point of the bridge is to feed it real quotes when they exist, not to invent them.
3. **Don't write a second `icp_profile` when re-entering.** Supersede the prior one (the adapter links `SUPERSEDES`) so the history is a clean diff, not a pile of duplicates.
4. **Don't run the adapter against a Neotoma instance the user didn't point you at.** `NEOTOMA_BASE_URL` is the user's call; never guess a remote.
