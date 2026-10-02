#!/usr/bin/env python3
"""Mount a skill file-tree from the catalog into a group-chat workspace."""
import json
import sys
from pathlib import Path

CATALOG = Path("data/catalog/skill_files.jsonl")
WORKSPACE_ROOT = Path("data/agent_workspaces")


def add_to_captain(skill_id: str, group_chat_id: str) -> dict:
    """Mount the skill's file tree into the group chat's agent directory."""
    skill = None
    with open(CATALOG) as f:
        for line in f:
            r = json.loads(line)
            if r["skill_id"] == skill_id:
                skill = r
                break

    if not skill:
        return {"status": "error", "msg": f"Skill {skill_id} not found"}

    workspace = WORKSPACE_ROOT / group_chat_id / skill_id
    workspace.mkdir(parents=True, exist_ok=True)

    mounted = 0
    for f_obj in skill["files"]:
        target = workspace / f_obj["file_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f_obj["file_content"], encoding="utf-8")
        mounted += 1

    return {
        "status": "ok",
        "skill_id": skill_id,
        "group_chat_id": group_chat_id,
        "mounted_files": mounted,
        "workspace": str(workspace),
    }


if __name__ == "__main__":
    result = add_to_captain(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2, ensure_ascii=False))
