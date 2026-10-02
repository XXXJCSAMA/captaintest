# spandrel-tools

> Framework plugin for Spandrel — graph-agnostic audit, health, traversal, and triage skills usable by any Spandrel knowledge graph.

## Status

**v0.0.1 — stub.** Plugin manifest scaffolded; no skills authored yet. Skills get authored once at least one content/client plugin has been in use long enough to surface concrete audit needs against a real graph. The first such instance is [`definite-os`](https://github.com/elegant-atomics/definite-os) (Trevor's Definite client engagement packaged as a Claude Code plugin).

## Why this exists

First, what this plugin is **not** for: the **deployment skills** (`using-knowledge`, `authoring`) ship *inside every Spandrel plugin*, scaffolded by `spandrel init`. A content plugin is operational on its own — it does not depend on `spandrel-tools` to orient an agent or handle authoring requests. This plugin is strictly for **power-user / maintenance** capabilities (audit, health, link integrity, staleness) that a graph maintainer opts into.

When a content plugin *does* want those capabilities, the packaging shape is **two-plugin**:

1. **Framework plugin** (this one — `spandrel-tools`) — ships graph-agnostic maintenance capabilities. Maintained alongside the Spandrel framework. Operates on any Spandrel graph via the CLI (`spandrel compile`, `spandrel audit`, `spandrel embed`) or the MCP server attached to whatever graph is loaded.

2. **Content/client plugin** (`definite-os`, future siblings) — ships graph content + client-specific skills (authoring workflows, content production). Declares `spandrel-tools` as a dependency:

   ```json
   {
     "name": "definite-os",
     "version": "0.1.0",
     "dependencies": ["spandrel-tools"]
   }
   ```

Installing the content plugin pulls in the framework plugin automatically. One install delivers framework toolkit + client content + client skills.

This separation matters because **generic and specific have different lifecycles**. Audit detector improvements ship once in this plugin; every Spandrel-based plugin inherits via dependency update. Content-production skills evolve per-engagement, in their own plugin. Skill-listing budget stays focused per plugin.

## Planned skill inventory

Initial scope when authoring begins:

| Skill | Backing CLI / MCP | What it does |
|---|---|---|
| `audit-health` | `spandrel compile` | Run compile, parse warnings by type, return structured health report (counts, severity, top findings). |
| `triage-warnings` | `spandrel audit` | Group findings by detector type, pick top-N for cleanup, suggest fixes per warning class. |
| `find-missing-links` | `spandrel embed` + `spandrel audit --semantic` | Present embedding-similar-but-graph-distant pairs with cosine scores; propose edges. |
| `check-link-integrity` | Compile + `get_node` | Surface broken links; fuzzy-match each broken path against existing nodes; propose fixes. |
| `detect-stale` | Audit + `get_references` | Identify stub_markers and high-fanin stale nodes (where staleness propagates). |
| `graph-stats` | Compile + analysis | Overall health snapshot — counts, warnings by category, leaf/composite ratio, top-fanin nodes. |
| `trace-references` | `get_references` + `get_node` | Given a path, dump all inbound + outbound edges with snippets — "what breaks if I rename." |
| `pre-commit-check` | Compile + audit | Run compile + audit before commit; block on hard errors. Pairs with the `Stop` lifecycle hook for write-time integration. |

Not all of these ship in v0.1.0. Start with `audit-health` + `triage-warnings` as the smallest useful set; add others as patterns emerge from real audit cycles against real graphs.

## Install (when v0.1.0 ships)

For local development against the stub:

```bash
git clone https://github.com/trevorfox/spandrel.git
claude --plugin-dir ./spandrel/spandrel-tools
```

Once published to a Claude Code marketplace, the standard `/plugin install` flow will work.

## Use (when skills ship)

Skills appear under the `spandrel-tools:` namespace and operate on whichever Spandrel graph is currently attached via MCP:

```
> /spandrel-tools:audit-health
# Runs `spandrel compile` against the attached graph, returns structured findings.

> /spandrel-tools:find-missing-links
# Requires embeddings to be populated first (npx spandrel embed <path>); presents candidate edges.
```

## Dependencies

This plugin doesn't depend on any other plugin. It's the framework root that content/client plugins depend on.

It does require:

- **Node.js** — for the bundled `npx -y spandrel` execution path.
- **A Spandrel graph** — either attached via MCP (from another plugin's `.mcp.json`) or pointed at via `--add-dir`.

## Why this lives in the Spandrel repo

The framework plugin's lifecycle is tied to the framework itself. Audit detectors, warning types, and CLI surface area all originate in Spandrel; co-locating the plugin in the same repo means framework changes and plugin updates ship together. Future split into a separate repo is possible once the plugin's release cadence diverges meaningfully from Spandrel's npm releases — defer until that divergence is real.

## Planning context

Architectural rationale lives in the planning graph (gitignored):

- `_planning/features/spandrel-tools-plugin.md` — this plugin's feature node
- `_planning/features/plugin-as-graph.md` — the architectural pattern this plugin completes
- `SPANDREL-FEEDBACK.md` § 15 — the two-plugin packaging direction
