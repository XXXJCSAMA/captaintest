# PMM Stack — Project CLAUDE.md

## What This Is

PMM Stack is a **distributable skill pack for product marketers** — a set of structured Claude skills for JTBD validation, ICP definition, and positioning work. Designed to be installed standalone by other PMMs, not just used by Paul.

Shipped publicly under The Battlecard brand but lives as its own repo so users can clone just this without the newsletter infrastructure.

## Skills Included

| Skill | What it does |
|-------|-------------|
| `jtbd-miner` | Extracts Jobs-to-be-Done from customer interview transcripts and research notes |
| `jtbd-validator` | Validates whether a claimed job meets the JTBD quality bar (demand, strugglingness, progress clarity) |
| `icp-definer` | Builds a scored ICP from your existing customer base + market signals |
| `positioning-workshop` | Runs a structured positioning exercise using April Dunford's framework |

## Folder Structure

```
projects/pmmstack/
├── CLAUDE.md              ← this file
├── README.md              ← public README (shown on GitHub)
├── DISTRIBUTION.md        ← how to install + use the skill pack
├── .gitignore
├── .claude/               ← Claude Code config scoped to this project
└── skills/
    ├── jtbd-miner/
    ├── jtbd-validator/
    ├── icp-definer/
    └── positioning-workshop/
```

## GitHub Repo Status

Currently lives inside the `PMMstack` repo alongside newsletter code. Being split in Pass 2 of the April 2026 reorg.

- **To do:** rename old `PMMstack` repo on GitHub → `pmmstack-legacy`
- **To do:** create fresh `pmmstack` repo, init from `projects/pmmstack/`, push
- **To do:** set up install flow: users clone + copy skills into their `~/.claude/skills/`

DISTRIBUTION.md has the current install instructions — may need updating after the rename.

## Relationship to The Battlecard

PMM Stack is distributed BY The Battlecard brand. The Battlecard newsletter promotes and documents it. The skills are usable standalone — installing PMM Stack doesn't require the newsletter or anything else in Paul's AI-Lab.

## Design Principles

- Every skill follows Claude Code's SKILL.md convention
- Outputs are structured (not free-form prose) so PMMs can reuse them across tools
- Every skill includes a `references/` folder with the source methodology it's based on
- Skills work in Cursor / Claude Code / Cowork — no vendor lock-in
