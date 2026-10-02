---
name: icp-definer
description: >
  Defines and evaluates Ideal Customer Profiles through a job-first lens — starting
  from who has the job most acutely rather than firmographic filters. Uses frameworks
  from Dunford, Murphy, Vohra/Ellis, and JTBD canon. Produces 2-3 candidate ICPs with
  comparison scoring and bottom-up market sizing. Can chain from the jtbd-validator
  skill output or work standalone. Use this skill whenever a user wants to define an
  ICP, identify their ideal customer, figure out who to sell to, evaluate target
  segments, compare customer profiles, size a market for a specific audience, or
  determine product-market fit by segment. Also trigger when users mention "ICP",
  "ideal customer profile", "target customer", "who should I sell to", "customer
  segmentation", "best-fit customer", "target audience", "beachhead market",
  "who is my customer", "market sizing", "TAM SAM SOM", or "who has this problem worst".
---

# ICP Definer Skill

## What This Skill Does

Runs a structured office-hours session that helps users define, evaluate, and size 2-3
candidate Ideal Customer Profiles. The core reframe: an ICP isn't a demographic profile —
it's "who has this job most acutely, with the fewest switching barriers, and the most
willingness to pay." The session produces ICP cards with comparison scoring and bottom-up
market sizing so users can make an informed bet on who to target first.

## Before You Start

Read the canonical reference at `references/icp-canon.md` in this skill's directory.
It contains the frameworks, scoring rubrics, and sizing methodology you'll apply throughout
the session.

## Chaining from JTBD Validator

This skill can follow directly from the jtbd-validator skill. If the user has just completed
a JTBD validation session, they'll have:
- A validated job statement
- A forces assessment (Push, Pull, Anxiety, Habit)
- Evidence gathered during Phase 3
- An opportunity score

Use all of this as input — reference it, don't re-ask for it. Start at Phase 1 with the
job statement already in hand and skip questions the user has already answered.

If there's no JTBD Validator output, the skill works standalone. Phase 1 will collect the
necessary job context.

## Session Flow

The session is conversational but structured. As with the JTBD Validator, early phases
require the user to do thinking work before Claude researches.

---

### Phase 1: Job & Context Grounding

**Goal:** Establish what job we're defining the ICP around, and what the user already knows
about who has it.

**If chaining from JTBD Validator:**
Briefly recap the validated job statement and key findings. Then move directly to asking
about customer knowledge.

**If standalone:**
Ask for three things:
1. The job statement or problem they're solving (help sharpen it if needed, but don't
   run the full JTBD Validator — suggest that skill if the job statement is very rough)
2. What product or solution they're building / offering
3. What they already know about who might want this

**Then ask the user to describe who they think their customer is today:**
- Who have they talked to, sold to, or built for?
- If pre-product: who have they seen struggling with this problem?
- If they have existing customers: who are their best ones, and why?

**Apply Dunford's Best-Fit lens:**
If they have existing customers or strong prospects, ask what those people have in common.
Not demographics — circumstances. What situation are they in? Why do they care more than
others? Push past firmographics to get at the WHY.

**Output of Phase 1:** The job statement (validated or working), and the user's current
understanding of who their customer is. Note any gaps in their knowledge.

---

### Phase 2: Candidate ICP Generation

**Goal:** Help the user generate 2-3 distinct candidate ICPs to evaluate. This is where
the user does the thinking work.

**Start by asking:** "Based on what you know, who are 2-3 *different types* of people or
companies who might have this job? Don't just give me variations on company size — think
about different circumstances, different triggers, different levels of pain."

**Help them generate candidates if they're stuck.** Use these prompts:
- "Who has this job AND is already spending money trying to solve it?"
- "Who has this job AND has the fewest switching barriers?"
- "Who has this job AND would get the most outsized value from a solution?"
- "Is there a group that has this job in an acute but different way than you initially thought?"

**For each candidate, get the user to articulate:**
1. **Who they are** — Role, company type, situation (not just "Series B SaaS" — what *about* a Series B SaaS company creates this job?)
2. **Why the job is acute for them** — What about their circumstance makes this problem worse?
3. **What they're doing today** — Current solution, workaround, or nothing?
4. **What buying looks like** — Who decides? What budget? How long is the sales cycle likely to be?

Use the ask_user_input tool for structured comparisons where it helps — for example,
asking the user to rank which candidate they think has the most acute version of the job.

**Important:** Push for genuine differentiation between candidates. "SMB vs. Enterprise"
is lazy segmentation. "Solo PMM at a startup who does everything vs. PMM team lead at a
growth-stage company who needs to arm her team vs. VP Marketing at a scale-up who needs
board-ready CI" — that's circumstance-driven segmentation.

**Output of Phase 2:** 2-3 clearly articulated candidate ICPs with the user's hypotheses
about each.

---

### Phase 3: Evidence & Validation

**Goal:** Claude researches to validate, challenge, or extend the user's hypotheses about
each candidate ICP.

**For each candidate ICP, search for:**

1. **Problem intensity signals**
   - Reddit, forums, G2 reviews from people matching this profile
   - Look for: language intensity, frequency of complaints, emotional stakes
   - Compare across candidates: which group sounds most frustrated?

2. **Compensatory behaviours**
   - Are people in this segment building workarounds, hiring for this, buying adjacent tools?
   - This is the strongest signal that the job is real AND underserved for this group

3. **Willingness to pay signals**
   - Are they already spending on this problem? (Tools, agencies, headcount)
   - What's the implied budget based on what they currently spend?
   - Are there competitor products priced specifically for this segment?

4. **Competitor targeting**
   - Which competitors explicitly target each candidate ICP?
   - Look at: competitor website messaging, case study pages, G2 reviewer profiles
   - High competitor density isn't automatically bad — it validates the segment exists.
     But it raises the bar for differentiation.

5. **Market sizing data**
   - LinkedIn Sales Navigator counts (or equivalent) for each candidate
   - Industry association data, census data, analyst reports
   - Job listing volumes for relevant roles (proxy for segment size)
   - If Ahrefs or similar tools are available, check search volume for segment-specific terms

**Classify evidence by candidate ICP** so the comparison is clear.

**Output of Phase 3:** Evidence organised by candidate ICP, with signal strength ratings.

---

### Phase 4: ICP Scoring & Comparison

**Goal:** Score each candidate ICP using the comparison scorecard from the canon reference,
grounded in the evidence from Phase 3.

**Score each candidate across nine dimensions:**

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Job Intensity | High | How acutely does this group experience the job? |
| Switching Readiness | High | Push + Pull vs. Anxiety + Habit |
| Willingness to Pay | High | Already spending on this problem? |
| Success Potential | High | Can they actually succeed with your product? |
| Acquisition Efficiency | Medium | Can you reach and convert them affordably? |
| Market Size | Medium | Is the segment big enough? |
| Ascension Potential | Medium | Will they expand over time? |
| Advocacy Potential | Low-Med | Will they refer and create case studies? |
| Competitive Density | Medium | How many alternatives already target this group? |

**Apply Murphy's framework explicitly** for Success Potential — walk through his six fit
inputs (Technical, Functional, Resource, Competence, Experience, Cultural) for each candidate.

**Apply the Vohra/Ellis lens** for comparison — which candidate would be most "very
disappointed" without a solution? Which one is merely "somewhat disappointed"?

**For Market Size, run a bottom-up sizing estimate for each candidate:**

For each candidate ICP:
1. Estimate the number of companies/people matching the profile
2. Apply a realistic ACV based on willingness-to-pay evidence
3. Calculate TAM = Count × ACV
4. Estimate SAM by filtering for reachability and product fit
5. Estimate SOM by applying a realistic capture rate (1-5% early, 5-15% growth)

Be transparent about confidence levels. Some numbers will be well-sourced, others will be
educated estimates. Label them accordingly.

**Present the comparison as a side-by-side table** in a structured artifact. Make scores
and sizing visible at a glance. Include the evidence behind each score so the user can
challenge specific ratings.

**Output of Phase 4:** Side-by-side comparison scorecard with sizing for each candidate ICP.

---

### Phase 5: Recommendation & ICP Cards

**Goal:** Present a recommendation and produce usable ICP cards.

**Make a recommendation, but frame it as a bet, not a verdict:**
"Based on the evidence, Candidate [X] looks like the strongest starting point because
[specific reasons]. Here's why I'd start there, and here's what could prove me wrong."

**Address the "start here" vs "expand to" distinction:**
- Your beachhead ICP is where you start — the group where you can win fastest
- Adjacent ICPs are where you expand — once you've nailed the beachhead
- Map the candidates into this sequence

**For the recommended ICP (and optionally for all candidates), produce an ICP Card:**

The ICP Card is a structured artifact containing:

1. **ICP Name** — A descriptive label (not "Persona A" — something like "Solo PMM at
   Growth-Stage SaaS")

2. **The Job** — The validated job statement as experienced by this specific ICP

3. **Circumstance Definition** — What situation they're in, what makes the job acute
   for THEM specifically. Written as a narrative paragraph, not bullet points.

4. **Current Solution** — What they do today (tools, workarounds, agencies, nothing)

5. **Switching Profile** (Moesta's forces for this specific ICP):
   - Push: What's driving them away from current approach?
   - Pull: What are they reaching for?
   - Anxiety: What would stop them from switching?
   - Habit: What entrenched behaviour needs to break?

6. **Murphy's Readiness Check:**
   - Ready? (Do they know they have the problem? Is it acute?)
   - Willing? (Are they actively looking or open to solutions?)
   - Able? (Budget, tech stack, org capacity?)

7. **Success Potential Summary** — Can they realistically succeed with your product?

8. **Market Size:**
   - Estimated count of addressable companies/people
   - Estimated TAM / SAM / SOM with assumptions stated
   - Key data sources used

9. **How to Find Them:**
   - Where they gather (communities, events, channels)
   - How to identify them (LinkedIn filters, signals, triggers)
   - What language they use to describe the problem

10. **Key Risk** — The single biggest reason this ICP might not work out

**Frame the ending as a provocation:**
"This is your starting hypothesis. The fastest way to validate it is to talk to 5-10
people who fit this profile and see if the forces match what we've mapped here. Here are
the specific questions to ask them." (Frame interview questions using Moesta's demand-side
approach — ask about the struggling moment and what they've tried, not about your solution.)

---

## Chaining: Offering the Next Skill

At the end of the session, if the user seems ready to move to positioning work, mention
that a positioning skill (Dunford-style) would be a natural next step — taking the
validated job and defined ICP into a positioning statement and sales narrative.

Similarly, the **jtbd-validator** skill should offer to chain into this ICP Definer
at the end of its Phase 5 output.

---

## Tone and Approach

- Same office-hours energy as the JTBD Validator. Thinking partner, not report generator.
- Push back on lazy segmentation. "SMB" is not an ICP. "Series B" is not an ICP.
  Push for circumstance-driven definitions.
- Be honest about sizing confidence. "I found LinkedIn data suggesting ~4,200 companies
  match this filter, but the ACV is an assumption based on competitor pricing" is more
  useful than a false-precision number.
- Name the frameworks explicitly. "Using Murphy's Success Potential framework..." gives
  the output authority.
- The ICP Cards should feel like working documents the user can take into their next
  strategy session or investor conversation — not academic exercises.

## Handling Edge Cases

- **User has no existing customers:** Focus on problem intensity signals from public
  evidence. The Vohra/Ellis method adapts: instead of "very disappointed without product,"
  evaluate "most disappointed with current workaround."

- **User insists on a single ICP:** That's fine — but still generate at least one
  alternative to pressure-test the choice. Confirming a hypothesis by comparing it
  against alternatives is stronger than evaluating it in isolation.

- **Very broad job with many possible ICPs:** Help narrow by asking "Where can you win
  FIRST?" Beachhead thinking. You're not choosing the only ICP forever — you're choosing
  the starting point.

- **User wants to target everyone:** Push back firmly but constructively. "Everyone who
  has this problem" is a TAM, not an ICP. The whole point is to find the segment where
  you can win disproportionately. Reference the Superhuman case — they went from 22% PMF
  across all users to much higher by narrowing to founders/managers/execs.

- **B2C or prosumer context:** Murphy's framework is SaaS-oriented. Adapt: replace
  firmographics with individual circumstances, replace "acquisition efficiency" with
  "channel accessibility," replace "ascension potential" with "lifetime value potential."

- **User disagrees with sizing:** Good — sizing is always partly assumptions. Ask what
  data they have that Claude doesn't. They may know the market better from direct
  experience.
