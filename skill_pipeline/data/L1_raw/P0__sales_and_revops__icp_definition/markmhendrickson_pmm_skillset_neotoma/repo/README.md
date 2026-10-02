# pmm-skillset-neotoma

A reference bridge that gives [Gab Bujold's pmm-skillset](https://github.com/Fearofsnakes/pmm-skillset) a persistent memory by wiring it to [Neotoma](https://github.com/markmhendrickson/neotoma).

The skills are excellent facilitators. They refuse vague inputs, force traceability, and produce stakeholder-ready artifacts. But they start cold every run: each skill re-interviews from zero, and its output lives in the chat session and then evaporates. This repo closes that loop. It does not modify the skills. It wraps `icp-definition` so that:

1. **Before the run** it reads any prior ICP, positioning, and evaluator language for the client out of Neotoma and hands them to the skill as context (the skill's own "Re-entry" mode is built for exactly this).
2. **After the run** it writes the finished ICP back to Neotoma as structured entities, so the next skill in the chain (`positioning-audit`) reads it instead of asking you to paste it, and re-running next quarter is a "what changed?" diff rather than a cold start.

This is a standalone, neutral bridge. The skills stay provider-agnostic in their own repo; Neotoma stays a clean memory engine in its own repo; this is the third thing that connects them — owned by neither, pointed at by both.

## Why this matters (the two-run proof)

We ran `icp-definition` against the Neotoma README twice: once cold, once grounded in stored evaluator data. Same skill, different context in, materially different (and more accurate) output. The full run, captured turn by turn, lives here:

→ [The before/after run](docs/before-after.md)

The short version: when Layer 4 ("real customer language") was answered from a README, the skill correctly refused to fabricate quotes and flagged a gap. When the same layer was answered from Neotoma's stored evaluator corpus, the skill got a real, sorted quote bank (problem / objection / win / product-feedback) pulled live from the store. The skills are only as good as the context fed in. Neotoma is that context.

## What's here

| Path | What it is |
| --- | --- |
| [`skills/icp-definition-neotoma/SKILL.md`](skills/icp-definition-neotoma/SKILL.md) | A thin wrapper skill that calls the adapter before and after the original `icp-definition` skill. Drop-in for Claude Code / Cursor / Codex. |
| [`adapter/`](adapter) | A small TypeScript adapter using the published `@neotoma/client`. `read-context` pulls prior state for a client; `write-artifact` persists the ICP back as entities. |
| [`docs/pattern.md`](docs/pattern.md) | The generic read-before / write-after pattern, so any skill in the suite can be wired the same way. |
| [`docs/before-after.md`](docs/before-after.md) | The captured two-run demonstration. |
| [`docs/entities.md`](docs/entities.md) | The Neotoma entity shapes the adapter reads and writes (`icp_profile`, and how it links to `positioning`, `messaging_hierarchy`, and the client). |

## How it works

```
                    ┌─────────────────────────┐
   read-context ───▶│  Neotoma (your store)   │◀─── write-artifact
        │           │  icp_profile, evaluator │          ▲
        │           │  quotes, prior runs     │          │
        ▼           └─────────────────────────┘          │
  ┌───────────────────────────────────────────────────────────┐
  │  icp-definition  (Gab's skill, unmodified)                 │
  │  Mode D "Re-entry" accepts the prior layers as input.      │
  │  Produces the ICP artifact.                                │
  └───────────────────────────────────────────────────────────┘
```

The skill is never edited. The wrapper runs the adapter's `read-context` for a named client, passes the result into the skill as Re-entry input, then runs `write-artifact` on the result. If there is no prior state, the skill runs as a normal full build and the artifact is written fresh.

## Quick start

```bash
# 1. Install Gab's skills and this bridge as Claude Code / Cursor skills
npx skills add Fearofsnakes/pmm-skillset
npx skills add markmhendrickson/pmm-skillset-neotoma

# 2. Provide the Neotoma client. It is not on npm yet, so link it from a
#    local Neotoma checkout (https://github.com/markmhendrickson/neotoma):
#      cd /path/to/neotoma/packages/client && npm install && npm run build && npm link
#    then from this repo:
cd adapter
npm link @neotoma/client
npm install
npm run build

# 3. Point the adapter at your Neotoma instance
export NEOTOMA_BASE_URL=http://localhost:9180   # your instance
# export NEOTOMA_TOKEN=...                       # only for a remote instance

# 4. Read prior context for a client (feeds the skill's Re-entry mode)
node dist/cli.js read-context --client "acme"

# 5. ...run icp-definition as usual...

# 6. Write the finished ICP back as entities
node dist/cli.js write-artifact --client "acme" --file ./icp-acme.md
```

> **Note on the client:** the adapter depends on `@neotoma/client`, which currently
> ships inside the [Neotoma monorepo](https://github.com/markmhendrickson/neotoma/tree/main/packages/client)
> rather than on npm. `npm link` (above) or a local `npm pack` tarball both work
> until it is published. This is the one rough edge of the prototype.

## Tests

```bash
cd adapter
npm run test:unit     # pure-logic tests, no Neotoma needed (runs in CI)
npm test              # also runs the live round-trip test IF NEOTOMA_BASE_URL
                      # + NEOTOMA_TOKEN are set; otherwise it skips
```

The unit tests cover the parts that are easy to get subtly wrong: `parseIcp`
(the four layers split cleanly and anti-ICP never bleeds into Layer 4), the
quote `bucketFor` classifier (win / objection / product-feedback / problem), and
the Re-entry rendering (prior ICP shown, `raw`/`name`/`client` never leaked into
the prompt, empty quote bank flagged honestly). The opt-in integration test does
a real `write-artifact` then `read-context` against a live instance and asserts
the ICP round-trips back. CI runs the unit tests on every push.

## Status

Reference prototype. Built by Mark Hendrickson (Neotoma) as the concrete proof of the pmm-skillset × Neotoma co-integration. Gab Bujold (pmm-skillset author) is invited to collaborate here; the intent is that the pattern proven on `icp-definition` then graduates into the wider skillset on his terms.

## License

MIT. The wrapped skills are MIT (© Gab Bujold); Neotoma is MIT (© Mark Hendrickson); this bridge is MIT.
