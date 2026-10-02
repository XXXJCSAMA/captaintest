#!/usr/bin/env python3
"""Offline classify + land: read latest tier1_results_*.jsonl, apply
l2_clean.classify_from_report (+PII redact retry), land to
L2_cleaned/ or L2_quarantine/ with _lineage.json, L2_cleaned.jsonl,
L2_rejected.jsonl."""
from __future__ import annotations

import glob
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from l2_clean import (  # noqa: E402
    L1_DIR, L2_DIR, L2_JSONL, L2_QUARANTINE, L2_REJECTED,
    build_lineage, classify, collect_pii_values,
    copy_skill, extract_score_card, classify_from_report,
    redact_skill_dir,
)

SPEC_MAP = {"pass": "pass", "soft_warn": "warn",
            "redacted_then_promote": "warn", "hard_fail": "reject",
            "needs_review": "needs_review"}

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    cands = sorted(glob.glob(str(ROOT / "data" / "L2_evaluations" / "tier1_results_*.jsonl")))
    if not cands:
        print("no tier1_results found")
        return
    src = Path(cands[-1])
    rows = [json.loads(l) for l in open(src) if l.strip()]
    print(f"Input: {src} ({len(rows)} rows)")

    L2_DIR.mkdir(parents=True, exist_ok=True)
    L2_QUARANTINE.mkdir(parents=True, exist_ok=True)
    if L2_JSONL.exists():
        L2_JSONL.unlink()
    if L2_REJECTED.exists():
        L2_REJECTED.unlink()

    # Clear stale dirs: topics present in this batch get rebuilt from scratch.
    topics = {str(Path(r["skill_dir"]).relative_to(L1_DIR).parts[0])
              for r in rows if r.get("status") == "ok"}
    for t in topics:
        for base in (L2_DIR / t, L2_QUARANTINE / t):
            if base.exists():
                shutil.rmtree(base)

    stats: dict[str, int] = {}
    with open(L2_JSONL, "w") as jf, open(L2_REJECTED, "w") as rf:
        for r in rows:
            if r.get("status") != "ok":
                stats["no_report"] = stats.get("no_report", 0) + 1
                rf.write(json.dumps({"skill_dir": r.get("skill_dir"),
                                     "decision": "needs_review",
                                     "reason": r.get("status")}) + "\n")
                continue
            report = r["report"]
            skill_dir = Path(r["skill_dir"])
            rel = skill_dir.relative_to(L1_DIR)
            topic, repo = rel.parts[0], rel.parts[1]
            target_name = f"{repo}__{skill_dir.name}"

            # Spec gate.
            spec_decision, _ = classify_from_report(report)
            decision, reasons = classify(report)
            score = extract_score_card(report)
            redactions = None
            if decision == "hard_fail":
                pii = collect_pii_values(report)
                if pii:
                    redactions = redact_skill_dir(skill_dir, pii)
            # skillspector-only incomplete degrades to warn; keep detailed
            # reasons from classify for the warning label.
            final = SPEC_MAP.get(decision, decision)
            if spec_decision == "needs_review" and decision != "hard_fail":
                final = "needs_review"
            elif spec_decision == "warn" and final == "pass":
                final = "warn"
                reasons = ["[warn] skillspector_llm_degraded"]

            meta, meta_p = {}, None
            for parent in skill_dir.parents:
                cand = parent / "metadata.json"
                if cand.exists():
                    meta_p = cand
                    break
            if meta_p:
                meta = json.loads(meta_p.read_text())

            stats[final] = stats.get(final, 0) + 1
            if final in ("reject", "needs_review"):
                q = L2_QUARANTINE / topic / target_name
                lin = build_lineage(skill_dir, meta, final, reasons, score, q, redactions)
                copy_skill(skill_dir, q)
                (q / "_lineage.json").write_text(json.dumps(lin, indent=2, ensure_ascii=False))
                row = json.dumps({"skill_id": target_name, **lin}, ensure_ascii=False)
                jf.write(row + "\n")
                rf.write(row + "\n")
            else:
                t = L2_DIR / topic / target_name
                lin = build_lineage(skill_dir, meta, final, reasons, score, t, redactions)
                copy_skill(skill_dir, t)
                (t / "_lineage.json").write_text(json.dumps(lin, indent=2, ensure_ascii=False))
                jf.write(json.dumps({"skill_id": target_name, **lin}, ensure_ascii=False) + "\n")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()
