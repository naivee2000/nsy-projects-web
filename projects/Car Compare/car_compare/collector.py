from __future__ import annotations

import json
import math
import re
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from car_compare.models import Listing, MSRP, VehicleQuery
from car_compare.parser import parse_vehicle_query
from car_compare.codex_cli import codex_environment, codex_login_status, find_codex_cli
from car_compare.sources.visor_facets import collect_visor_public_facets
from car_compare.sources.source_plan import build_collection_plan


CODEX_TIMEOUT_SECONDS = 900
MIN_MODEL_YEAR = 1980
MAX_SCHEMA_MODEL_YEAR = 2100
MIN_LISTING_PRICE = 500
MAX_LISTING_PRICE = 10_000_000
MIN_MSRP_PRICE = 5_000
MAX_MSRP_PRICE = 10_000_000
# Backward-compatible listing bounds for callers migrating to the split names.
MIN_VEHICLE_PRICE = MIN_LISTING_PRICE
MAX_VEHICLE_PRICE = MAX_LISTING_PRICE
MAX_MILEAGE = 1_000_000


@dataclass
class CollectionJob:
    id: str
    query: str
    status: str
    created_at: float
    updated_at: float
    message: str = ""
    result: dict[str, Any] | None = None
    error: str = ""
    codex_path: str = ""
    process_id: int = 0
    started_at: float = 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["createdAt"] = self.created_at
        data["updatedAt"] = self.updated_at
        if self.started_at:
            data["elapsedSeconds"] = max(0, int(time.time() - self.started_at))
        else:
            data["elapsedSeconds"] = 0
        return data


@dataclass
class CollectorConfig:
    root: Path
    codex_path: str = ""
    dry_run: bool = False
    timeout_seconds: int = CODEX_TIMEOUT_SECONDS
    use_visor_facets: bool = True
    jobs_dir: Path = field(init=False)
    schema_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.jobs_dir = self.root / "data" / "collector_jobs"
        self.schema_path = self.root / "car_compare" / "collector_schema.json"


class CollectionManager:
    def __init__(self, config: CollectorConfig):
        self.config = config
        self.config.jobs_dir.mkdir(parents=True, exist_ok=True)
        self._jobs: dict[str, CollectionJob] = {}
        self._lock = threading.Lock()

    def availability(self) -> dict[str, Any]:
        path = self._codex_path()
        status = codex_login_status(path) if path else codex_login_status(self.config.codex_path)
        website_available = bool(path and status["authenticated"])
        visor_available = bool(self.config.use_visor_facets)
        if website_available and visor_available:
            message = "Visor facets and Codex website collector ready"
        elif website_available:
            message = "Codex website collector ready"
        elif visor_available:
            message = f"Visor facet collector ready; {status['message']}"
        else:
            message = status["message"]
        return {
            "available": bool(visor_available or website_available),
            "visorAvailable": visor_available,
            "websiteCollectorAvailable": website_available,
            "codexPath": path,
            "codexHome": status["codexHome"],
            "authenticated": status["authenticated"],
            "authMethod": status["authMethod"],
            "dryRun": self.config.dry_run,
            "message": message,
        }

    def start(self, query: str, max_age: int | None = None) -> CollectionJob:
        request = parse_vehicle_query(query)
        if max_age:
            request.max_age = max_age
        job = CollectionJob(
            id=uuid.uuid4().hex,
            query=request.raw,
            status="queued",
            created_at=time.time(),
            updated_at=time.time(),
            message="Queued website collection",
            codex_path=self._codex_path(),
        )
        with self._lock:
            self._jobs[job.id] = job
        thread = threading.Thread(target=self._run_job, args=(job.id, request), daemon=True)
        thread.start()
        return job

    def get(self, job_id: str) -> CollectionJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def listings_from_job(self, job_id: str) -> list[Listing]:
        job = self.get(job_id)
        if not job or not job.result:
            return []
        return listings_from_result(job.result)

    def msrp_from_job(self, job_id: str) -> MSRP | None:
        job = self.get(job_id)
        if not job or not job.result:
            return None
        msrp = msrp_from_result(job.result)
        request = parse_vehicle_query(job.query)
        return msrp if msrp and _msrp_matches_request(msrp, request) else None

    def _run_job(self, job_id: str, request: VehicleQuery) -> None:
        self._update(job_id, status="running", message="Starting Codex website collection")
        codex_path = self._codex_path()
        codex_status = codex_login_status(codex_path) if codex_path else codex_login_status(self.config.codex_path)
        if self.config.dry_run:
            result = _dry_run_result(request)
            self._write_job_result(job_id, result)
            self._update(job_id, status="completed", message="Dry-run collection completed", result=result)
            return
        facet_result: dict[str, Any] | None = None
        if self.config.use_visor_facets:
            self._update(job_id, status="running", message="Checking Visor public market facets")
            try:
                facet_result = collect_visor_public_facets(request)
            except Exception as exc:
                facet_result = {
                    "query": request.raw,
                    "status": "blocked",
                    "notes": [f"Visor public facets failed: {exc}"],
                    "msrp": None,
                    "sources": [],
                    "listings": [],
                }
            if facet_result.get("listings"):
                self._update(
                    job_id,
                    status="running",
                    message=(
                        f"Visor public facets collected {len(facet_result.get('listings') or [])} aggregate observations; "
                        "continuing to Codex website collection"
                    ),
                )
            else:
                self._update(job_id, status="running", message="Visor facets had no listings; starting Codex website collection")
        if not codex_path or not codex_status["authenticated"]:
            unavailable_note = (
                "Codex CLI was not found"
                if not codex_path
                else "Codex CLI is not logged in for the deployment user"
            )
            if facet_result and facet_result.get("listings"):
                facet_result["status"] = "partial"
                facet_result.setdefault("notes", []).append(f"{unavailable_note}, so only Visor public facets were collected.")
                self._write_job_result(job_id, facet_result)
                self._update(
                    job_id,
                    status="completed",
                    message=f"Visor public facets collected {len(facet_result.get('listings') or [])} aggregate observations",
                    result=facet_result,
                )
                return
            self._update(
                job_id,
                status="blocked",
                message=f"{unavailable_note} and Visor public facets had no listings.",
                error="codex_not_authenticated" if codex_path else "codex_not_found",
            )
            return

        job_dir = self.config.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        output_path = job_dir / "collector_result.json"
        stdout_path = job_dir / "codex_stdout.log"
        stderr_path = job_dir / "codex_stderr.log"
        prompt = build_codex_prompt(request)
        command = build_codex_command(
            codex_path=codex_path,
            root=self.config.root,
            schema_path=self.config.schema_path,
            output_path=output_path,
        )
        start_time = time.time()
        try:
            with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open("w", encoding="utf-8") as stderr_file:
                process = subprocess.Popen(
                    command,
                    env=codex_environment(),
                    stdin=subprocess.PIPE,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    text=True,
                )
                self._update(
                    job_id,
                    status="running",
                    message=f"Codex process started (PID {process.pid}).",
                    process_id=process.pid,
                    started_at=start_time,
                )
                if process.stdin:
                    try:
                        process.stdin.write(prompt)
                        process.stdin.close()
                    except BrokenPipeError:
                        pass
                while process.poll() is None:
                    elapsed = int(time.time() - start_time)
                    if elapsed >= self.config.timeout_seconds:
                        process.kill()
                        process.wait()
                        self._update(
                            job_id,
                            status="failed",
                            message=f"Codex collection timed out after {_format_elapsed(elapsed)}",
                            error=f"Timed out after {self.config.timeout_seconds} seconds.",
                        )
                        return
                    self._update(
                        job_id,
                        status="running",
                        message=(
                            f"Codex is still running for {_format_elapsed(elapsed)} "
                            f"(PID {process.pid}). Waiting for website collection JSON."
                        ),
                    )
                    time.sleep(min(1, max(1, self.config.timeout_seconds - elapsed)))
                returncode = process.returncode
        except OSError as exc:
            if facet_result and facet_result.get("listings"):
                facet_result["status"] = "partial"
                facet_result.setdefault("notes", []).append(f"Could not launch Codex collector after Visor facets: {exc}")
                self._write_job_result(job_id, facet_result)
                self._update(
                    job_id,
                    status="completed",
                    message=(
                        f"Visor public facets collected {len(facet_result.get('listings') or [])} aggregate observations; "
                        "Codex could not be launched"
                    ),
                    result=facet_result,
                )
                return
            self._update(
                job_id,
                status="failed",
                message="Could not launch Codex collector",
                error=str(exc),
            )
            return

        stdout_text = _read_text(stdout_path)
        stderr_text = _read_text(stderr_path)
        if returncode != 0:
            error_text = clean_codex_error(stderr_text or stdout_text)
            if facet_result and facet_result.get("listings"):
                facet_result["status"] = "partial"
                facet_result.setdefault("notes", []).append(f"Codex website collection failed after Visor facets: {error_text}")
                self._write_job_result(job_id, facet_result)
                self._update(
                    job_id,
                    status="completed",
                    message=(
                        f"Visor public facets collected {len(facet_result.get('listings') or [])} aggregate observations; "
                        "Codex website collection failed"
                    ),
                    result=facet_result,
                )
                return
            self._update(
                job_id,
                status="failed",
                message=codex_failure_message(error_text),
                error=error_text,
            )
            return

        try:
            result = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if facet_result and facet_result.get("listings"):
                facet_result["status"] = "partial"
                facet_result.setdefault("notes", []).append(f"Codex collector did not produce valid JSON after Visor facets: {exc}")
                self._write_job_result(job_id, facet_result)
                self._update(
                    job_id,
                    status="completed",
                    message=(
                        f"Visor public facets collected {len(facet_result.get('listings') or [])} aggregate observations; "
                        "Codex JSON was invalid"
                    ),
                    result=facet_result,
                )
                return
            self._update(
                job_id,
                status="failed",
                message="Codex collector did not produce valid JSON",
                error=str(exc),
            )
            return

        result = _merge_collector_results(facet_result, result, request)
        self._write_job_result(job_id, result)
        final_status = "completed" if result.get("status") in {"success", "partial"} else "blocked"
        self._update(
            job_id,
            status=final_status,
            message=f"Collection {result.get('status', 'finished')}",
            result=result,
        )

    def _codex_path(self) -> str:
        return find_codex_cli(self.config.codex_path)

    def _update(self, job_id: str, **updates: Any) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in updates.items():
                setattr(job, key, value)
            job.updated_at = time.time()

    def _write_job_result(self, job_id: str, result: dict[str, Any]) -> None:
        job_dir = self.config.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "collector_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


def build_codex_prompt(request: VehicleQuery) -> str:
    plan = build_collection_plan(request)
    return f"""
You are collecting public car market data for the local Car Compare app.

Vehicle query:
{request.raw}

Parsed vehicle:
make={request.make}
model={request.model}
trim={request.trim or "(none)"}
trend_horizon_years={request.max_age}

Vehicle resolver:
{json.dumps(plan["resolution"], indent=2)}

Collection targets:
{json.dumps(plan["targets"], indent=2)}

Rules:
- Do not edit project files.
- Prefer normal visible website/browser interaction if browser automation is available.
- If you are running inside Codex desktop and can show/use the browser, make website operation visible.
- Open the target URLs, confirm the visible page matches the requested vehicle, scroll results, and click visible Load More / See More Results / Next controls when available.
- After clicking a load-more control, verify that listing count, visible listing text, or page height changed. If it does not change, record that in source notes and continue.
- Stop on CAPTCHA, login-only wall, paywall, or access refusal. Do not bypass restrictions.
- Each target includes required_keywords, exclude_keywords, model_aliases, and location_policy. Treat those as binding collection rules.
- The resolver includes chips with mode="exact", mode="range", mode="constrained", or mode="all". Exact/range chips restrict collection; constrained chips inherit named sibling exclusions from the exact trim; all chips mean include every visible variant for that dimension.
- If trim, body_style, drivetrain, or powertrain is marked all, do not reject rows just because that field differs or is missing. Only require make/model and any exact chips.
- Extract only listings where every required keyword appears as a separate visible token in the listing row/detail page and none of the exclude keywords appear. For example, GT is not the same token as GTC.
- If a site redirects a model URL to all cars for the make, that is not automatically a failure. Continue only if visible rows can be filtered by the required/exclude rules; otherwise mark the source unavailable.
- Set or confirm the search radius/location to Nationwide, All miles, Unlimited, or the closest equivalent. If a zip is required, use it only to unlock the search and record the nationwide setting in source notes.
- If a source cannot be made nationwide/all-US, record that limitation clearly and avoid mixing it into a national depreciation trend unless no better source exists.
- Collect actual new-car examples when visible on manufacturer inventory pages, Autotrader/Edmunds new inventory, or Visor new-car results. Mark those listings with condition="new" and use a title beginning with "New ".
- Mark ordinary used examples with condition="used"; mark certified pre-owned with condition="cpo" when the page clearly says CPO/certified.
- Capture VIN and dealer when visible; if VIN is only visible on detail pages, open a small number of listing detail pages when practical.
- Deduplication happens in the app, but include VIN/dealer when possible.
- Listing price must be the vehicle asking/sale price between $500 and $10,000,000. Never use a payment, down payment, discount, fee, delivery charge, package, option, rebate, MSRP, or market-value reference as listing price.
- Try to collect enough listings across model years to support depreciation buckets.
- Use manufacturer official MSRP between $5,000 and $10,000,000 when practical; never place a monthly payment in MSRP. If the manufacturer site also exposes current new inventory prices, include those as condition="new" listings. Otherwise set msrp to null.

Return only JSON matching the provided schema. Do not include Markdown.
""".strip()


def build_codex_command(codex_path: str, root: Path, schema_path: Path, output_path: Path) -> list[str]:
    return [
        codex_path,
        "--ask-for-approval",
        "never",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--output-schema",
        str(schema_path),
        "-o",
        str(output_path),
        "-C",
        str(root),
        "-",
    ]


def _merge_collector_results(
    facet_result: dict[str, Any] | None,
    codex_result: dict[str, Any],
    request: VehicleQuery | None = None,
) -> dict[str, Any]:
    if not facet_result:
        merged = dict(codex_result)
        codex_msrp = msrp_from_result({"msrp": codex_result.get("msrp")})
        if codex_msrp and (not request or _msrp_matches_request(codex_msrp, request)):
            merged["msrp"] = codex_msrp.to_dict()
        else:
            merged["msrp"] = None
        return merged

    merged = dict(codex_result)
    merged["query"] = codex_result.get("query") or facet_result.get("query")
    merged_statuses = {str(facet_result.get("status") or ""), str(codex_result.get("status") or "")}
    if "success" in merged_statuses and not (merged_statuses - {"success", ""}):
        merged["status"] = "success"
    elif codex_result.get("listings") or facet_result.get("listings"):
        merged["status"] = "partial" if "blocked" in merged_statuses or "partial" in merged_statuses else "success"
    else:
        merged["status"] = codex_result.get("status") or facet_result.get("status") or "blocked"

    merged["notes"] = [*(facet_result.get("notes") or []), *(codex_result.get("notes") or [])]
    merged["sources"] = [*(facet_result.get("sources") or []), *(codex_result.get("sources") or [])]
    merged["evidence"] = [*(facet_result.get("evidence") or []), *(codex_result.get("evidence") or [])]
    merged["listings"] = [*(facet_result.get("listings") or []), *(codex_result.get("listings") or [])]
    codex_msrp = msrp_from_result({"msrp": codex_result.get("msrp")})
    facet_msrp = msrp_from_result({"msrp": facet_result.get("msrp")})
    if codex_msrp and request and not _msrp_matches_request(codex_msrp, request):
        codex_msrp = None
    if facet_msrp and request and not _msrp_matches_request(facet_msrp, request):
        facet_msrp = None
    selected_msrp = codex_msrp or facet_msrp
    merged["msrp"] = selected_msrp.to_dict() if selected_msrp else None
    return merged


def _msrp_matches_request(msrp: MSRP, request: VehicleQuery) -> bool:
    if request.target_year:
        return msrp.year == request.target_year
    if msrp.year is None:
        return False
    current_year = _runtime_current_year()
    return current_year <= msrp.year <= current_year + 2


def clean_codex_error(raw: str) -> str:
    structured_message = _structured_error_message(raw)
    if structured_message:
        return _cap_error(structured_message)

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    important = [
        line
        for line in lines
        if not line.startswith("WARN ")
        and " WARN " not in line
        and "codex_core_plugins::manifest" not in line
        and "codex_core_skills::loader" not in line
    ]
    usage_lines = [line for line in important if "usage limit" in line.lower()]
    if usage_lines:
        return _usage_limit_error("\n".join(dict.fromkeys(usage_lines)))
    error_lines = [line for line in important if line.startswith("ERROR") or " ERROR " in line]
    if error_lines:
        return _cap_error("\n".join(error_lines))
    if important:
        return _cap_error("\n".join(important))
    return _cap_error(raw.strip() or "Codex exited without an error message.")


def _structured_error_message(raw: str) -> str:
    match = re.search(r'"message"\s*:\s*"(?P<message>(?:\\"|[^"])*)"', raw, re.S)
    if not match:
        return ""
    try:
        return json.loads(f'"{match.group("message")}"')
    except json.JSONDecodeError:
        return match.group("message").replace('\\"', '"')


def codex_failure_message(error_text: str) -> str:
    lower = error_text.lower()
    if "usage limit" in lower:
        return "Codex usage limit reached"
    if "unexpected argument" in lower:
        return "Codex command option failed"
    if "invalid_json_schema" in lower or "schema" in lower:
        return "Codex collector schema failed"
    return "Codex collector failed"


def _cap_error(text: str, limit: int = 1200) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1].rstrip()}..."


def _format_elapsed(seconds: int) -> str:
    seconds = max(0, int(seconds))
    minutes, secs = divmod(seconds, 60)
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}h {mins}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _usage_limit_error(text: str) -> str:
    match = re.search(r"try again at ([^.]+)", text, re.I)
    retry = f" Try again at {match.group(1).strip()}." if match else ""
    return f"Codex usage limit reached.{retry}"


def listings_from_result(result: dict[str, Any]) -> list[Listing]:
    rows = []
    for item in result.get("listings") or []:
        if not isinstance(item, dict):
            continue
        try:
            year_number = float(item["year"])
            if not math.isfinite(year_number) or not year_number.is_integer():
                continue
            year = int(year_number)
            price = float(item["price"])
            mileage = _optional_int(item.get("mileage"))
            if not MIN_MODEL_YEAR <= year <= _runtime_current_year() + 2:
                continue
            if not math.isfinite(price) or not MIN_LISTING_PRICE <= price <= MAX_LISTING_PRICE:
                continue
            if mileage is not None and not 0 <= mileage <= MAX_MILEAGE:
                continue
            title_condition = _condition_from_title(item.get("title"))
            condition = title_condition or str(item.get("condition") or "unknown").lower()
            if condition not in {"new", "used", "cpo", "unknown"}:
                condition = "unknown"
            rows.append(
                Listing(
                    source=str(item.get("source") or "codex_collector"),
                    year=year,
                    price=price,
                    trim=str(item.get("trim") or ""),
                    mileage=mileage,
                    title=str(item.get("title") or ""),
                    url=str(item.get("url") or ""),
                    vin=str(item.get("vin") or ""),
                    dealer=str(item.get("dealer") or ""),
                    confidence=str(item.get("confidence") or "codex_collected"),
                    condition=condition,
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return rows


def msrp_from_result(result: dict[str, Any]) -> MSRP | None:
    item = result.get("msrp")
    if not isinstance(item, dict):
        return None
    price = item.get("price")
    if price in (None, ""):
        return None
    try:
        price_float = float(price)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(price_float) or not MIN_MSRP_PRICE <= price_float <= MAX_MSRP_PRICE:
        return None
    year = _optional_int(item.get("year"))
    if year is not None and not MIN_MODEL_YEAR <= year <= _runtime_current_year() + 2:
        return None
    return MSRP(
        price=price_float,
        label=str(item.get("label") or "Codex collected MSRP"),
        source=str(item.get("source") or "codex_collector"),
        url=str(item.get("url") or ""),
        year=year,
    )


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _runtime_current_year() -> int:
    return datetime.now(timezone.utc).year


def _condition_from_title(value: Any) -> str:
    title = str(value or "").lower().strip()
    if title.startswith("new arrival"):
        return "used"
    if re.match(r"^used\b", title):
        return "used"
    if re.match(r"^(?:certified(?:\s+pre[- ]?owned)?|cpo)\b", title):
        return "cpo"
    if re.match(r"^new\b", title):
        return "new"
    # A neutral title has no authority over structured collector evidence.
    return ""


def _dry_run_result(request: VehicleQuery) -> dict[str, Any]:
    plan = build_collection_plan(request)
    return {
        "query": request.raw,
        "status": "blocked",
        "notes": ["Dry-run mode: no websites were opened."],
        "msrp": None,
        "sources": [
            {
                "source": target["source"],
                "url": target["url"],
                "status": "unavailable",
                "load_more_clicked": 0,
                "notes": "Dry-run target only.",
            }
            for target in plan["targets"]
        ],
        "listings": [],
    }
