# Spandrel

Spandrel ships your team's internal knowledge as a Claude Code plugin — a shared brain all your agents can use.

How? It compiles your markdown knowledge repo into a knowledge graph, served over MCP. Your agents compose from it, so the artifacts and actions they produce stay faithful to what your team actually knows.

Plug it in and your team's brain becomes part of the agent's working environment. Everyone composes from the same canonical source, updates compound across every artifact and action, and new hires inherit your institutional knowledge on install. The agent orients to what you actually know, produces work that reflects your decisions and conventions, and writes back when asked. No per-user configuration.

## Built for knowledge

Coding agents are great for authoring knowledge repos, but they are weak at retrieving knowledge. Grep, glob, and file reads suit code well, but they fare worse on institutional knowledge—rules, decisions, runbooks—where the useful answer rarely matches one obvious search string.

Three problems compound:
- **Brittle retrieval.** Grep finds strings; agents need to navigate concepts.
- **Silent staleness.** Without metadata, no one knows what's load-bearing or out of date.
- **Conflated concerns.** Instructions, knowledge, and skills crammed into the same files reduce reuse and feed hallucination.

## A framework for high-fidelity agent context

A framework for compiling markdown into a navigable, queryable, governable knowledge graph:

- **Compiler** — markdown tree → typed graph. Every node has a name, description, and links; every link has a type and per-edge description.
- **MCP + REST server** — exposes the graph through `context`, `get_node`, `navigate`, `get_references`, `get_graph`. Same data, two surfaces, one access contract.
- **Access policy** — `_access/config.yaml` defines roles and per-path read/write/admin; enforced at the wire.
- **Audit** — `spandrel audit` flags low-signal content (weak descriptions, stub markers, thin bodies); `--semantic` surfaces missing links between concepts that read like neighbors but aren't connected.
- **Task-fidelity harness** — measures whether structural changes to your graph actually make agents better at real tasks.

Plus a browser viewer at `localhost:4000` and a static-publish bundle for read-only production hosting.

Common atoms — the canonical, reused units agents compose from: user personas, product features, client and account briefs, decision logs, runbooks, playbooks, ICP definitions, team rosters.

![Spandrel viewer rendering the content-model collection at spandrel.org/content-model/](assets/spandrel-content-model.png)

*The browser viewer at `localhost:4000` — and at [spandrel.org/content-model/](https://spandrel.org/content-model/) — renders any node as readable markdown plus its typed edges, with a clickable d3-force graph alongside.*

**See it running.** [spandrel.org](https://spandrel.org) is itself a Spandrel graph — point your agent at it before installing anything locally:

```bash
claude mcp add spandrel https://mcp.spandrel.org/mcp --transport http --scope user
```

Then ask Claude: *"Use the spandrel MCP to orient me — start at `/` and walk me through the philosophy and content model."* You'll see progressive disclosure in action: the agent navigates by following edges, reading descriptions to decide where to go next, loading content only when needed.

## Architecture

![Spandrel architecture — markdown tree compiles into a graph governed by a single AccessPolicy, served over MCP and REST to Claude Code, the browser viewer, and HTTP/SDK clients](assets/architecture.png)

Markdown is the source of truth. The compiler builds a graph in memory; the same `AccessPolicy` instance gates every wire surface; MCP and REST are siblings, not a stack.

## A toolchain, not a service

A three-layer toolchain produces the artifact above:

- **Compile** — `spandrel compile` or `spandrel dev` turns a markdown tree into a graph. Deterministic, fast, watches for changes.
- **Serve** — REST + MCP through one `AccessPolicy`. Same data, two surfaces, one access contract.
- **Govern** — `_links/config.yaml` (link vocabulary), `_access/config.yaml` (per-path roles), `DESIGN.md` (collection schemas).

## Measure the graph

Spandrel ships with tools to evaluate graph quality, so you can answer *"is this graph good?"* rather than guess.

- **`spandrel audit`** — cheap heuristics flag low-signal descriptions, stub markers, thin bodies, weak edges.
- **`spandrel audit --semantic`** — embeddings surface missing links between concepts that read like neighbors but aren't connected.
- **Task-fidelity harness** (`test/fidelity/`) — runs curated questions through a Claude Code subprocess against your graph's MCP and scores answers with an LLM judge. Measures whether a structural change improved or degraded agent performance on real tasks.

Calibration on our own graphs: a mature graph scored **0.91** baseline on a 10-task set; structural cleanup (filling load-bearing descriptions, restructuring node bodies) moved it to **0.96**. The sample is small and local to that graph — the point is you can run the same harness against yours.

## Get started

Zero to a local MCP endpoint in five steps. For a guided walkthrough of designing a real graph, see [ONBOARDING.md](ONBOARDING.md).

**1. Install.**

```bash
npm install -g spandrel
```

**2. Create a graph.** Scaffolds the root node plus a `_links/config.yaml` seeded with the baseline vocabulary (`owns`, `depends-on`, `relates-to`, …).

```bash
spandrel init my-graph --name "My Graph" --description "Trying Spandrel out."
cd my-graph
```

**3. Add a node.** Create `clients/acme.md`:

```markdown
---
name: Acme Corp
description: Enterprise SaaS client, onboarded Q2 2025.
links:
  - to: /
    type: relates-to
---
Main engagement this quarter.
```

See [docs/patterns/linking.md](docs/patterns/linking.md) for frontmatter vs. inline links.

**4. Compile and serve.** Starts REST + MCP and a visual viewer at `localhost:4000`, plus a file watcher that reloads both on save.

```bash
spandrel dev .
```

Open `localhost:4000` to navigate the graph visually — rendered markdown, clickable d3-force graph, typed relationships, authoring warnings.

**5. Connect your agent.** Get the MCP snippet:

```bash
spandrel init-mcp .
```

The primary deployment path is a **Claude Code plugin** — `spandrel init` scaffolds the graph, MCP wiring, and skills as one installable unit (see [docs/deployment/claude-plugin.md](docs/deployment/claude-plugin.md)). To wire this snippet into Claude Code directly, drop it into `.mcp.json`; for Claude Desktop, paste it into `~/Library/Application Support/Claude/claude_desktop_config.json` and restart. Then ask the agent to start at `/` and navigate.

## Repo structure

A knowledge repo is pure content — no framework code, no system files:

```
my-knowledge/
├── index.md                  Root — what this graph is about
├── _access/config.yaml       Access control (optional)
├── _links/config.yaml        Link-type vocabulary
├── personas/                 A collection — canonical Things agents compose from
│   ├── index.md              Collection description
│   └── enterprise-buyer.md   Leaf node — an atom other Things reference
├── clients/                  A collection...
│   ├── index.md              Collection description
│   ├── DESIGN.md             What a well-formed member looks like
│   ├── acme-corp.md          Leaf node — a simple Thing
│   └── globex/               Directory node — a Thing with children
│       └── index.md
└── people/
    └── jane.md               Leaf node
```

Two ways to create a Thing: **`foo.md`** (leaf at `/parent/foo`) or **`foo/index.md`** (composite at `/parent/foo`, can have children). If both exist, the directory wins. `DESIGN.md`, `SKILL.md`, `AGENT.md`, and `README.md` are companion files — never compiled as nodes.

When you package that graph as a Claude Code plugin, the knowledge moves under `knowledge/` and a thin procedural shell wraps it — manifests, MCP wiring, and the deployment skills. `spandrel init` (plugin mode is the default) scaffolds exactly this:

```
my-plugin/
├── .claude-plugin/
│   ├── plugin.json                  Plugin manifest (name, version, description)
│   └── marketplace.json             One-plugin marketplace, so `/plugin install` works
├── .mcp.json                        Wires `spandrel mcp` at ${CLAUDE_PLUGIN_ROOT}/knowledge
├── skills/                          Claude Code skills — procedural, outside the graph
│   ├── using-knowledge/SKILL.md     Orient to the attached graph on session start
│   └── authoring/SKILL.md           Handle explicit "add/edit a node" requests
├── README.md                        Install + usage
├── AGENTS.md                        Operational guide for agents in this repo
└── knowledge/                       ← the Spandrel graph (the pure-content tree above)
    ├── index.md
    ├── _links/config.yaml
    └── ...
```

The split is physical and load-bearing: Spandrel only crawls `knowledge/`, while Claude Code's plugin loader reads everything else. Knowledge and procedure stay legible separately. Full walkthrough: [docs/deployment/claude-plugin.md](docs/deployment/claude-plugin.md).

## Deployment modes

Four modes, one compiled graph:

- **Local dev** — `spandrel dev` runs REST + MCP + a visual viewer on localhost. The authoring loop.
- **Static + MCP adapter** — `spandrel publish --static` emits a self-contained bundle; a thin serverless function adapts MCP over it. Read-only, hostable anywhere. The recommended production pattern. [mcp.spandrel.org](https://mcp.spandrel.org) is a running example; source at [trevorfox/spandrel-mcp](https://github.com/trevorfox/spandrel-mcp).
- **Claude Code plugin** — `spandrel init` scaffolds the graph + MCP server + skills as an installable Claude Code plugin; `/plugin install` delivers all three wired together. Best for handing a specific graph to agents inside Claude Code as a sealed, versioned unit.
- **Live backend** — a Postgres-backed `GraphStore` for graphs that need writes, identity-aware reads, or federation.

Full walkthrough: [docs/deployment/](docs/deployment/).

## Learn more

- [**ONBOARDING.md**](ONBOARDING.md) — agent-guided setup for a new graph
- [**docs/architecture/**](docs/architecture/index.md) — compiler, storage, access policy, REST, MCP
- [**docs/content-model/**](docs/content-model/index.md) — Things, Collections, link types, progressive disclosure
- [**docs/patterns/**](docs/patterns/index.md) — linking conventions, governance, progressive disclosure as a craft
- [**docs/philosophy.md**](docs/philosophy.md) — why a knowledge graph, not a vector store
- [**MCP tool reference**](docs/architecture/mcp.md) — read and write surface
- [**PUBLIC-API.md**](PUBLIC-API.md) — stable npm imports for embedding Spandrel in another TS/JS project

## License

MIT
