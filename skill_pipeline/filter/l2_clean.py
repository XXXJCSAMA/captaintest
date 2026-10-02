#!/usr/bin/env python3
"""
L2 Cleaner — apply SkillEvaluator Tier 1 to every skill in L1_raw.

Per spec (2026-10-02):
  - Discover every SKILL.md under data/L1_raw/<topic>/<repo>/repo/
  - Run `skillevaluator tier1 --no-llm -r json` on the containing dir
  - Classify each skill:
      * hard_fail      : critical/high severity in {PII, License, Security(real),
                         Secrets(real), Unicode smuggling}
      * soft_warn      : passed everything hard, but failed schema/version/quality/etc.
      * pass           : all blocking checks passed and no real findings
  - For hard_fail, attempt PII redaction (email -> redacted@skill.local);
    after redaction re-classify. If still hard-fail, drop. Otherwise promote.

  Output layout:
      data/L2_cleaned/<topic>/<repo>__<skill>/SKILL.md  (plus ancillary files)
      data/L2_cleaned/<topic>/<repo>__<skill>/_lineage.json
      data/L2_cleaned.jsonl  (one row per skill)

  Each skill keyed <repo_slug>__<skill_basename>.

  Default policy:
      --max-skills-per-repo 10   (skip repo if SKILL.md count > 30)

Resume:
  Skip skills whose target dir already has _lineage.json (idempotent).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
L1_DIR = ROOT / "data" / "L1_raw"
L2_DIR = ROOT / "data" / "L2_cleaned"
L2_QUARANTINE = ROOT / "data" / "L2_quarantine"
L2_JSONL = L2_DIR / "L2_cleaned.jsonl"
L2_REJECTED = ROOT / "data" / "L2_rejected.jsonl"
LOG_DIR = ROOT / "logs"
TMP_REPORTS = Path("/tmp/se_l2_reports")

# Categories that count as a real security/secrets finding
SEC_CATEGORIES = {"SECRET", "CREDENTIAL", "SECURITY", "PII", "VULNERABILITY"}

# Map validator name -> whether it can produce real hard-fail findings
REAL_HARD_VALIDATORS = {
    "PII Scan",
    "License Compliance",
    "Unicode Smuggling Detection",
    "Security Scan",
    "Secrets Detection",
}

SOFT_VALIDATORS = {
    "Schema & Repository Governance",
    "Semantic Version Validation",
    "QUALITY",
    "Code Risk Analysis",
    "Code Integrity & Hygiene",
    "Dependency Vulnerability Audit",
    "SCRIPT_LINT",
}

PLACEHOLDER_EMAIL = "user@example.com"


# ----------------------------------------------------------------------------- #
# Helpers
# ----------------------------------------------------------------------------- #
def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {msg}",
          flush=True)


def find_topics() -> list[Path]:
    return sorted(p for p in L1_DIR.iterdir() if p.is_dir())


def find_repos(topic_dir: Path) -> list[Path]:
    return sorted(p for p in topic_dir.iterdir()
                  if p.is_dir() and (p / "metadata.json").exists())


def find_skills(repo_dir: Path) -> list[Path]:
    """Return every directory directly containing a SKILL.md (case-insensitive)."""
    repo = repo_dir / "repo"
    if not repo.exists():
        return []
    found: dict[str, Path] = {}
    for p in repo.rglob("*"):
        if p.is_file() and p.name.lower() == "skill.md":
            found[str(p.relative_to(repo))] = p.parent
    return sorted(found.values(), key=lambda d: str(d))


# ----------------------------------------------------------------------------- #
# Tier 1 invocation
# ----------------------------------------------------------------------------- #
def run_tier1(skill_dir: Path, work_dir: Path) -> dict:
    work_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "skillevaluator", "tier1", str(skill_dir),
        "--no-llm",
        "-r", "json",
        "-o", str(work_dir),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    report_path = work_dir / "skillevaluator-tier1.json"
    if not report_path.exists():
        raise RuntimeError(
            f"SkillEvaluator produced no JSON report for {skill_dir}\n"
            f"stdout: {proc.stdout[-500:]}\nstderr: {proc.stderr[-500:]}"
        )
    with report_path.open() as f:
        return json.load(f)


# ----------------------------------------------------------------------------- #
# Classification
# ----------------------------------------------------------------------------- #
def _sev_rank(s: str) -> int:
    return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(s, 0)


def classify_from_report(report: dict) -> tuple[str, list[str] | str]:
    """Spec-level parse: read JSON, not returncode.

    - skillspector-only incomplete -> warn (static done, LLM degraded)
    - other incomplete -> needs_review (neither pass nor reject)
    - critical anywhere -> reject
    - high only counts when from Security/PII-class validators
    - medium/low -> warn
    """
    incomplete = report.get("incomplete_scans", []) or []
    # skillspector has no env-var --no-llm switch and SkillEvaluator does not
    # forward one, so skillspector-only incomplete just means LLM semantic
    # analysis was skipped; static analysis is complete -> degrade to warn.
    if incomplete == ["skillspector"]:
        return "warn", {"reason": "skillspector_llm_degraded"}
    if incomplete:
        return "needs_review", incomplete
    if report.get("overall_status") == "incomplete":
        return "needs_review", incomplete
    severity = report.get("severity_counts", {}) or {}
    if severity.get("critical", 0) > 0:
        return "reject", "critical_issue"
    # Validator-aware high: only Security/PII-class high is hard.
    for r in report.get("results", []):
        if r.get("validator") in REAL_HARD_VALIDATORS:
            real = [f for f in (r.get("findings") or [])
                    if f.get("category") not in {"MISSING_TOOL", "MISSING_SCANNER"}
                    and _sev_rank(f.get("severity", "low")) >= 3]
            if real:
                return "reject", f"{r.get('validator')}_high"
    if severity.get("medium", 0) + severity.get("low", 0) > 0:
        return "warn", severity
    return "pass", None


def classify(report: dict) -> tuple[str, list[str]]:
    """Returns (decision, reasons). decision in {pass, soft_warn, hard_fail}."""
    reasons: list[str] = []
    hard = False

    for r in report.get("results", []):
        vname = r.get("validator", "")
        status = r.get("status", "")
        findings = r.get("findings", [])

        if vname in REAL_HARD_VALIDATORS:
            real_findings = [
                f for f in findings
                if f.get("category") not in {"MISSING_TOOL", "MISSING_SCANNER"}
            ]
            if real_findings:
                max_sev = max(
                    (_sev_rank(f.get("severity", "low"))
                     for f in real_findings),
                    default=0,
                )
                if max_sev >= 3:
                    hard = True
                    cats = {f.get("category") for f in real_findings}
                    reasons.append(
                        f"[hard] {vname}: {len(real_findings)} finding(s), "
                        f"categories={cats}"
                    )

        if vname in SOFT_VALIDATORS and status == "failed":
            msg = r.get("legacy", {}).get("errors", [])
            reasons.append(f"[warn] {vname}: {msg[0] if msg else 'failed'}")

    if hard:
        return "hard_fail", reasons
    if reasons:
        return "soft_warn", reasons
    return "pass", []


def extract_score_card(report: dict) -> dict:
    qs = report.get("quality_summary", [])
    if not qs:
        return {"quality": None}
    q = qs[0]
    return {
        "quality": {
            "overall": q.get("overall_score"),
            "grade": q.get("grade"),
            "skill_type": q.get("skill_type"),
            "dimensions": {
                k: v.get("score") for k, v in (q.get("dimensions") or {}).items()
            },
            "tokens": q.get("metrics", {}).get("total_tokens"),
        },
        "severity_counts": report.get("severity_counts", {}),
    }


# ----------------------------------------------------------------------------- #
# Redaction
# ----------------------------------------------------------------------------- #
def collect_pii_values(report: dict) -> set[str]:
    pii: set[str] = set()
    for r in report.get("results", []):
        if r.get("validator") != "PII Scan":
            continue
        for f in r.get("findings", []):
            md = f.get("metadata") or {}
            v = md.get("matched_value") or md.get("value")
            if v and "@" in v:
                pii.add(v)
    return pii


def redact_skill_dir(skill_dir: Path, pii_values: set[str]) -> dict:
    """Replace PII values with placeholders. Returns {file: n_replacements}."""
    if not pii_values:
        return {}
    counts: dict[str, int] = {}
    for p in skill_dir.rglob("*.md"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        per_file = 0
        for v in pii_values:
            per_file += text.count(v)
            text = text.replace(v, PLACEHOLDER_EMAIL)
        if per_file:
            counts[str(p.relative_to(skill_dir))] = per_file
            p.write_text(text, encoding="utf-8")
    return counts


# ----------------------------------------------------------------------------- #
# Skill copy + lineage
# ----------------------------------------------------------------------------- #
def copy_skill(skill_dir: Path, target_dir: Path) -> None:
    """Copy the whole skill dir (SKILL.md + scripts/, resources/, LICENSE, ...)."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for p in skill_dir.iterdir():
        if p.is_file():
            shutil.copy2(p, target_dir / p.name)
        elif p.is_dir():
            shutil.copytree(p, target_dir / p.name, dirs_exist_ok=True)


def build_lineage(
    l1_path: Path,
    repo_metadata: dict,
    decision: str,
    reasons: list[str],
    score_card: dict,
    l2_path: Path,
    redactions: dict | None = None,
) -> dict:
    return {
        "source_l1_path": str(l1_path.relative_to(ROOT)),
        "source_repo": repo_metadata.get("source_repo"),
        "source_commit": repo_metadata.get("source_commit"),
        "source_url": repo_metadata.get("source_url"),
        "source_author": repo_metadata.get("source_author"),
        "crawled_at": repo_metadata.get("crawled_at"),
        "cleaned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cleaned_by": "skillevaluator_tier1_v0.3.0__no_llm",
        "l2_path": str(l2_path.relative_to(ROOT)) if l2_path else None,
        "decision": decision,
        "filter_passed": [r.strip("[warn] ") for r in reasons
                          if r.startswith("[warn] ")],
        "filter_hard_failed": [r.strip("[hard] ") for r in reasons
                               if r.startswith("[hard] ")],
        "redactions": redactions or {},
        "score_card": score_card,
    }


# ----------------------------------------------------------------------------- #
# Main
# ----------------------------------------------------------------------------- #
def process_skill(skill_dir: Path, meta: dict, target_dir: Path,
                  topic_clean: str) -> tuple[str, dict, list[str], dict | None]:
    """Returns (decision, score_card, reasons, redactions|None)."""
    work_dir = TMP_REPORTS / topic_clean / target_dir.name
    report = run_tier1(skill_dir, work_dir)
    # Spec gate first: incomplete -> needs_review, severity-only grading.
    spec_decision, spec_info = classify_from_report(report)
    if spec_decision == "needs_review":
        return "needs_review", extract_score_card(report), [
            f"[review] incomplete_scans={spec_info}"], None
    if spec_decision == "reject" and str(spec_info).endswith("_high"):
        # Validator-aware high already decided; keep detailed reasons below.
        pass
    decision, reasons = classify(report)
    score_card = extract_score_card(report)
    redactions = None

    # Redact-once-and-retry for hard_fail: replace PII and re-run Tier 1.
    if decision == "hard_fail":
        pii = collect_pii_values(report)
        if pii:
            redactions = redact_skill_dir(skill_dir, pii)
            report2 = run_tier1(skill_dir, work_dir)
            decision2, reasons2 = classify(report2)
            # If the post-redaction report passes soft- or hard-only-via-non-PII,
            # we still call it hard_fail (PII was the proximate cause; if it
            # re-appears via other content we want to know).
            if decision2 != "hard_fail":
                decision = "redacted_then_promote"
                reasons = reasons2
                score_card = extract_score_card(report2)
    return decision, score_card, reasons, redactions


def write_jsonl(jsonl_f, target_name: str, lineage: dict, mirrorable: bool):
    row = {
        "skill_id": target_name,
        "l1_path": lineage["source_l1_path"],
        "l2_path": lineage["l2_path"],
        "decision": lineage["decision"],
        "domain": lineage.get("source_repo"),  # filled later via meta
        "topic": None,
        "source_repo": lineage["source_repo"],
        "source_url": lineage["source_url"],
        "source_commit": lineage["source_commit"],
        "crawled_at": lineage["crawled_at"],
        "cleaned_at": lineage["cleaned_at"],
        "filter_passed": lineage["filter_passed"],
        "filter_hard_failed": lineage["filter_hard_failed"],
        "redactions": lineage["redactions"],
        "score_card": lineage["score_card"],
        "mirrorable": mirrorable,
    }
    jsonl_f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-skills-per-repo", type=int, default=10)
    ap.add_argument("--skip-repo-gt", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only-topic", type=str, default=None)
    args = ap.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    L2_DIR.mkdir(parents=True, exist_ok=True)
    L2_QUARANTINE.mkdir(parents=True, exist_ok=True)
    TMP_REPORTS.mkdir(parents=True, exist_ok=True)

    topics = find_topics()
    if args.only_topic:
        topics = [t for t in topics if t.name == args.only_topic]
        if not topics:
            log(f"ERROR: topic {args.only_topic} not found")
            return 2

    summary = {
        "total": 0, "pass": 0, "soft_warn": 0,
        "hard_fail": 0, "redacted_promote": 0, "skipped": 0,
        "needs_review": 0,
    }

    # Fresh JSONL on each non-dry-run start
    if not args.dry_run and L2_JSONL.exists():
        L2_JSONL.unlink()
    if not args.dry_run and L2_REJECTED.exists():
        L2_REJECTED.unlink()

    jsonl_f = L2_JSONL.open("a")
    rejected_f = L2_REJECTED.open("a")

    # Spec mapping: internal -> L1→L2 rigorous spec (pass/warn/reject)
    SPEC_MAP = {"pass": "pass", "soft_warn": "warn",
                "redacted_then_promote": "warn", "hard_fail": "reject",
                "needs_review": "needs_review"}

    for topic in topics:
        log(f"=== topic: {topic.name} ===")
        repos = find_repos(topic)
        for repo in repos:
            with (repo / "metadata.json").open() as f:
                meta = json.load(f)
            skills = find_skills(repo)
            if not skills:
                summary["skipped"] += 1
                log(f"  skip {meta['source_repo']}: no SKILL.md")
                continue
            if len(skills) > args.skip_repo_gt:
                summary["skipped"] += 1
                log(f"  skip {meta['source_repo']}: {len(skills)} skills "
                    f"> {args.skip_repo_gt}")
                continue

            selected = skills[:args.max_skills_per_repo]
            repo_slug = repo.name
            topic_clean = topic.name

            for skill_dir in selected:
                target_name = f"{repo_slug}__{skill_dir.name}"
                target_dir = L2_DIR / topic_clean / target_name

                if (target_dir / "_lineage.json").exists():
                    log(f"  skip {target_name}: already in L2")
                    continue

                summary["total"] += 1
                t0 = time.time()
                try:
                    decision, score_card, reasons, redactions = process_skill(
                        skill_dir, meta, target_dir, topic_clean
                    )
                except Exception as e:
                    log(f"  ! {target_name}: tier1 crashed — {e}")
                    summary["hard_fail"] += 1
                    continue

                dt = time.time() - t0
                qs = score_card.get("quality") or {}
                log(f"  {target_name:60s} -> {decision:18s} "
                    f"({dt:.1f}s, {qs.get('overall') or '-'} "
                    f"/ {qs.get('grade') or '-'})")

                # Tally
                if decision == "needs_review":
                    summary["needs_review"] += 1
                elif decision == "hard_fail":
                    summary["hard_fail"] += 1
                elif decision == "redacted_then_promote":
                    summary["redacted_promote"] += 1
                else:
                    summary[decision] += 1

                if decision == "needs_review":
                    # Spec: incomplete -> neither pass nor reject.
                    # Park in quarantine for manual review, audit only.
                    q_dir = L2_QUARANTINE / topic_clean / target_name
                    lineage = build_lineage(skill_dir, meta, "needs_review",
                                            reasons, score_card, q_dir,
                                            redactions)
                    write_jsonl(rejected_f, target_name, lineage,
                                mirrorable=False)
                    if not args.dry_run:
                        copy_skill(skill_dir, q_dir)
                        with (q_dir / "_lineage.json").open("w") as f:
                            json.dump(lineage, f, indent=2,
                                      ensure_ascii=False)
                    continue

                if decision == "hard_fail":
                    # Spec: reject -> L2_quarantine/ + L2_rejected.jsonl
                    spec_decision = "reject"
                    q_dir = L2_QUARANTINE / topic_clean / target_name
                    lineage = build_lineage(skill_dir, meta, spec_decision,
                                            reasons, score_card, q_dir,
                                            redactions)
                    write_jsonl(jsonl_f, target_name, lineage,
                                mirrorable=False)
                    write_jsonl(rejected_f, target_name, lineage,
                                mirrorable=False)
                    if not args.dry_run:
                        copy_skill(skill_dir, q_dir)
                        with (q_dir / "_lineage.json").open("w") as f:
                            json.dump(lineage, f, indent=2,
                                      ensure_ascii=False)
                    continue

                # Spec: pass / warn -> L2_cleaned/ (+warning label in lineage)
                spec_decision = SPEC_MAP.get(decision, decision)
                if not args.dry_run:
                    copy_skill(skill_dir, target_dir)
                    lineage = build_lineage(skill_dir, meta, spec_decision,
                                            reasons, score_card, target_dir,
                                            redactions)
                    with (target_dir / "_lineage.json").open("w") as f:
                        json.dump(lineage, f, indent=2, ensure_ascii=False)
                    write_jsonl(jsonl_f, target_name, lineage,
                                mirrorable=True)

    jsonl_f.close()
    rejected_f.close()
    log(f"=== summary: {summary} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())