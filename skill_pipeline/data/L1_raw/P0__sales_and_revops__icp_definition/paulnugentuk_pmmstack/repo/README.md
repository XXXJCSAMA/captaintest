# PMMstack
Four structured product marketing skills using Claude to take you from a URL to validated jobs to be done, a scored ICP, and a positioning document. Three are interactive office-hours sessions that force you to think before the AI researches. One is a fast research tool that feeds the others.

I'm a product and growth marketer who has done ICP/JTBD/Positioning processes manually a lot for tech firms over the years. Most AI skills I've seen in this space are one-shot: paste a link/your idea, AI does work, you get a report and feel smart. But the end output of this product marketing work should be as much about sharpening your insight as it is the document you end up with. These skills take a different approach, inspired by /office-hours in gstack — they're structured conversations that make you do the thinking work first, then use AI to validate, challenge, and extend your thinking. The output is better too because it's grounded in what you actually know (and what you don't).

## Frameworks used

These skills draw on established product marketing and innovation frameworks:

- **Clayton Christensen** — Jobs-to-be-Done theory (Competing Against Luck)
- **Tony Ulwick** — Outcome-Driven Innovation, Opportunity Scoring
- **Bob Moesta** — Four Forces of Progress (Demand-Side Sales 101)
- **Alan Klement** — Compensatory Behaviours (When Coffee and Kale Compete)
- **April Dunford** — Positioning methodology (Obviously Awesome, Sales Pitch)
- **Lincoln Murphy** — ICP evaluation framework (Sixteen Ventures)
- **Rahul Vohra / Sean Ellis** — PMF segmentation method (Superhuman)

## The skills

### 0. JTBD Miner (`skills/jtbd-miner/`)

Extracts candidate Jobs-to-be-Done from any product or company URL.

**What it does:** Fetches the page and analyses it through six lenses — feature-to-outcome translation, customer voice, case study headlines, pricing structure, "who it's for" signals, and conspicuous absence. Produces 3-5 candidate job statements with signal strength ratings and a quick evidence check.

**Key feature:** This is the fast entry point. Give it a competitor URL or your own product page, and it generates a prioritised shortlist of candidate jobs ready to feed into the JTBD Validator.

### 1. JTBD Validator (`skills/jtbd-validator/`)

Validates whether a Job-to-be-Done is real, underserved, and worth building against. Uses frameworks from Christensen, Ulwick, Moesta, and Klement.

**What it does:** Walks you through five phases — sharpening your job statement, assessing forces of progress, gathering external evidence, scoring the opportunity, and synthesising a verdict with risks and next steps.

**Key feature:** Phases 1-2 are blocking. You have to articulate what you already know before Claude does any research. This is deliberate — it produces better outputs and surfaces your own knowledge gaps. I've built it to work one JTBD at a time because the thinking is sharper that way.

### 2. ICP Definer (`skills/icp-definer/`)

Defines and evaluates Ideal Customer Profiles through a job-first lens — starting from who has the job most acutely rather than firmographic filters.

**What it does:** Walks you through generating 2-3 candidate ICPs, then validates them with external evidence, scores them on nine dimensions (Murphy's framework, Vohra/Ellis method), and produces ICP Cards with bottom-up market sizing.

**Key feature:** Can chain directly from the JTBD Validator — it consumes the validated job statement, forces assessments, and evidence so you don't repeat context.

### 3. Positioning Workshop (`skills/positioning-workshop/`)

A guided positioning workshop based on April Dunford's Obviously Awesome methodology. Walks through the five components in sequence with firm pushback on weak answers.

**What it does:** Takes you through competitive alternatives, unique attributes, value themes, target customer, and market category — producing a structured positioning document with full reasoning chain.

**Key feature:** Includes reference transcripts from Dunford's Lenny's Podcast appearances (very cool that he has made these public btw) and a pushback patterns library extracted from her books, podcasts, and writing. The AI becomes a better approximation for how Dunford would challenge your thinking.

## The chain

The skills are designed to work as a sequence:

```
JTBD Miner → JTBD Validator → ICP Definer → Positioning Workshop
```

Each skill can run standalone, but they're strongest when chained. The Miner extracts candidate jobs from a URL, the Validator pressure-tests one in depth, the ICP Definer figures out who has that job worst, and the Positioning Workshop nails how to position for that customer. By the end, you have a validated job, a scored ICP with market sizing, and a complete positioning document — all grounded in evidence and your own thinking.

## Session design

The full PMMstack chain takes approximately 90-120 minutes of active work. This is too long for a single session — input quality degrades as the user fatigues, and the later skills (which require the sharpest thinking) get the worst inputs.

### Recommended session boundaries

| Session | Skills | Duration | User effort |
|---------|--------|----------|-------------|
| 1 | JTBD Miner + Validator (Phases 1-2) | ~25 min | High (thinking work) |
| 2 | Validator (Phases 3-5) + ICP Definer (Phases 1-2) | ~30 min | Medium (reacting to research) |
| 3 | ICP Definer (Phases 3-5) + Positioning Workshop (Phases 0-2) | ~30 min | Medium-High (judgment calls) |
| 4 | Positioning Workshop (Phases 3-5) + final document | ~20 min | Medium (refining and confirming) |

Each skill produces a saved artifact (markdown report) that the next skill consumes. Sessions can be days apart — the artifacts carry the context.

### Scaffolding principle

When running 1:1 with an AI (rather than in a cross-functional team workshop), the skills compensate for missing voices by doing more preparatory work: pre-populating attributes from product evidence, offering structured choices, and using research to prime collaborative phases. Your unique contribution is domain knowledge and judgment. Claude's unique contribution is structure, evidence synthesis, and framework enforcement.

### Miner → Validator handoff

The Miner produces raw candidate job statements that will score 10-15/25 on the Job Statement Quality Rubric. This is by design — the Miner finds the veins, the Validator assays the ore. The Miner's output includes an expectation-setting note so users aren't surprised when the Validator's first move is to sharpen their statement.

## Installation

Requires a Claude Pro, Team, or Enterprise subscription.

### Claude Code

Copy the skill folders into your Claude Code skills directory:

```bash
# Clone or download this repo, then:
cp -r skills/jtbd-miner/ ~/.claude/skills/jtbd-miner/
cp -r skills/jtbd-validator/ ~/.claude/skills/jtbd-validator/
cp -r skills/icp-definer/ ~/.claude/skills/icp-definer/
cp -r skills/positioning-workshop/ ~/.claude/skills/positioning-workshop/
```

### Cowork

If using Claude's Cowork mode, place the skill folders in your workspace's `.claude/skills/` directory.

## Design inspiration

The office-hours approach — where the AI interrogates you before doing work — was inspired by [gstack](https://github.com/garrytan/gstack). I wanted to bring that same energy to the core PMM workflows I've run manually for years.

---

Built by [Paul Nugent](https://www.linkedin.com/in/pauldnugent/). 
