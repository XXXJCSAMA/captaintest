"""Captain marketplace backend: dynamic skill list + add-to-captain."""
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE = Path(__file__).resolve().parent
FRONTEND = BASE.parent / "Quest-Space-Marketplace" / "MVP Frontend"
EQUIP_MAP = FRONTEND / "assets" / "equipment-map.json"
CATALOG = BASE.parent / "skill_pipeline" / "data" / "catalog" / "skill_files.jsonl"

app = FastAPI(title="Captain Marketplace API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# group_chat_id -> list[skill_id]
captains: dict[str, list[str]] = {}


def load_equipment():
    try:
        return json.loads(EQUIP_MAP.read_text(encoding="utf-8"))
    except Exception:
        return {"animals": {}}


def load_catalog_meta():
    meta: dict[str, dict] = {}
    try:
        for line in CATALOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            sid = obj.get("skill_id")
            if sid:
                meta[sid] = obj
    except FileNotFoundError:
        pass
    return meta


class AddResult(BaseModel):
    ok: bool
    skill_id: str
    group_chat_id: str
    captain_skills: list[str]


@app.get("/api/skills")
def list_skills():
    """Dynamic equipment list. Merges local equipment-map.json with skill catalog."""
    equip = load_equipment()
    meta = load_catalog_meta()
    animals = equip.get("animals", {})
    slots = ["model", "skills", "permissions", "role"]
    items = []
    catalog_ids = list(meta.keys())
    n = 0
    for animal, conf in animals.items():
        base = conf.get("base", f"animals/{animal}.png")
        for slot in slots:
            e = conf.get(slot)
            if not e:
                continue
            skill_id = f"{animal}__{slot}"
            m = meta.get(skill_id) or (meta.get(catalog_ids[n % len(catalog_ids)]) if catalog_ids else {})
            n += 1
            items.append({
                "skill_id": skill_id,
                "name": e.get("name", skill_id),
                "slot": slot,
                "animal": animal,
                "src": f"assets/{e.get('src', '')}",
                "base": f"assets/{base}",
                "anchor": e.get("anchor"),
                "x": e.get("x"), "y": e.get("y"),
                "width": e.get("width"),
                "rotationDeg": e.get("rotationDeg", 0),
                "zIndex": e.get("zIndex", 10),
                "repo": m.get("source_repo"),
                "source_url": m.get("source_url"),
                "topic": m.get("topic"),
            })
    return {"skills": items, "count": len(items)}


@app.post("/api/skills/{skill_id}/add-to-captain", response_model=AddResult)
def add_to_captain(skill_id: str, group_chat_id: str = Query(...)):
    if not group_chat_id:
        raise HTTPException(400, "group_chat_id required")
    valid = {f"{a}__{s}" for a in load_equipment().get("animals", {}) for s in ("model", "skills", "permissions", "role")}
    catalog_ids = set(load_catalog_meta().keys())
    if skill_id not in valid and skill_id not in catalog_ids:
        raise HTTPException(404, f"unknown skill_id: {skill_id}")
    lst = captains.setdefault(group_chat_id, [])
    if skill_id not in lst:
        lst.append(skill_id)
    return AddResult(ok=True, skill_id=skill_id, group_chat_id=group_chat_id, captain_skills=list(lst))


@app.get("/api/captain")
def get_captain(group_chat_id: str = Query(...)):
    return {"group_chat_id": group_chat_id, "skills": captains.get(group_chat_id, [])}
