# Commercial Cofounder

A structured framework for tech founders who'd rather build than sell. It won't let you skip the hard commercial work — but it will make it systematic, conversational, and actually useful.

## What This Is

You're great at building. You're probably not great at (or interested in) figuring out who your customer is, what they actually want, or whether your business model makes any sense. That's normal — most technical founders are the same way.

This framework is your commercial cofounder. It takes you through a structured process to:

1. **Define your ICP** — not "developers" but the specific person who will pay you money
2. **Map your assumptions** — separate what you know from what you believe
3. **Test those assumptions** — design real experiments, not just "talk to users"
4. **Track what you learn** — so you actually make progress instead of going in circles

## How to Use It

### Quick Start
Open Claude in this directory and run:
```
/cofounder
```
It'll figure out where you are and tell you what to do next.

### The Skills (Interactive)
| Command | What It Does |
|---------|-------------|
| `/cofounder` | Entry point — assesses your stage, routes you |
| `/w3` | Deep dive on Who/What/Why (your ICP) |
| `/canvas` | Fill out a LEAN(er) or LEAN Canvas |
| `/customers` | Map customer Pains, Gains, and Jobs-to-be-Done |
| `/assumptions` | Extract and prioritize your business assumptions |
| `/valueprop` | Articulate your value proposition |
| `/sizing` | Calculate your Minimum Success Criteria |
| `/experiment` | Design a test for your riskiest assumption |
| `/learning` | Capture learnings from an experiment |
| `/review` | Weekly progress check-in |
| `/stage` | Check what stage you're at |

### The Docs (Reference)
The `framework/` directory has the theory and process behind each step. Read them if you want to understand *why* you're doing something, or if a skill references a concept you're not familiar with.

### The Templates
The `templates/` directory has blank, fillable versions of every exercise. Use them directly if you prefer working in markdown over running the interactive skills.

## The Process

```
Define your customer (W3) 
  → Model your business (Canvas) 
    → Map what you know about them (Customer Insights)
      → Identify what you're assuming (Assumptions)
        → Say what you do clearly (Value Prop)
          → Size the opportunity (MSC)
            → Test your riskiest assumption (Experiment)
              → Learn from it (Learning Card)
                → Repeat faster
```

You don't have to go in strict order. The `/cofounder` skill will help you figure out where to start based on what you've already done.

## Your Working Files

As you work through the process, your outputs accumulate in `state/`. This is your startup's commercial brain — your W3 answers, canvas, assumptions, experiment results, and weekly reviews all live there and build on each other.

## Credits

Framework inspired by the ULTRA.VC accelerator methodology, Ash Maurya's Lean Stack, Strategyzer's testing tools, Clayton Christensen's Jobs-to-be-Done, and Eric Ries' Lean Startup.
