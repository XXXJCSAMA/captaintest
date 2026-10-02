#!/usr/bin/env python3
"""
L1 Crawler — crawl Skill *directories* from GitHub.

Per spec (2026-10-02):
  For each (priority, domain, topic) in seeds/domain_topics.json:
    1. Build 5~10 queries (repos + code)
    2. Search /search/repositories and /search/code (filename:SKILL.md, AGENTS.md, ...)
    3. Merge + dedupe by repo full_name
    4. For each repo:
        a. negative_keywords hit -> skip
        b. fetch repo metadata (stars, license, author, updated_at)
        c. fetch tree (git/trees?recursive=1)
        d. whitelist: SKILL.md, manifest.json, LICENSE, README.md, scripts/**, resources/**, references/**
        e. download files to data/L1_raw/<topic_slug>/<repo_slug>/repo/...
        g. write JSONL record to data/L1_raw/<topic_slug>.jsonl

Output:
  data/L1_raw/<priority>__<domain_slug>__<topic_slug>.jsonl
  data/L1_raw/<priority>__<domain_slug>__<topic_slug>/<repo_slug>/metadata.json
  data/L1_raw/<priority>__<domain_slug>__<topic_slug>/<repo_slug>/repo/{whitelisted files}

Resume:
  data/L1_raw/.progress.json  -- set of completed topic keys
  --force  -> ignore progress

Important:
  Set env GITHUB_TOKEN. Anonymous = 60 req/h. Token = 5000 req/h.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.parse
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parent.parent
SEED_FILE = ROOT / "seeds" / "domain_topics.json"
L1_DIR = ROOT / "data" / "L1_raw"
PROGRESS_FILE = L1_DIR / ".progress.json"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

GITHUB_API = "https://api.github.com"

# ---------- negative keywords (description/topics check) ----------
NEGATIVE_KEYWORDS = {
    "programming", "developer", "coding", "code-editor", "ide",
    "compiler", "debugger", "kernel", "operating-system", "bootloader",
    "leetcode", "competitive-programming", "tutorial-code", "homework",
}

# ---------- whitelist of file basenames / dirs ----------
WHITELIST_BASENAMES = {
    "skill.md", "agents.md", "claude.md", ".cursorrules",
    "manifest.json", "license", "readme.md",
}
WHITELIST_DIRS = {"scripts", "resources", "references"}

# ---------- query filename variants for code search ----------
CODE_FILENAMES = ["SKILL.md", "AGENTS.md", "CLAUDE.md", ".cursorrules"]


# ---------------------------------------------------------------- session
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _build_session(token: str | None) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "skill-pipeline-l1-crawler/1.0",
    })
    if token:
        s.headers["Authorization"] = f"Bearer {token}"
    retry = Retry(
        total=4, backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10))
    return s


SESSION: requests.Session | None = None


def http_get_json(url: str, token: str | None) -> tuple[Any, dict]:
    global SESSION
    if SESSION is None:
        SESSION = _build_session(token)
    r = SESSION.get(url, timeout=30)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        body = (r.text or "")[:400]
        raise RuntimeError(f"HTTP {r.status_code}: {body}") from e
    return r.json(), dict(r.headers)


def rate_limit_sleep_if_needed(headers: dict, token: str | None) -> None:
    if not token:
        return
    try:
        remaining = int(headers.get("x-ratelimit-remaining", "9999"))
        reset = int(headers.get("x-ratelimit-reset", "0"))
    except (TypeError, ValueError):
        return
    if remaining < 5:
        wait = max(reset - int(time.time()), 5)
        logf.warn(f"rate-limit low ({remaining}); sleeping {wait}s")
        time.sleep(min(wait, 65))


# ---------------------------------------------------------------- slugs
def topic_slug(topic: str) -> str:
    s = topic.lower()
    s = s.replace(" → ", "_to_")
    s = s.replace(" ", "_")
    s = s.replace("/", "_")
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:80]


def domain_slug(domain: str) -> str:
    return topic_slug(domain)  # same slug recipe


def repo_slug(full_name: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", full_name.lower()).strip("_")[:80]


# ---------------------------------------------------------------- logging
class Logger:
    def __init__(self) -> None:
        log_path = LOG_DIR / f"l1_crawl_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.log"
        self.fh = open(log_path, "w")
        self.path = log_path

    def __call__(self, level: str, msg: str) -> None:
        line = f"[{now_iso()}] {msg}"
        self.fh.write(line + "\n"); self.fh.flush()
        print(line, flush=True)

    def info(self, msg: str) -> None: self("INFO", msg)
    def warn(self, msg: str) -> None: self("WARN", msg)
    def error(self, msg: str) -> None: self("ERR ", msg)

    def close(self) -> None:
        self.fh.close()


logf = Logger()


# ---------------------------------------------------------------- queries
def build_queries(topic: str, domain: str) -> list[str]:
    """5-10 queries mixing generic skill-search and topic-specific searches."""
    t = topic
    qs = [
        f'"{t}" skill',                           # very direct
        f'"{t}" cursor skill',                     # cursor-targeted
        f'"{t}" in:name,description,readme',       # name+desc match
        f'"{t}" topic:claude-code',
        f'"{t}" topic:openai-codex',
        f'"{t}" "SKILL.md"',
        f'"{t}" agent prompt',                     # generic agent searches
        f'"{t}" llm workflow',
    ]
    # deduplicate while preserving order
    seen, out = set(), []
    for q in qs:
        if q not in seen:
            seen.add(q); out.append(q)
    return out


def search_repositories(q: str, token: str | None) -> list[dict]:
    url = f"{GITHUB_API}/search/repositories?q={urllib.parse.quote(q)}&per_page=15&sort=stars"
    try:
        data, headers = http_get_json(url, token)
        rate_limit_sleep_if_needed(headers, token)
        return data.get("items", [])
    except RuntimeError as e:
        logf.warn(f"  repos search failed q={q!r}: {e}")
        return []


def search_code(q: str, token: str | None) -> list[dict]:
    url = f"{GITHUB_API}/search/code?q={urllib.parse.quote(q)}&per_page=10"
    try:
        data, headers = http_get_json(url, token)
        rate_limit_sleep_if_needed(headers, token)
        return data.get("items", [])
    except RuntimeError as e:
        logf.warn(f"  code search failed q={q!r}: {e}")
        return []


def code_queries_for_topic(topic: str) -> list[str]:
    return [f'"{topic}" filename:{fn}' for fn in CODE_FILENAMES]


# ---------------------------------------------------------------- filtering
def has_negative_keyword(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    return any(f" {k} " in f" {t} " or re.search(rf"\b{re.escape(k)}\b", t) for k in NEGATIVE_KEYWORDS)


def likely_irrelevant(repo: dict) -> bool:
    """Soft flag (do not drop)."""
    fields = " ".join([
        (repo.get("description") or ""),
        " ".join(repo.get("topics") or []),
        repo.get("name") or "",
    ])
    return has_negative_keyword(fields)


# ---------------------------------------------------------------- repo data
def fetch_repo(full_name: str, token: str | None) -> dict:
    url = f"{GITHUB_API}/repos/{full_name}"
    data, _ = http_get_json(url, token)
    return data


def fetch_default_branch_commit(full_name: str, token: str | None) -> tuple[str, str]:
    """return (sha, default_branch)"""
    repo = fetch_repo(full_name, token)
    return repo.get("default_branch", "main"), repo.get("default_branch", "main")  # branch resolved by API


def fetch_tree(full_name: str, branch: str, token: str | None) -> list[dict]:
    """Recursive tree; truncate=False means real recursive."""
    url = f"{GITHUB_API}/repos/{full_name}/git/trees/{branch}?recursive=1"
    data, _ = http_get_json(url, token)
    if data.get("truncated"):
        logf.warn(f"  tree truncated for {full_name}; some files may be missing")
    return data.get("tree", [])


def fetch_latest_sha(full_name: str, branch: str, token: str | None) -> str:
    url = f"{GITHUB_API}/repos/{full_name}/commits/{branch}"
    try:
        data, _ = http_get_json(url, token)
        return data.get("sha", "")
    except RuntimeError:
        return ""


def fetch_raw(full_name: str, sha: str, path: str, token: str | None) -> bytes:
    url = f"{GITHUB_API}/repos/{full_name}/contents/{urllib.parse.quote(path)}?ref={sha}"
    data, _ = http_get_json(url, token)
    if data.get("encoding") == "base64" and data.get("content"):
        return base64.b64decode(data["content"])
    return b""


# ---------------------------------------------------------------- whitelist + download
def is_whitelisted(path: str) -> bool:
    p = path.lower()
    base = os.path.basename(p)
    if base in WHITELIST_BASENAMES:
        return True
    # folder-prefix: scripts/foo.py, resources/foo.txt, references/bar.md
    parts = p.split("/")
    if len(parts) >= 2 and parts[0] in WHITELIST_DIRS:
        return True
    return False


# ---------------------------------------------------------------- output paths
def jsonl_path(priority: str, domain: str, topic: str) -> Path:
    return L1_DIR / f"{priority}__{topic_slug(domain)}__{topic_slug(topic)}.jsonl"


def topic_dir(priority: str, domain: str, topic: str) -> Path:
    return L1_DIR / f"{priority}__{topic_slug(domain)}__{topic_slug(topic)}"


# ---------------------------------------------------------------- progress
def load_progress() -> set[str]:
    if PROGRESS_FILE.exists():
        try:
            return set(json.loads(PROGRESS_FILE.read_text()))
        except Exception:
            return set()
    return set()


def save_progress(done: set[str]) -> None:
    L1_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(sorted(done), indent=2))


# ---------------------------------------------------------------- pipeline
def collect_repos_for_topic(topic: str, domain: str, priority: str, token: str | None) -> list[dict]:
    """Run all queries, dedupe by full_name, apply hard negative filter."""
    raw_hits: list[dict] = []

    # 1. repo search via 5~10 generic queries
    for q in build_queries(topic, domain):
        raw_hits.extend({"source": "repo", **r} for r in search_repositories(q, token))

    # 2. code search via filename variants
    for q in code_queries_for_topic(topic):
        items = search_code(q, token)
        for it in items:
            repo = it.get("repository", {}) or {}
            # promote code hits to a synthetic repo dict
            synth = {
                "full_name": repo.get("full_name"),
                "name": repo.get("name"),
                "description": repo.get("description"),
                "topics": repo.get("topics") or [],
                "stargazers_count": repo.get("stargazers_count"),
                "language": repo.get("language"),
                "html_url": repo.get("html_url"),
                "owner": repo.get("owner"),
                "license": repo.get("license"),
                "updated_at": repo.get("updated_at"),
                "default_branch": repo.get("default_branch"),
                "_code_path": it.get("path"),
            }
            raw_hits.append({"source": "code", **synth})
        time.sleep(0.3 if token else 1.5)

    # dedupe by full_name
    by_repo: dict[str, dict] = {}
    for h in raw_hits:
        fn = h.get("full_name")
        if not fn:
            continue
        if fn not in by_repo or h["source"] == "code":
            by_repo[fn] = h  # prefer code-source for richer path info

    # hard negative filter
    accepted: list[dict] = []
    for fn, hit in by_repo.items():
        text = " ".join(filter(None, [
            hit.get("description") or "",
            " ".join(hit.get("topics") or []),
            hit.get("name") or "",
        ]))
        if has_negative_keyword(text):
            logf.info(f"  [skip] negative-keyword: {fn}")
            continue
        accepted.append(hit)

    return accepted


def harvest_repo(full_name: str, priority: str, domain: str, topic: str, token: str | None) -> dict | None:
    """Fetch metadata + tree + whitelist files, write to disk."""
    try:
        repo = fetch_repo(full_name, token)
    except RuntimeError as e:
        logf.warn(f"  repo fetch failed {full_name}: {e}")
        return None

    branch = repo.get("default_branch") or "main"
    sha = fetch_latest_sha(full_name, branch, token) or branch

    try:
        tree = fetch_tree(full_name, branch, token)
    except RuntimeError as e:
        logf.warn(f"  tree fetch failed {full_name}: {e}")
        return None

    # whitelist filter
    files = sorted({t["path"] for t in tree if t.get("type") == "blob" and is_whitelisted(t["path"])})

    # layout per domain doc:
    #   <topic_dir>/<repo_slug>/metadata.json
    #   <topic_dir>/<repo_slug>/repo/<files>
    rd = topic_dir(priority, domain, topic) / repo_slug(full_name)
    (rd / "repo").mkdir(parents=True, exist_ok=True)

    saved_files: list[str] = []
    for path in files:
        try:
            content = fetch_raw(full_name, sha, path, token)
        except RuntimeError as e:
            logf.warn(f"    raw fetch failed {full_name}::{path}: {e}")
            continue
        dest = rd / "repo" / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        saved_files.append(path)
        time.sleep(0.05 if token else 0.5)

    record = {
        "candidate_id": str(uuid.uuid4()),
        "priority": priority,
        "domain": domain,
        "topic": topic,
        "topic_slug": topic_slug(topic),
        "source_repo": full_name,
        "source_author": (repo.get("owner") or {}).get("login"),
        "source_commit": sha,
        "source_url": repo.get("html_url"),
        "crawled_at": now_iso(),
        "stars": repo.get("stargazers_count"),
        "license_raw": ((repo.get("license") or {}).get("spdx_id")) or None,
        "description": repo.get("description"),
        "topics": repo.get("topics") or [],
        "language": repo.get("language"),
        "updated_at": repo.get("updated_at"),
        "default_branch": branch,
        "raw_path": str((rd / "repo").relative_to(ROOT)),
        "files": saved_files,
        "likely_irrelevant": likely_irrelevant(repo),
    }

    # metadata.json in the topic_dir/repo_slug/ root
    (rd / "metadata.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))
    return record


# ---------------------------------------------------------------- main
def iter_topics(seed: dict) -> Iterable[tuple[str, str, str]]:
    for d in seed["topics"]:
        for t in d["topics"]:
            yield d["priority"] or "P?", d["domain"], t


def topic_key(priority: str, domain: str, topic: str) -> str:
    return f"{priority}|{domain}|{topic}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-topics", type=int, default=0, help="0 = all")
    ap.add_argument("--max-skills", type=int, default=100,
                    help="stop once we've harvested this many skills (default 100)")
    ap.add_argument("--only-priority", choices=["P0", "P1", "P2"], default=None)
    ap.add_argument("--force", action="store_true", help="ignore .progress.json")
    ap.add_argument("--dry-run", action="store_true", help="don't download files / write outputs")
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token and not args.dry_run:
        logf.warn("GITHUB_TOKEN not set; running with anonymous rate limit (60 req/h)")
    if not token:
        token = None

    seed = json.loads(SEED_FILE.read_text())
    L1_DIR.mkdir(parents=True, exist_ok=True)
    done = set() if args.force else load_progress()

    total_harvested = 0
    topic_idx = 0
    for priority, domain, topic in iter_topics(seed):
        if args.only_priority and priority != args.only_priority:
            continue
        key = topic_key(priority, domain, topic)
        if key in done:
            continue
        topic_idx += 1
        if args.max_topics and topic_idx > args.max_topics:
            break
        if total_harvested >= args.max_skills:
            logf.info(f"[stop] reached --max-skills={args.max_skills}")
            break

        logf.info(f"[{topic_idx}] ({priority}) {domain} :: {topic}")
        repos = collect_repos_for_topic(topic, domain, priority, token)
        logf.info(f"    candidates={len(repos)}")

        jl = jsonl_path(priority, domain, topic)
        appended = 0
        for ci, hit in enumerate(repos, 1):
            if total_harvested >= args.max_skills:
                break
            full_name = hit["full_name"]
            stars = hit.get("stargazers_count", 0)
            logf.info(f"    [{ci}/{len(repos)}] {full_name} ({stars}*)")
            if args.dry_run:
                total_harvested += 1
                appended += 1
                continue
            rec = harvest_repo(full_name, priority, domain, topic, token)
            if not rec:
                continue
            with jl.open("a") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total_harvested += 1
            appended += 1
            time.sleep(0.2 if token else 1.2)

        logf.info(f"    saved={appended} → {jl.name}")
        done.add(key)
        save_progress(done)

    logf.info(f"[done] topics={topic_idx} harvested={total_harvested}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        logf.close()