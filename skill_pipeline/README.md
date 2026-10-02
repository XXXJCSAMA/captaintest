# Skill Pipeline

An offline-first pipeline that crawls Agent Skills from GitHub (L1), cleans and safety-filters them with SkillEvaluator Tier 1 (L2), evaluates and deduplicates them (Tier 1–3), and publishes mountable skills to a storefront catalog (L3/L4).

```
seeds/Domain.docx
        │  scripts/parse_seed_docx.py
        ▼
seeds/domain_topics.json  (priority × domain × topics)
        │  crawler/l1_crawl.py  (GitHub repo + code search)
        ▼
data/L1_raw/<P>__<domain>__<topic>.jsonl
data/L1_raw/<P>__<domain>__<topic>/<repo>/repo/... + metadata.json
        │  filter/batch_tier1.py  (parallel SkillEvaluator Tier 1)
        ▼
data/L2_evaluations/tier1_results_<ts>.jsonl
        │  filter/classify_offline.py  (classify + land, wraps filter/l2_clean.py)
        ▼
data/L2_cleaned/<topic>/<repo>__<skill>/SKILL.md + _lineage.json
data/L2_quarantine/... (rejects / needs_review)
data/L2_cleaned.jsonl, data/L2_rejected.jsonl
        │  filter/build_skill_files.py
        ▼
data/catalog/skill_files.jsonl  (file trees for storefront)
        │  filter/mount_skill.py
        ▼
data/agent_workspaces/<group_chat_id>/<skill_id>/...
```

## 1. Architecture Overview

| Layer | Directory | Purpose |
|---|---|---|
| Seed | `seeds/` | Source of truth for what to crawl: `Domain.docx` → `domain_topics.json`. |
| Ingest (L1) | `crawler/` → `data/L1_raw/` | GitHub search + whitelisted file download. Raw, untrusted. |
| Filter (L2) | `filter/` → `data/L2_cleaned/`, `data/L2_quarantine/`, `data/L2_evaluations/` | SkillEvaluator Tier 1 safety/quality gate, PII redaction, lineage tracking. |
| Catalog (L3/L4 staging) | `data/catalog/`, `data/L3_pending/`, `data/L4_published/`, `data/agent_workspaces/` | Flattened file trees for the storefront and per-chat mounting. |
| Evaluator | `SkillEvaluator/` (vendored upstream) | The underlying `skillevaluator tier1/tier2/tier3` engine this pipeline shells out to. |
| Ops | `logs/` | Timestamped logs for every crawl/clean run. |

Data-stage convention:

- `L1_raw` — raw GitHub harvests, one JSONL + one directory per `(priority, domain, topic)`.
- `L2_cleaned` — skills that passed (`pass`/`warn`); each skill dir carries `_lineage.json`.
- `L2_quarantine` — `reject` / `needs_review` skills kept for inspection, never published.
- `L2_evaluations` — raw Tier 1 batch outputs (`tier1_results_<ts>.jsonl`).
- `L2_cleaned.jsonl` / `L2_rejected.jsonl` — flat indexes of landed skills.
- `L3_pending` / `L4_published` — reserved for human review and final publication.
- `catalog/skill_files.jsonl` — storefront feed: one record per skill with full file contents.
- `agent_workspaces/` — runtime mounts created by `mount_skill.py`.

## 2. File Reference

### 2.1 `scripts/` — seed parsing

| File | Role | Input → Output | Notes |
|---|---|---|---|
| `scripts/parse_seed_docx.py` | Parse the prioritized domain table (2nd table) out of `Domain.docx`. | `seeds/Domain.docx` → `seeds/domain_topics.json` (`{priority: P0\|P1\|P2, domain, quantity, topics[]}`) | Skips header/`TOTAL` rows; splits the scenarios cell on commas; records `total_domains`/`total_topics`. Run once per seed update. |

### 2.2 `seeds/` — crawl specification

| File | Role |
|---|---|
| `seeds/Domain.docx` | Human-authored source: domains, skill quotas, scenario lists. |
| `seeds/domain_topics.json` | Machine-readable crawl plan consumed by `crawler/l1_crawl.py`. |

### 2.3 `crawler/` — L1 ingest

| File | Role | Key behavior |
|---|---|---|
| `crawler/l1_crawl.py` | Crawl Skill *repositories* from GitHub for every `(priority, domain, topic)`. | Builds ~8 repo queries + 4 `filename:SKILL.md/AGENTS.md/CLAUDE.md/.cursorrules` code queries per topic; merges and dedupes by `full_name`; drops repos matching `NEGATIVE_KEYWORDS` (programming/leetcode/homework, etc.); fetches repo metadata → recursive git tree → downloads only whitelisted basenames (`SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `manifest.json`, `LICENSE`, `README.md`) and dirs (`scripts/`, `resources/`, `references/`); writes `data/L1_raw/<P>__<domain>__<topic>.jsonl` plus `<topic>/<repo>/metadata.json` and `<topic>/<repo>/repo/...`. Resumable via `data/L1_raw/.progress.json` (`--force` to redo); `--max-topics`, `--max-skills`, `--only-priority`, `--dry-run` flags; rate-limit aware (needs `GITHUB_TOKEN`, anonymous = 60 req/h). |

### 2.4 `filter/` — L2 clean, classify, publish

| File | Role | Input → Output | Notes |
|---|---|---|---|
| `filter/l2_clean.py` | Core L2 library + standalone cleaner (~511 lines). Discovers every `SKILL.md` under `L1_raw`, runs `skillevaluator tier1 --no-llm -r json`, and classifies each skill. | `data/L1_raw/...` → `data/L2_cleaned/...`, `data/L2_quarantine/...`, `L2_cleaned.jsonl`, `L2_rejected.jsonl` | Decisions: `pass` (all blocking checks clean), `soft_warn`/`warn` (schema/version/quality only), `hard_fail` (critical/high PII, License, real Security/Secrets, Unicode smuggling). Hard-fails get one PII-redaction pass (`user@example.com` → redacted placeholder, `redact_skill_dir`) + Tier 1 re-run; survivors land as `redacted_then_promote`, persistent failures are dropped. Helpers: `run_tier1`, `classify`/`classify_from_report` (severity-aware gate), `collect_pii_values`, `extract_score_card`, `build_lineage`, `copy_skill`, `process_skill`. Enforces `--max-skills-per-repo` (default 10, skip repo over 30) and skips targets already containing `_lineage.json` (idempotent). |
| `filter/batch_tier1.py` | Parallel Tier 1 runner over all `SKILL.md` under `L1_raw`. | `data/L1_raw/...` → `data/L2_evaluations/tier1_results_<ts>.jsonl` | `ProcessPoolExecutor` (`--workers`, default 8; `--topic`/`--all`/`--limit`); each worker runs `skillevaluator tier1 <skill_dir> --no-llm -r json` in a temp dir with `skillspector`/`gitleaks` on `PATH`; emits `{skill_dir, status: ok\|timeout\|no_report, report, returncode}` per row. Skips noisy marketplace repos (`SKIP_REPOS`). Decouples expensive evaluation from landing so `classify_offline.py` can re-run cheaply. |
| `filter/classify_offline.py` | Offline classify-and-land: reads the newest `tier1_results_*.jsonl`, applies `l2_clean.classify_from_report` + `classify` with PII-redact retry, and lands results. | `data/L2_evaluations/tier1_results_*.jsonl` → `data/L2_cleaned/`, `data/L2_quarantine/`, `L2_cleaned.jsonl`, `L2_rejected.jsonl` | Maps internal decisions to spec labels (`pass→pass`, `soft_warn`/`redacted_then_promote→warn`, `hard_fail→reject`, incomplete scans→`needs_review`); rebuilds only topics present in the batch; each landed skill gets `copy_skill` + `_lineage.json` (source repo/URL/commit, scores, reasons, redactions). Rejected rows are mirrored to `L2_rejected.jsonl`. |
| `filter/build_skill_files.py` | Build the storefront feed from landed skills. | `data/L2_cleaned/*/*/_lineage.json` → `data/catalog/skill_files.jsonl` | Walks every `_lineage.json`, reads all sibling files (skipping `_lineage.json` itself) as `{file_path, file_content}`, and emits one JSON record per skill with `skill_id`, `topic`, provenance (`source_repo/url/author/commit/crawled_at`), `decision`, `score_card`, `filter_passed/hard_failed`, and full `files[]`. |
| `filter/mount_skill.py` | Mount a catalog skill into a group-chat workspace. | `data/catalog/skill_files.jsonl` → `data/agent_workspaces/<group_chat_id>/<skill_id>/...` | `add_to_captain(skill_id, group_chat_id)` looks up the skill, recreates its file tree under the workspace, and returns `{status, skill_id, group_chat_id, mounted_files, workspace}`. CLI: `python filter/mount_skill.py <skill_id> <group_chat_id>`. |

### 2.5 `SkillEvaluator/` — vendored evaluation engine

Upstream three-tier evaluator that `filter/` shells out to (do not edit; pin and call it):

- **Tier 1 (static validation)** — schema/governance, semver, PII/secrets/security/unicode-smuggling scans, quality and code-risk checks. Invoked as `skillevaluator tier1 <dir> --no-llm -r json`. See `SkillEvaluator/docs/tier1-validation.mdx`.
- **Tier 2 (deduplication)** — embedding/canonical clustering of near-duplicate skills. See `docs/tier2-deduplication.mdx`.
- **Tier 3 (live evaluation)** — sandboxed agent rollouts with custom graders. See `docs/tier3-live-evaluation.mdx`, `docs/custom-graders.mdx`.

Key entry points: `SkillEvaluator/src/skillevaluator/cli.py`, `config/`, `docs/cli-reference.mdx`, `docs/quickstart.mdx`.

### 2.6 Top-level files

| Path | Role |
|---|---|
| `README.md` | This file. |
| `LICENSE` | Pipeline license. |
| `logs/` | Per-run logs (`l1_crawl_<ts>.log`, `l2_clean_<ts>.log`, `run.out`). |
| `--workers` | Stray artifact, safe to delete. |
| `gitleaks_8.30.1_linux_x64.tar.gz` | Bundled `gitleaks` binary archive used by the Secrets Detection validator. |

## 3. Typical Workflows

```bash
# 0. Parse seed (after editing Domain.docx)
python scripts/parse_seed_docx.py

# 1. Crawl L1 (needs GITHUB_TOKEN)
export GITHUB_TOKEN=ghp_...
python crawler/l1_crawl.py --only-priority P0 --max-skills 100

# 2a. Evaluate all L1 skills with Tier 1 (parallel)
python filter/batch_tier1.py --all --workers 8

# 2b. Classify + land to L2 (offline, re-runnable)
python filter/classify_offline.py

# 2c. (Alternative single-step) run cleaner directly
python filter/l2_clean.py

# 3. Build storefront catalog
python filter/build_skill_files.py

# 4. Mount a skill into a chat workspace
python filter/mount_skill.py <skill_id> <group_chat_id>
```

## 4. Design Notes

- **Offline-first two-phase filtering.** `batch_tier1.py` (slow, parallel, network-free after crawl) is separated from `classify_offline.py` (fast, deterministic) so classification policy can iterate without re-running the evaluator.
- **Idempotent + resumable.** L1 tracks completed topics in `.progress.json`; L2 skips skill targets that already have `_lineage.json`; `classify_offline.py` rebuilds only topics in the current batch.
- **Provenance everywhere.** Every L2 skill carries `_lineage.json` (source repo, commit, URL, crawl/clean timestamps, decision, reasons, score card, redactions), and every catalog record echoes it — any published file traces back to an exact GitHub commit.
- **Conservative safety posture.** Real `hard_fail` categories (PII, license, security, secrets, unicode smuggling) block publication; PII gets exactly one redact-and-retry; marketplace bulk repos are excluded from batch Tier 1 to control noise.
