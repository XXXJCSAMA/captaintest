# SaaS-GTM-Navigator

A free, open source Claude Skill for SaaS founders.

Tell Claude about your product it handles ICP definition, competitive positioning, and launch sequencing automatically. No prompting required.

Works for Indian founders and global indie hackers.

---

## What it does

Most founders waste hours figuring out who to target, how to position against competitors, and where to launch. This skill embeds that entire GTM thinking process directly into Claude.

Three modules activate automatically based on what you say:

| Module | Trigger | What you get |
|---|---|---|
| **ICP + Positioning** | "who should I target", "what's my ICP", "help me with positioning" | Structured ICP profile, positioning statement, one-liner for cold outreach |
| **Competitive Positioning** | "how do I stand out", "my competitors are X", "what makes me different" | Competitive landscape table, your wedge, a battlecard for sales conversations |
| **Launch Sequence** | "how do I launch", "where do I post", "Product Hunt launch" | Phased launch plan, ready-to-post copy for LinkedIn, HN, SaaSBoomi, Reddit |

---

## How to install

**Step 1 — Download the skill**

Click the green **Code** button on this repo → **Download ZIP**

Extract the ZIP. You'll see a folder called `saas-gtm-skill` inside.

**Step 2 — Re-zip just the skill folder**

You need to zip only the `saas-gtm-skill` folder itself (not the whole repo).

- On Mac: right-click `saas-gtm-skill` → Compress
- On Windows: right-click `saas-gtm-skill` → Send to → Compressed folder

**Step 3 — Upload to Claude**

1. Go to [claude.ai](https://claude.ai) and sign in
2. Click **Customize** (left sidebar) → **Skills**
3. Click the **+** button → **Upload a skill**
4. Select the `saas-gtm-skill.zip` file you just created
5. Your skill appears in the list — toggle it **on**

> Note: Skills require a Claude Pro, Max, Team, or Enterprise plan. Free tier does not support Skills.

---

## How to use it

Once installed, just start a conversation with Claude normally. No special commands needed.

**For ICP and positioning:**
> "I'm building a tool that helps D2C brands track their inventory automatically. Who should I be targeting?"

Claude will run Module 1 — ask you a few quick questions, then output a full ICP profile and positioning statement.

**For competitive positioning:**
> "My main competitors are Zoho Inventory and Unicommerce. How do I stand out?"

Claude will run Module 2 — build a competitive landscape table, identify your wedge, and give you a battlecard.

**For launch planning:**
> "My product is live. How do I get my first 10 customers?"

Claude will run Module 3 — give you a phased launch plan with ready-to-post copy for LinkedIn, Hacker News, SaaSBoomi Slack, and Reddit.

**For a full GTM plan in one shot:**
> "Help me build a full GTM plan for my product. Here's what it does: [description]"

Claude will run all three modules in sequence.

---

## What's inside

```
saas-gtm-skill/
├── SKILL.md                        # Core skill — ICP, positioning, launch modules
└── references/
    └── launch-channels.md          # Channel playbook — SaaSBoomi, PH, HN, Reddit, 
                                    # outreach templates, timing guide
```

---

## Indian founder notes

This skill has specific context for the Indian SaaS ecosystem baked in:

- SaaSBoomi Slack and iSPIRT WhatsApp outreach templates included
- WhatsApp-first outreach approach (converts 3-5x better than email for Indian buyers)
- INR pricing guidance for Indian market positioning
- Indian launch channels: SaaSBoomi, Indie Hackers India, LinkedIn India, Product Hunt India

---

## Contributing

Found a channel that works better? Have a positioning framework that's missing? PRs are welcome.

Specifically looking for contributions on:
- Regional language market GTM (Marathi, Tamil, Telugu, Hindi SaaS markets)
- Enterprise India GTM (BFSI, manufacturing, logistics)
- Southeast Asia launch channels

---

## License

Apache 2.0 — free to use, modify, and distribute.

---

Built by [Saurabh Ahire](https://github.com/automatewithsaurabh)
