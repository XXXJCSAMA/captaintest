#!/usr/bin/env python3
"""Skill Shop API：把 skill_files.jsonl 暴露成 HTTP API。"""

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 导入挂载函数
import sys
sys.path.insert(0, "/home/lab/captaintest/skill_pipeline")
import filter.mount_skill as _mount_mod
from filter.mount_skill import add_to_captain

# mount_skill.py 内部用的是相对路径 data/...，从后端进程导入时 cwd 不对，
# 这里把它补成绝对路径，避免 FileNotFoundError。
_mount_mod.CATALOG = Path("/home/lab/captaintest/skill_pipeline/data/catalog/skill_files.jsonl")
_mount_mod.WORKSPACE_ROOT = Path("/home/lab/captaintest/skill_pipeline/data/agent_workspaces")

app = FastAPI(title="Skill Shop API")

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOG = Path("/home/lab/captaintest/skill_pipeline/data/catalog/skill_files.jsonl")


def load_skills():
    """读所有 Skill 的元数据（不含 files[]）。"""
    skills = []
    with open(CATALOG) as f:
        for line in f:
            r = json.loads(line)
            skills.append({
                "skill_id": r["skill_id"],
                "topic": r["topic"],
                "source_repo": r["source_repo"],
                "source_url": r["source_url"],
                "source_author": r["source_author"],
                "score_card": r.get("score_card"),
                "decision": r["decision"],
                "file_count": len(r["files"]),
            })
    return skills


def load_skill(skill_id: str):
    """读单个 Skill 的完整数据。"""
    with open(CATALOG) as f:
        for line in f:
            r = json.loads(line)
            if r["skill_id"] == skill_id:
                return r
    return None


@app.get("/api/skills")
def list_skills():
    return load_skills()


@app.get("/api/skills/{skill_id}")
def get_skill(skill_id: str):
    skill = load_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.post("/api/skills/{skill_id}/add-to-captain")
def add_skill_to_captain(skill_id: str, group_chat_id: str):
    result = add_to_captain(skill_id, group_chat_id)
    if result["status"] != "ok":
        raise HTTPException(status_code=404, detail=result["msg"])
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
