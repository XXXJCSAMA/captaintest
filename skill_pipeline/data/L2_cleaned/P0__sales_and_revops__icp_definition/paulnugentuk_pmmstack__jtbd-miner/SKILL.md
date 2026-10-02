---
name: jtbd-miner
description: >
  Extracts candidate Jobs-to-be-Done from a product or company URL by analysing
  feature copy, customer quotes, case studies, pricing tiers, and positioning —
  then reframes them as solution-free job statements with initial signal strength
  ratings. Produces a prioritised shortlist ready to feed into the jtbd-validator
  skill. Use this skill whenever a user provides a URL and wants to understand
  what jobs a product serves, extract JTBD from a website, analyse a competitor
  through a jobs lens, reverse-engineer a product's demand side, identify what
  jobs a company is implicitly solving, or figure out what jobs to investigate
  before running a full validation. Also trigger when users say things like
  "what jobs does this product solve", "analyse this site for JTBD",
  "what are the jobs here", "mine this for jobs", "help me find the jobs
  in this product", or provide a URL with a request to understand the
  product through a JTBD lens.
---

# JTBD Miner Skill

## What This Skill Does

Takes a product or company URL, analyses the page through a demand-side lens, and
extracts a prioritised shortlist of 3-5 candidate Jobs-to-be-Done. Each candidate
job comes with a properly formatted job statement, the page evidence that surfaced
it, and an initial signal strength rating from a quick evidence check.

This is a lightweight research tool, not a full validation session. The output is
designed to feed directly into the jtbd-validator skill for deep investigation.

## How It Works

### Step 1: Fetch and Analyse the URL

Use web_fetch to retrieve the page content. If the URL is a homepage, also fetch
2-3 linked pages that are likely to contain job-revealing content:
- /pricing or /plans (different tiers often serve different jobs)
- /customers or /case-studies (customer language reveals actual jobs)
- /about or /why-us (positioning reveals intended jobs)
- /features or /product (feature copy reveals functional jobs)

Don't fetch more than 4 pages total — this is meant to be fast.

### Step 2: Read Through Six Lenses

Analyse the page content through each of these lenses. Not every page will have
material for all six — use what's available.

**Lens 1: Feature-to-Outcome Translation**
Look at feature descriptions and product capabilities. For each significant feature
cluster, ask: "What decision or outcome does this enable? What goes wrong without it?"

Don't just restate the feature. "Real-time dashboards" is a feature. The job might be
"Spot problems before they become crises so I'm not blindsided in the Monday standup."

Common trap: accepting the product's own framing. They'll say "powerful analytics."
That's marketing, not a job. Push through to the struggling moment.

**Lens 2: Customer Voice**
Look for testimonials, customer quotes, case study pull-quotes, and review snippets.
Customers describe jobs in their own words, usually more concretely than the company's
marketing copy. Pay attention to:
- What problem they describe having BEFORE the product
- What outcome they describe AFTER
- The emotional language they use (relief, confidence, control)

**Lens 3: Case Study Headlines**
Case study titles and summaries reveal jobs the marketing team may not have explicitly
articulated. "How [Company] reduced onboarding time by 60%" reveals a job around
accelerating time-to-value for new hires. Extract the implied job, not just the metric.

**Lens 4: Pricing Structure**
Different pricing tiers often serve different jobs implicitly:
- Free/basic tier: usually a lightweight or individual job
- Mid tier: usually the core job for the primary ICP
- Enterprise tier: often a different job entirely (compliance, governance, scale)

Look at what features gate each tier — the gates reveal what the company thinks
different customer types value most.

**Lens 5: "Who It's For" Signals**
Look for explicit ICP statements, industry pages, persona pages, or use-case pages.
These reveal who the company THINKS has the job. But note the gap between who they
target and what the customer evidence says — sometimes these diverge, revealing
underserved or mis-served jobs.

**Lens 6: Conspicuous Absence**
What does the product NOT address that adjacent products do? What complaints or
requests might exist in the gap? This lens is speculative but can surface interesting
candidate jobs that the company hasn't yet addressed.

### Step 3: Generate Candidate Job Statements

From the lens analysis, generate 3-5 candidate job statements. Apply basic JTBD
hygiene to each:

**Each statement must be:**
- Solution-free (no product names, no technology references)
- Circumstance-specific (who is the person, what situation are they in)
- Progress-oriented (describes transformation, not a task)
- Written in natural language (how a real person would describe the struggle)

**Format each candidate as:**
```
JOB [N]: [Job statement]
Source: [Which lens/page element surfaced this]
Page evidence: [Brief quote or paraphrase from the page that supports this]
```

### Step 4: Quick Signal Check

For each candidate job, run ONE web_search query to check for demand signal.
Look for evidence that real people describe this struggling moment independently
of the product being analysed.

Good search queries:
- "[role] frustrated with [current approach to this job]"
- "[the problem described] workaround"
- "[the outcome described] how to"

This is a quick check, not a full validation. You're looking for:
- **High signal:** Multiple independent sources describing this struggle
- **Medium signal:** Some mentions, but not widespread
- **Low signal:** Minimal independent evidence (doesn't mean the job isn't real —
  may mean it's niche or the language is different)

### Step 5: Prioritise and Present

Present the candidate jobs as a ranked list, ordered by signal strength.

**For each candidate job, present:**

1. **Job Statement** — Clean, solution-free, circumstance-specific
2. **Source** — Which analytical lens surfaced it
3. **Page Evidence** — The specific copy, quote, or structural element that
   revealed this job
4. **Signal Strength** — High / Medium / Low, with a one-line explanation
5. **Worth Investigating If...** — A one-line qualifier that helps the user
   decide whether this job is relevant to THEM. Examples:
   - "Worth investigating if your target is mid-market teams without a dedicated
     ops function"
   - "Worth investigating if you believe the current solutions are overbuilt
     for the actual job"
   - "Worth investigating if the emotional dimension (credibility anxiety) is
     as strong as the case studies suggest"

**After the list, offer the handoff:**
"Pick the 1-2 jobs that feel most relevant to what you're building, and I can
run them through a full JTBD validation — pressure-testing the job statement,
mapping the forces, gathering evidence, and scoring the opportunity."

## Tone and Approach

- This is a quick, analytical tool. Less conversational than the Validator or
  ICP Definer — more like a research brief.
- Be direct about what the page reveals and what it doesn't. "The website is
  heavy on feature copy but light on customer evidence, so these jobs are
  inferred from capability claims rather than validated demand" is useful context.
- Don't over-generate. 3-5 candidate jobs is the sweet spot. More than 5 dilutes
  the signal and creates choice paralysis.
- Be honest about signal strength. A "Low" rating isn't a failure — it means the
  job needs more investigation, which is exactly what the Validator does.

## Handling Edge Cases

- **URL is a landing page with minimal content:** Fetch additional pages (about,
  features, pricing). If still thin, say so and present what you can extract,
  noting the low confidence.

- **URL is a competitor the user wants to analyse:** Great use case. Frame the
  output as "these are the jobs [competitor] appears to be positioning against."
  This is useful competitive intelligence even before validation.

- **URL is the user's own product:** Also great. Frame the output as "these are
  the jobs your current positioning implies. The question is whether these are
  the RIGHT jobs to anchor on." Natural lead-in to both the Validator and the
  ICP Definer.

- **URL returns a paywall or login wall:** Let the user know and ask if they can
  paste the relevant page content instead.

- **URL is not a product page (e.g., blog post, article):** Adapt — extract jobs
  from the problems and solutions discussed in the content, but note that this
  is editorial interpretation rather than product positioning analysis.

- **Multiple URLs provided:** Process the primary URL first. If the user provides
  2-3 URLs (e.g., competitors to compare), process each and present the jobs
  side by side, noting overlaps and divergences across products.
