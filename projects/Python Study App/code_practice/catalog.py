from __future__ import annotations

from collections.abc import Iterator, Mapping
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from typing import Any, Literal

from pydantic import BaseModel

from .database import approved_variant_rows
from .schemas import ProblemDefinition


CATALOG_DIR = Path(os.environ.get("CODE_PRACTICE_CATALOG_DIR", Path(__file__).resolve().parent.parent / "catalog_data"))


class CatalogEntry(BaseModel):
    id: str
    version: int
    status: str = "approved"
    title: str
    summary: str
    topics: list[str]
    prerequisites: list[str]
    difficulty: int
    estimated_minutes: int
    path: str | None = None
    content_sha256: str | None = None
    source_id: int | None = None


class Catalog(Mapping[str, ProblemDefinition]):
    """Small searchable metadata index plus bounded, on-demand detail loading."""
    def __init__(self, directory: Path, variants: list[dict]):
        self.directory = directory.resolve()
        manifest = json.loads((directory / "manifest.json").read_text())
        self.metadata = {entry["id"]: CatalogEntry.model_validate(entry) for entry in manifest["entries"]
                         if entry["status"] == "approved"}
        self.variants = {}
        for row in variants:
            problem = ProblemDefinition.model_validate(row)
            if problem.status != "approved":
                continue
            if problem.id in self.metadata:
                raise ValueError(f"Variant ID collides with the shipped catalog: {problem.id}")
            self.variants[problem.id] = problem
            self.metadata[problem.id] = CatalogEntry(**problem.model_dump(), difficulty=problem.difficulty)
        self.index = sqlite3.connect(":memory:", check_same_thread=False)
        self.index.execute("CREATE TABLE entries(id TEXT PRIMARY KEY, difficulty INTEGER, title TEXT, search_text TEXT)")
        self.index.execute("CREATE TABLE topics(problem_id TEXT, topic TEXT, PRIMARY KEY(topic, problem_id))")
        self.index.executemany("INSERT INTO entries VALUES(?,?,?,?)", [
            (p.id, p.difficulty, p.title, f"{p.title} {p.summary} {' '.join(p.topics)}".casefold())
            for p in self.metadata.values()])
        self.index.executemany("INSERT INTO topics VALUES(?,?)", [
            (p.id, topic) for p in self.metadata.values() for topic in set(p.topics)])
        self.index.execute("CREATE INDEX entries_order ON entries(difficulty, title, id)")
        self.index.commit()
        self._load = lru_cache(maxsize=32)(self._load_detail)

    def __len__(self) -> int:
        return len(self.metadata)

    def __iter__(self) -> Iterator[str]:
        return iter(self.metadata)

    def __contains__(self, key: object) -> bool:
        return key in self.metadata

    def __getitem__(self, key: str) -> ProblemDefinition:
        if key in self.variants:
            return self.variants[key]
        return self._load(key)

    def _load_detail(self, key: str) -> ProblemDefinition:
        entry = self.metadata[key]
        path = (self.directory / entry.path).resolve()
        if not path.is_relative_to(self.directory):
            raise ValueError("Catalog detail path escapes its package")
        payload = json.loads(path.read_text())
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if digest != entry.content_sha256:
            raise ValueError(f"Catalog content hash mismatch: {key}; rebuild or restore the package")
        problem = ProblemDefinition.model_validate(payload)
        if problem.id != key or problem.status != "approved":
            raise ValueError(f"Invalid published problem: {key}")
        return problem

    def search(self, *, solved: set[str], search: str = "", topic: str | None = None,
               difficulty_min: int = 1, difficulty_max: int = 10,
               completion: Literal["all", "passed", "unsolved"] = "all",
               page: int = 1, page_size: int = 30) -> dict:
        clauses, params = ["difficulty BETWEEN ? AND ?"], [difficulty_min, difficulty_max]
        if search.strip():
            escaped = search.strip().casefold().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            clauses.append("search_text LIKE ? ESCAPE '\\'")
            params.append("%" + escaped + "%")
        if topic:
            clauses.append("id IN (SELECT problem_id FROM topics WHERE topic=?)")
            params.append(topic)
        if completion != "all":
            clauses.append("id " + ("IN" if completion == "passed" else "NOT IN") + " (SELECT value FROM json_each(?))")
            params.append(json.dumps(sorted(solved)))
        where = " AND ".join(clauses)
        total = self.index.execute("SELECT count(*) FROM entries WHERE " + where, params).fetchone()[0]
        ids = self.index.execute("SELECT id FROM entries WHERE " + where +
                                 " ORDER BY difficulty,title,id LIMIT ? OFFSET ?",
                                 [*params, page_size, (page - 1) * page_size]).fetchall()
        return {"items": [problem_summary(self.metadata[row[0]], solved) for row in ids],
                "total": total, "catalogTotal": len(self), "page": page, "pageSize": page_size,
                "topics": sorted({t for p in self.metadata.values() for t in p.topics})}


@lru_cache(maxsize=1)
def get_catalog() -> Catalog:
    return Catalog(CATALOG_DIR, approved_variant_rows())


def refresh_catalog() -> None:
    get_catalog.cache_clear()


def problem_summary(problem: ProblemDefinition | CatalogEntry, solved_ids: set[str] | None = None) -> dict[str, Any]:
    solved_ids = solved_ids or set()
    return {
        "id": problem.id,
        "version": problem.version,
        "title": problem.title,
        "summary": problem.summary,
        "topics": problem.topics,
        "prerequisites": problem.prerequisites,
        "difficulty": problem.difficulty,
        "estimatedMinutes": problem.estimated_minutes,
        "solved": problem.id in solved_ids,
    }


def public_problem(problem: ProblemDefinition) -> dict[str, Any]:
    payload = problem.model_dump(mode="json", exclude={"reference_solution", "brute_force_solution", "known_wrong_solutions", "tests", "hints", "editorial"})
    payload["difficulty"] = problem.difficulty
    payload["tests"] = [test.model_dump(mode="json") for test in problem.tests if test.visible]
    payload["hints"] = []
    payload["editorial"] = ""
    return payload
