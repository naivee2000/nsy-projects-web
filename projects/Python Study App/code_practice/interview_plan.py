"""Build a gradual path through published interview targets using metadata only."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import hashlib

from .learning import attempt_score, choose_daily_session, normalized_topics
from .study_lists import study_list_badges, study_list_options, study_list_snapshot


@dataclass(frozen=True)
class Foundation:
    topic: str
    minimum: int
    maximum: int


def _normalize(topic: str) -> str:
    return "-".join(topic.lower().replace("_", " ").split())


def _focus(topics: set[str]) -> set[str]:
    # Common container tags alone should not unlock a new algorithm such as intervals.
    return topics - {"arrays", "strings", "math"} or topics


class InterviewPlan:
    def __init__(self, catalog, attempts, reviews, now: datetime, day: str):
        self.catalog = catalog
        self.day = day
        self.solved = {a.problem_id for a in attempts if a.result == "accepted"}
        self.targets = {key for key in catalog if study_list_badges(key)}
        self.remaining = self.targets - self.solved
        self.topics = {p.id: normalized_topics(p) for p in catalog.values()}
        self.by_topic = defaultdict(list)
        for problem in catalog.values():
            for topic in self.topics[problem.id]:
                self.by_topic[topic].append(problem)
        for problems in self.by_topic.values():
            problems.sort(key=lambda p: (p.difficulty, p.id))

        recent = defaultdict(list)
        self.history = defaultdict(list)
        for attempt in sorted(attempts, key=lambda a: a.created_at, reverse=True):
            self.history[attempt.problem_id].append(attempt)
            for topic in self.topics.get(attempt.problem_id, set()):
                if len(recent[topic]) < 10:
                    recent[topic].append(attempt_score(attempt))
        self.mastery = {topic: 100 * sum(scores) / len(scores) for topic, scores in recent.items()}
        self.passed_easy_topics = {
            topic for key in self.solved if key in catalog and catalog[key].difficulty <= 3
            for topic in self.topics[key]
        }
        self.easy_topics = {topic for topic, pool in self.by_topic.items() if any(p.difficulty <= 3 for p in pool)}
        self._blockers = {}
        self.ready_targets = {key for key in self.remaining if not self.blockers(catalog[key])}
        self.preparation_for: dict[str, str] = {}

        # Trace unmet foundations down to an available exercise. Recursion is
        # bounded by visited problem IDs; prerequisites cannot produce a loop.
        for key in sorted(self.remaining, key=lambda key: (catalog[key].difficulty, key)):
            self._prepare(catalog[key], key, set())

        eligible = self.ready_targets | set(self.preparation_for)
        due = {r.problem_id for r in reviews if r.due_at <= now}
        used_topics = defaultdict(int)
        self.ordered = []
        while eligible:
            def rank(key):
                problem = catalog[key]
                stage = 0 if problem.difficulty <= 3 else 1 if problem.difficulty <= 5 else 2 if problem.difficulty <= 7 else 3
                tie = hashlib.sha256(f"{day}:{key}".encode()).hexdigest()
                return (stage, key not in due, key not in self.targets,
                        sum(used_topics[t] for t in _focus(self.topics[key])), problem.difficulty, tie)
            key = min(eligible, key=rank)
            self.ordered.append(catalog[key])
            eligible.remove(key)
            for topic in _focus(self.topics[key]):
                used_topics[topic] += 1

    def daily_session(self):
        """Reserve two of five credits for progressive DP, then interview work."""
        dp_ids = {key for key, topics in self.topics.items()
                  if any(t == "dp" or t == "dynamic-programming"
                         or t.endswith("-dynamic-programming") or t.endswith("-dp") for t in topics)}
        if not dp_ids:
            return self._within_daily_budget(self._standard_session())
        dp_history = sorted((a for key in dp_ids for a in self.history.get(key, [])),
                            key=lambda a: a.created_at, reverse=True)[:10]
        mastery = 100 * sum(attempt_score(a) for a in dp_history) / len(dp_history) if dp_history else 0
        passed_easy = sum(key in self.solved and self.catalog[key].difficulty <= 3 for key in dp_ids)
        medium_ready = passed_easy >= 2 and mastery >= 70
        eligible = [self.catalog[key] for key in dp_ids
                    if key not in self.solved and not self.blockers(self.catalog[key])]
        # Start with recognizable recurrence exercises before game-theory or
        # bit-manipulation questions that also happen to carry a DP tag.
        foundations = ("recursive-step-combinations", "leetcode-1137", "leetcode-118",
                       "leetcode-119", "exact-coin-reachability")
        def dp_rank(p):
            return (p.id not in self.targets, p.difficulty,
                    foundations.index(p.id) if p.id in foundations else len(foundations),
                    hashlib.sha256(f"{self.day}:dp:{p.id}".encode()).hexdigest())
        easy = sorted((p for p in eligible if p.difficulty <= 3), key=dp_rank)
        medium = sorted((p for p in eligible if 4 <= p.difficulty <= 7), key=dp_rank)
        focus = medium[:1] if medium_ready and medium else easy[:2]
        if not focus:
            # Do not silently bypass the DP progression gate when its pool is
            # exhausted. Unused credits return to ordinary interview practice.
            excluded = {key for key in dp_ids if 4 <= self.catalog[key].difficulty <= 7} if not medium_ready else set()
            return self._within_daily_budget(self._standard_session(excluded))

        selected = list(focus)
        budget = 5 - sum(self._credits(p) for p in focus)
        # Prefer other topics. A fully unlocked Hard DP interview target can
        # still use the normal three-credit track, so it is never stranded by
        # the two-credit cap on dedicated DP practice.
        normal = [p for p in self.ordered if p.id not in dp_ids or
                  (p.id in self.ready_targets and p.difficulty >= 8)]
        normal.sort(key=lambda p: p.id in dp_ids)
        normal.sort(key=lambda p: p.id not in self.ready_targets)
        for p in normal:
            cost = self._credits(p)
            if cost <= budget:
                selected.append(p)
                budget -= cost
        used = {p.id for p in selected} | self.solved
        pool = [p for p in self.catalog.values() if p.id not in used and p.id not in dp_ids
                and p.difficulty <= 3 and not self.blockers(p)]
        while budget and pool:
            counts = defaultdict(int)
            for p in selected:
                for topic in _focus(self.topics[p.id]):
                    counts[topic] += 1
            p = min(pool, key=lambda p: (sum(counts[t] for t in _focus(self.topics[p.id])),
                    hashlib.sha256(f"{self.day}:practice:{p.id}".encode()).hexdigest()))
            pool.remove(p)
            selected.append(p)
            budget -= 1
        return selected

    @staticmethod
    def _credits(problem):
        return 1 if problem.difficulty <= 3 else 2 if problem.difficulty <= 7 else 3

    def _within_daily_budget(self, candidates):
        selected, budget = [], 5
        for p in candidates:
            cost = self._credits(p)
            if cost <= budget:
                selected.append(p)
                budget -= cost
        return selected

    def _standard_session(self, excluded_ids=frozenset()):
        """Advance ready targets; use preparation without starving that progress."""
        candidates = [p for p in self.ordered if p.id not in excluded_ids]
        # A weak topic can keep producing new Easy preparation indefinitely.
        # It must not block interview targets already unlocked in other topics.
        # Keep the roadmap's stage/priority order among ready targets, and leave
        # preparation available as the session's Easy reinforcement.
        anchor = next((p for p in candidates if p.id in self.ready_targets), None)
        if anchor is not None:
            candidates.remove(anchor)
            candidates.insert(0, anchor)
        if not candidates or candidates[0].difficulty > 3:
            return choose_daily_session(candidates)
        easy = [p for p in candidates if p.difficulty <= 3]
        if len(easy) >= 5:
            return choose_daily_session(candidates)
        used = {p.id for p in candidates} | self.solved | set(excluded_ids)
        topic_counts = defaultdict(int)
        for p in easy[:5]:
            for topic in _focus(self.topics[p.id]):
                topic_counts[topic] += 1
        pool = [p for p in self.catalog.values()
                if p.id not in used and p.difficulty <= 3 and not self.blockers(p)]
        while len(easy) < 5 and pool:
            # Re-score after each pick so extra practice covers different topics.
            p = min(pool, key=lambda p: (
                sum(topic_counts[t] for t in _focus(self.topics[p.id])),
                hashlib.sha256(f"{self.day}:practice:{p.id}".encode()).hexdigest(),
            ))
            pool.remove(p)
            candidates.append(p)
            easy.append(p)
            used.add(p.id)
            for topic in _focus(self.topics[p.id]):
                topic_counts[topic] += 1
        if len(easy) < 5:
            # Only use Mediums after exhausting eligible Easy practice. The same
            # foundation, prerequisite, and repeated-failure gates still apply.
            candidates.extend(sorted(
                (p for p in self.catalog.values() if p.id not in used
                 and 4 <= p.difficulty <= 7 and not self.blockers(p)),
                key=lambda p: (p.difficulty, hashlib.sha256(
                    f"{self.day}:practice:{p.id}".encode()).hexdigest()),
            ))
        return choose_daily_session(candidates)

    def blockers(self, problem) -> list[Foundation]:
        if problem.id in self._blockers:
            return self._blockers[problem.id]
        missing = set()
        for topic in problem.prerequisites:
            topic = _normalize(topic)
            if self.mastery.get(topic, 0) < 70:
                missing.add(Foundation(topic, 1, max(3, min(7, problem.difficulty - 1))))
        if problem.difficulty > 3:
            for topic in self.topics[problem.id] & self.easy_topics - self.passed_easy_topics:
                missing.add(Foundation(topic, 1, 3))

        # Upper Medium needs a lower Medium; Hard needs two distinct Medium
        # successes in each relevant topic (one if only one exists), at 70%.
        if problem.difficulty >= 6:
            maximum = min(7, problem.difficulty - 1)
            for topic in _focus(self.topics[problem.id]):
                pool = [p for p in self.by_topic[topic] if 4 <= p.difficulty <= maximum]
                if not pool:
                    continue
                needed = min(2 if problem.difficulty >= 8 else 1, len(pool))
                passed = sum(p.id in self.solved for p in pool)
                if passed < needed or (problem.difficulty >= 8 and self.mastery.get(topic, 0) < 70):
                    missing.add(Foundation(topic, 4, maximum))
        history = self.history[problem.id]
        if len(history) >= 2 and all(a.result != "accepted" for a in history[:2]):
            last_failure = history[0].created_at
            focus = _focus(self.topics[problem.id])
            reinforced = any(
                key in self.catalog and self.catalog[key].difficulty < problem.difficulty
                and self.topics[key] & focus
                and any(a.result == "accepted" and a.created_at > last_failure for a in records)
                for key, records in self.history.items()
            )
            if not reinforced:
                for topic in sorted(focus):
                    if any(p.id not in self.solved and p.difficulty < problem.difficulty for p in self.by_topic[topic]):
                        missing.add(Foundation(topic, 1, problem.difficulty - 1))
                        break
        result = sorted(missing, key=lambda b: (b.maximum, b.topic, b.minimum))
        self._blockers[problem.id] = result
        return result

    def _prepare(self, problem, target_id: str, visited: set[str]) -> None:
        if problem.id in visited:
            return
        visited = visited | {problem.id}
        for need in self.blockers(problem):
            pool = [p for p in self.by_topic[need.topic]
                    if p.id not in self.solved and p.id not in visited
                    and need.minimum <= p.difficulty <= need.maximum]
            ready = [p for p in pool if not self.blockers(p)]
            if ready:
                candidate = min(ready, key=lambda p: (p.id not in self.targets, p.difficulty, p.id))
                if candidate.id not in self.targets:
                    self.preparation_for.setdefault(candidate.id, target_id)
            elif pool:
                self._prepare(pool[0], target_id, visited)

    def reason(self, problem_id: str) -> str | None:
        if problem_id in self.catalog and self.catalog[problem_id].difficulty <= 7 and any(
            t == "dp" or t == "dynamic-programming" or t.endswith("-dynamic-programming")
            or t.endswith("-dp") for t in self.topics[problem_id]
        ):
            return "Daily DP focus: build Easy foundations, then progress to one unlocked Medium."
        target = self.preparation_for.get(problem_id)
        if target:
            return f"Preparation for {self.catalog[target].title}: build the related foundations first."
        if problem_id not in self.targets and problem_id in self.catalog:
            return "Extra practice to round out today's workload and broaden topic coverage."
        return None

    def progress(self) -> dict:
        plans = study_list_options(set(self.catalog))
        for plan, source in zip(plans, study_list_snapshot()["lists"]):
            members = {p["problem_id"] for p in source["problems"]} & self.targets
            plan["solved"] = len(members & self.solved)
        return {
            "available": len(self.targets), "solved": len(self.targets & self.solved),
            "remaining": len(self.remaining), "ready": len(self.ready_targets),
            "blocked": len(self.remaining - self.ready_targets), "lists": plans,
        }
