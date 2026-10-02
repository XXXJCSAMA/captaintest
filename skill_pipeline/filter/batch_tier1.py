#!/usr/bin/env python3
"""
Batch run SkillEvaluator Tier 1, parallel over every SKILL.md under L1_raw.
Each skill is the full directory containing SKILL.md (+scripts/, resources/).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
L1_ROOT = ROOT / "data" / "L1_raw"
OUTPUT_DIR = ROOT / "data" / "L2_evaluations"

# Skip marketplace-style repos (30+ skills each, noisy / duplicate).
SKIP_REPOS = [
    "jeremylongshore_tons_of_skills_marketplace",
    "ericosiu_ai_marketing_skills",
    "productfculty",
    "shawnpang_startup_founder_skills",
]


def run_one(skill_dir_str: str) -> dict:
    skill_dir = Path(skill_dir_str)
    work_dir = Path(tempfile.mkdtemp(prefix="skilleval_"))

    # Explicit PATH so skillspector and gitleaks are found in workers.
    env = os.environ.copy()
    candidates = [
        "/home/lab/captaintest/skill_pipeline/.venv312/bin",
        "/home/lab/.local/bin",
    ]
    for extra in candidates:
        if extra not in env.get("PATH", ""):
            env["PATH"] = f"{extra}:{env.get('PATH', '')}"
    for tool in ("skillspector", "gitleaks"):
        if not shutil.which(tool, path=env["PATH"]):
            found = shutil.which(tool)
            if found:
                env["PATH"] = f"{Path(found).parent}:{env['PATH']}"

    cmd = [
        "skillevaluator", "tier1", str(skill_dir),
        "--no-llm", "-r", "json", "-o", str(work_dir),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=300, env=env)
    except subprocess.TimeoutExpired:
        return {"skill_dir": str(skill_dir), "status": "timeout"}

    report_path = work_dir / "skillevaluator-tier1.json"
    if report_path.exists():
        report = json.loads(report_path.read_text())
        return {
            "skill_dir": str(skill_dir),
            "status": "ok",
            "report": report,
            "returncode": result.returncode,
        }
    return {
        "skill_dir": str(skill_dir),
        "status": "no_report",
        "stderr": result.stderr[:500],
        "returncode": result.returncode,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="only run one topic")
    parser.add_argument("--all", action="store_true", help="run all topics")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if args.all:
        topic_dirs = [d for d in L1_ROOT.iterdir() if d.is_dir()]
    elif args.topic:
        topic_dirs = [L1_ROOT / args.topic]
    else:
        print("Must specify --topic or --all")
        return

    # Find all SKILL.md (case-sensitive; evaluator expects SKILL.md),
    # dedupe by parent dir, skip marketplace repos.
    skill_dirs_set: set[Path] = set()
    for topic_dir in topic_dirs:
        for skill_md in topic_dir.rglob("SKILL.md"):
            skill_dir = skill_md.parent
            if any(skip in str(skill_dir) for skip in SKIP_REPOS):
                continue
            skill_dirs_set.add(skill_dir)

    skill_dirs = sorted(skill_dirs_set)
    if args.limit:
        skill_dirs = skill_dirs[:args.limit]

    print(f"Found {len(skill_dirs)} skills, using {args.workers} workers")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_one, str(sd)): sd for sd in skill_dirs}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            print(f"[{i}/{len(skill_dirs)}] {result['skill_dir']} -> {result['status']}",
                  flush=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_file = OUTPUT_DIR / f"tier1_results_{timestamp}.jsonl"
    with open(out_file, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nResults written to {out_file}")
    stats: dict[str, int] = {}
    for r in results:
        stats[r["status"]] = stats.get(r["status"], 0) + 1
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()
