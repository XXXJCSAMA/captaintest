---
name: saas-gtm-navigator
description: Full GTM strategy skill for SaaS founders. Use this skill whenever a user mentions launching a SaaS product, finding first customers, positioning their product, defining their ICP, writing a launch post, preparing for Product Hunt, posting in communities like SaaSBoomi or Indie Hackers, competitive positioning, or anything related to go-to-market strategy. Also trigger when user says things like "how do I get users", "who should I target", "how do I launch", "what's my positioning", "how do I stand out from competitors", or "where do I post about my product". This skill works for Indian SaaS founders, global indie hackers, and B2B SaaS teams at any stage.
---

# SaaS GTM Navigator

A structured GTM skill for SaaS founders covering ICP definition, competitive positioning, and launch sequencing. Works for Indian founders, global indie hackers, and B2B teams with a live product.

---

## How to use this skill

When triggered, first ask the user ONE question to understand where they are:

> "Tell me about your product in one sentence — what it does and who it's for."

Then identify which of the three modules applies and run that module. You can run multiple modules in sequence if the user needs a full GTM plan.

---

## Module 1: ICP Definition + Positioning

**Trigger phrases:** "who should I target", "what's my ICP", "who is my customer", "help me with positioning", "what's my niche"

### Step 1 — Extract product context

Ask the user (combine into one message, don't ask one by one):
- What does your product do in one sentence?
- What problem does it solve?
- Who have you built it for so far? (even assumptions)
- What's the pricing or intended pricing?

### Step 2 — Build the ICP

Output a structured ICP with these fields:

```
IDEAL CUSTOMER PROFILE

Company type: [B2B/B2C/Both] | [Industry] | [Size: solo/startup/SMB/enterprise]
Geography: [Primary market]
Role: [Job title of the buyer/user]
Pain: [The specific problem they have RIGHT NOW]
Current solution: [What they use today to solve this — even if it's manual]
Trigger event: [What happens in their life/work that makes them look for a solution like yours]
Budget signal: [Are they already paying for something similar? How much?]
Where they hang out: [Specific communities, platforms, Slack groups, subreddits]
```

### Step 3 — Write the positioning statement

Use this formula:
> For [ICP role] at [company type] who [have this pain], [Product name] is the [category] that [key benefit] unlike [alternative] which [limitation of alternative].

Give 2 variants — one direct, one story-led.

### Step 4 — One-liner for cold outreach

Write a 1-sentence product description the founder can use in any cold message. Under 20 words. No jargon. Must include the pain and the outcome.

---

## Module 2: Competitive Positioning

**Trigger phrases:** "how do I stand out", "my competitors are", "what makes me different", "competitive analysis", "positioning against X"

### Step 1 — Map the landscape

Ask:
- Who are your top 2-3 competitors? (name them)
- What do customers complain about those competitors? (app reviews, Twitter, Reddit)
- What's one thing you do that none of them do?

### Step 2 — Build a positioning table

Output a simple comparison:

```
COMPETITIVE LANDSCAPE

              | You | Competitor A | Competitor B
[Feature 1]   | ✅  |      ✅      |      ❌
[Feature 2]   | ✅  |      ❌      |      ✅
[Price]       | $X  |      $Y      |      $Z
[Key diff]    | ✅  |      ❌      |      ❌
```

Fill in based on what the user tells you. Note: always ask for real competitor info, don't invent.

### Step 3 — Define the wedge

The wedge is the ONE thing that makes switching to your product the obvious decision for a specific buyer. It should be:
- Specific (not "easier to use")
- Verifiable (customer can test it in 5 minutes)
- Painful to live without (losing it costs them something real)

Output: "Your wedge is [X]. Lead every conversation, every post, every cold message with this."

### Step 4 — Battlecard (one page)

A quick-reference card the founder can use in sales conversations:

```
BATTLECARD: You vs [Main Competitor]

When prospect says "[Competitor]":
→ Acknowledge: "Yes, [Competitor] is solid for [use case]."
→ Redirect: "The difference is [your wedge]."
→ Proof: "One of our customers switched because [specific reason]."

Their weakness: [X]
Your strength: [Y]
Closing question: "Is [competitor weakness] costing you [specific pain]?"
```

---

## Module 3: Launch Sequence

**Trigger phrases:** "how do I launch", "Product Hunt launch", "where do I post", "launch plan", "first users", "launch checklist"

Read `references/launch-channels.md` for channel-specific templates and tactics.

### Step 1 — Assess launch readiness

Ask:
- Is your product live and usable today?
- Do you have any existing users (even 1)?
- What's your geography focus — India, global, or both?
- Do you have a landing page?

### Step 2 — Sequence the launch

Output a phased plan:

**Phase 1 — Warm launch (Week 1-2): Your network first**
- Post in personal LinkedIn/Twitter with honest founder story
- DM 20 people who fit your ICP from your existing network
- Goal: 5-10 users who will give feedback, not just sign up

**Phase 2 — Community launch (Week 2-3): Targeted communities**
Based on geography, prioritize channels from `references/launch-channels.md`:
- Indian founders: SaaSBoomi Slack, iSPIRT WhatsApp, Indie Hackers India
- Global: Indie Hackers, Hacker News (Show HN), relevant subreddits
- Rule: Give value first, pitch second. Share what you learned building, not just "check out my product"

**Phase 3 — Public launch (Week 3-4): Product Hunt + press**
- Only launch on PH when you have 10+ happy users who can upvote and comment
- Prep a Hunter (someone with PH followers to post for you)
- Write your PH tagline using the positioning statement from Module 1

### Step 3 — Write launch assets

Generate ready-to-post versions of:

**LinkedIn post (founder story format):**
```
[Hook — a specific painful moment that led to building this]

[What you built and why]

[What makes it different — one line]

[Social proof if any — even "5 founders are already using it"]

[Call to action — specific and low friction]

[Link]
```

**Show HN post:**
```
Show HN: [Product name] – [what it does in 8 words]

[2-3 paragraphs: the problem, how you solved it, what stage you're at]

[Honest ask: looking for feedback / early users / specific type of user]
```

**SaaSBoomi/community Slack post:**
```
Built something for [specific ICP]. Would love 5 founders to try it and tear it apart.

[One line on the problem]
[One line on your solution]
[One line on what you're NOT — sets expectations]

DM me or drop your email — will personally onboard you.
```

---

## General principles embedded in this skill

- **ICP before everything.** A founder who can name one specific person who needs their product will always outperform one with a broad target market.
- **Positioning is a choice, not a description.** You're not describing your product — you're choosing a battle you can win.
- **Launch to learn, not to go viral.** The goal of launch week is 10 honest conversations, not 10,000 signups.
- **Wedge thinking.** One sharp differentiator beats five features in every sales conversation.
- **Indian market context.** WhatsApp outreach converts 3-5x better than email for Indian founders. SaaSBoomi Slack is the highest-leverage community in Indian SaaS. Price in INR when targeting Indian buyers — USD pricing creates friction.
