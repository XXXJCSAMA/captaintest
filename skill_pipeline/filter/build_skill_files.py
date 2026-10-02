#!/usr/bin/env python3
"""Split L2_cleaned skill dirs into file trees, output JSONL for storefront."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
L2_ROOT = ROOT / "data" / "L2_cleaned"
OUTPUT = ROOT / "data" / "catalog" / "skill_files.jsonl"

SKIP = {"_lineage.json"}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

records: list[dict] = []

for lineage_path in sorted(L2_ROOT.rglob("_lineage.json")):
    skill_dir = lineage_path.parent
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))

    files = []
    for f in sorted(skill_dir.rglob("*")):
        if not f.is_file() or f.name in SKIP:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = ""
        files.append({
            "file_path": str(f.relative_to(skill_dir)),
            "file_content": content,
        })

    records.append({
        "skill_id": skill_dir.name,
        "topic": skill_dir.parent.name,
        "source_repo": lineage.get("source_repo"),
        "source_url": lineage.get("source_url"),
        "source_author": lineage.get("source_author"),
        "source_commit": lineage.get("source_commit"),
        "crawled_at": lineage.get("crawled_at"),
        "decision": lineage.get("decision"),
        "score_card": lineage.get("score_card"),
        "filter_passed": lineage.get("filter_passed"),
        "filter_hard_failed": lineage.get("filter_hard_failed"),
        "files": files,
    })
    print(f"[{len(records)}] {skill_dir.name} ({len(files)} files)")

with open(OUTPUT, "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"\nWrote {len(records)} skills to {OUTPUT}")
