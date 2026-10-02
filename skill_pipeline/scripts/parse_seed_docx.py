#!/usr/bin/env python3
"""
Parse Domain.docx into a structured JSON topic list.

Output: seeds/domain_topics.json
Schema:
{
  "source": "Domain.docx",
  "parsed_at": "<ISO timestamp>",
  "total_topics": <int>,
  "topics": [
    {
      "priority": "P0" | "P1" | "P2" | null,
      "domain": "<Sales/RevOps/...>",
      "quantity": <int>,
      "topics": ["ICP Definition", "Account Research", ...]
    },
    ...
  ]
}
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from docx import Document


SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds"
INPUT_DOCX = SEEDS_DIR / "Domain.docx"
OUTPUT_JSON = SEEDS_DIR / "domain_topics.json"


def parse_docx(path: Path) -> list[dict]:
    doc = Document(str(path))
    tables = doc.tables
    if len(tables) < 2:
        print(f"[warn] expected at least 2 tables, found {len(tables)}", file=sys.stderr)

    # Table 1 (index 1): the prioritized list with # Skills and Family
    priority_table = tables[1]
    rows = list(priority_table.rows)

    out: list[dict] = []
    for row in rows[1:]:  # skip header
        cells = [c.text.strip() for c in row.cells]
        priority, domain, quantity_raw, *scenario_cells = cells
        if not domain and not quantity_raw:
            continue
        if domain.upper().startswith("TOTAL"):
            continue

        # scenarios come as one big comma-separated string in the last cell
        scenarios_raw = " ".join(scenario_cells).strip()
        scenarios = [s.strip() for s in scenarios_raw.split(",") if s.strip()]

        try:
            quantity = int(quantity_raw.replace(",", "")) if quantity_raw else 0
        except ValueError:
            quantity = 0

        out.append(
            {
                "priority": priority or None,
                "domain": domain,
                "quantity": quantity,
                "topics": scenarios,
            }
        )

    return out


def main() -> int:
    if not INPUT_DOCX.exists():
        print(f"[error] missing {INPUT_DOCX}", file=sys.stderr)
        return 1

    topics = parse_docx(INPUT_DOCX)
    total = sum(len(t["topics"]) for t in topics)

    payload = {
        "source": INPUT_DOCX.name,
        "parsed_at": datetime.now(timezone.utc).isoformat(),
        "total_domains": len(topics),
        "total_topics": total,
        "topics": topics,
    }

    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"[ok] wrote {OUTPUT_JSON}")
    print(f"[ok] {len(topics)} domains, {total} topics")
    return 0


if __name__ == "__main__":
    sys.exit(main())