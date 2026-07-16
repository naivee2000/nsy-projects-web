from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from car_compare.condition import sanitize_listing_condition
from car_compare.models import Listing, VehicleQuery
from car_compare.trim_match import trim_tokens
from car_compare.vehicle_match import vehicle_text_match_score
from car_compare.vehicle_catalog import collection_start_year, make_candidates


PRICE_RE = re.compile(
    r"(?<![\d,])(?P<prefix>\$\s*)?"
    r"(?P<value>(?:[1-9]\d{0,2}(?:,\d{3}){1,2}|[1-9]\d{2,7})(?:\.\d{2})?)"
    r"(?!\d|,\d{3})"
)
YEAR_RE = re.compile(r"\b(20\d{2}|19[8-9]\d)\b")
MILEAGE_RE = re.compile(r"(\d{1,3}(?:,\d{3})?|\d+(?:\.\d+)?)\s*(k)?\s*(?:mi|miles)\b", re.I)
VIN_RE = re.compile(r"\b([A-HJ-NPR-Z0-9]{17})\b", re.I)
NON_PRICE_CONTEXT_RE = re.compile(
    r"\b(?:msrp|sticker|discount|savings?|rebate|credit|cash\s*back|"
    r"down\s*payment|due\s*at\s*signing|monthly|per\s*month|payment|lease|"
    r"original(?:\s+price)?|list\s+price|market\s+value|was|package|options?|"
    r"accessor(?:y|ies)|add[ -]?on|(?:dealer|doc|documentation)\s+fee|fee|"
    r"delivery|destination|shipping|stock|listing\s+id|unit|order|"
    r"zip|postal(?:\s+code)?|address|vin(?:\s+ending)?|"
    r"(?:dealer|inventory|offer)\s+id|reference|serial|lot|"
    r"phone|telephone|tel|call|text|odometer|mileage)\b",
    re.I,
)
SALE_PRICE_CONTEXT_RE = re.compile(r"\b(?:sale|selling|asking|internet|our|vehicle)?\s*price\b", re.I)
PREFERRED_PRICE_CONTEXT_RE = re.compile(r"\b(?:sale|selling|asking|internet|our)\s+price\b|\bnow\b", re.I)
NON_MILEAGE_CONTEXT_RE = re.compile(
    r"\b(?:epa|driving\s+range|range|warranty|coverage|radius|distance)\b",
    re.I,
)
ZERO_RESULTS_RE = re.compile(
    r"(?im)^\s*(?:0\s+(?:matches|results|listings?|vehicles?)\b|"
    r"no\s+(?:matching\s+)?(?:results?|matches|listings?|vehicles?|cars?)\s+found\b)"
)
SEARCH_RESULTS_HEADING_RE = re.compile(r"\bfor\s+sale\s+(?:in|near)\b", re.I)
POSTAL_CONTEXT_RE = re.compile(r"\b(?:zip|postal(?:\s+code)?)\b", re.I)
LISTING_CONDITION_RE = re.compile(
    r"^\s*(?:brand\s+new|new|used|pre[- ]?owned|certified(?:\s+pre[- ]?owned)?|cpo)\b",
    re.I,
)
DEALER_LABEL_RE = re.compile(
    r"^(?:sponsored by|dealer|seller|sold by|provided by)\s*:?\s*(?P<dealer>.+)$",
    re.I,
)
DETAIL_PATH_RE = re.compile(r"/(?:vehicle|inventory|vin|details?)/", re.I)
KNOWN_MAKE_TOKEN_GROUPS = [
    re.findall(r"[a-z0-9]+", " ".join(alias_tokens).lower())
    for alias_tokens, _ in make_candidates()
]


def parse_visible_listing_text(
    source: str,
    url: str,
    text: str,
    request: VehicleQuery,
    *,
    card_scoped: bool = False,
) -> list[Listing]:
    if ZERO_RESULTS_RE.search(text):
        return []

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    listings: list[Listing] = []
    for idx, line in enumerate(lines):
        year_match = YEAR_RE.search(line)
        if not year_match or not _is_listing_header(line, request):
            continue
        listing_year = int(year_match.group(1))
        if listing_year > _runtime_current_year() + 2:
            continue
        window = _listing_window(lines, idx, request)
        haystack = " ".join(window).lower()
        match = vehicle_text_match_score(request, haystack, source=source)
        if not match["accepted"]:
            continue

        price = _find_price(window, url=url)
        if not price:
            continue
        if not _has_credible_listing_signals(window, price, url):
            continue

        mileage = _find_mileage(window)
        vin = _find_vin(window)
        title = _title_from_window(window, url=url)
        trim = _trim_from_title(title, request)
        trim = _append_verified_drivetrain_context(trim, haystack, request)
        condition_context = [*(lines[idx - 1 : idx] if card_scoped and idx else []), *window]
        declared_condition = (
            "cpo"
            if _looks_cpo(condition_context)
            else "used"
            if _looks_used(condition_context)
            else "new"
            if _looks_new(condition_context)
            else "used"
        )
        condition = sanitize_listing_condition(declared_condition, title, listing_year)
        listings.append(
            Listing(
                source=source,
                year=listing_year,
                price=price,
                trim=trim,
                mileage=mileage,
                title=title,
                url=url,
                vin=vin,
                dealer=_find_dealer(window),
                confidence=str(match["confidence"]),
                condition=condition,
            )
        )

    return _dedupe(listings)


def parse_visible_listing_cards(
    source: str,
    cards: list[dict[str, object]],
    request: VehicleQuery,
) -> list[Listing]:
    listings: list[Listing] = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        text = str(card.get("text") or "").strip()
        url = str(card.get("url") or "").strip()
        if not text or not url:
            continue
        listings.extend(
            parse_visible_listing_text(
                source,
                url,
                text,
                request,
                card_scoped=True,
            )
        )
    return _dedupe(listings)


def listing_year_in_scope(year: int, request: VehicleQuery) -> bool:
    if request.target_year:
        return year == request.target_year
    current_year = _runtime_current_year()
    start_year = max(
        current_year - request.max_age,
        request.start_year or current_year - request.max_age,
    )
    start_year = collection_start_year(request.make, request.model, start_year)
    return start_year <= year <= current_year


def _find_price(lines: list[str], *, url: str = "") -> float | None:
    candidates: list[tuple[int, int, int, float]] = []
    url_postal_codes = _postal_codes_from_url(url)
    for line_index, line in enumerate(lines):
        matches = list(PRICE_RE.finditer(line))
        for index, match in enumerate(matches):
            if _looks_like_mileage_candidate(line, match):
                continue
            if _looks_like_postal_candidate(lines, line_index, match, url_postal_codes):
                continue
            raw = match.group("value").replace(",", "")
            numeric_value = float(raw)
            if len(raw.split(".", 1)[0]) < 5 and not match.group("prefix"):
                candidate_only = re.fullmatch(r"\s*(?:[1-9]\d{3}|[1-9]\d{0,2},\d{3})\s*", line)
                labeled_price = SALE_PRICE_CONTEXT_RE.search(line[: match.start()])
                if not candidate_only and not labeled_price:
                    continue
                if numeric_value < 5000 and "," not in match.group("value") and not labeled_price:
                    continue
            previous_end = matches[index - 1].end() if index else 0
            next_start = matches[index + 1].start() if index + 1 < len(matches) else len(line)
            before = line[previous_end:match.start()]
            whole_prefix = line[: match.start()]
            suffix = line[match.end():next_start]
            suffix = re.split(r"[,;|]", suffix, maxsplit=1)[0]
            explicitly_price_labeled = bool(SALE_PRICE_CONTEXT_RE.search(before))
            preferred_price_labeled = bool(PREFERRED_PRICE_CONTEXT_RE.search(before))
            if (
                match.start() > 0
                and line[match.start() - 1] == "#"
                and not explicitly_price_labeled
            ):
                continue
            if NON_PRICE_CONTEXT_RE.search(before) and not PREFERRED_PRICE_CONTEXT_RE.search(before):
                continue
            if NON_PRICE_CONTEXT_RE.search(whole_prefix) and not (
                explicitly_price_labeled or preferred_price_labeled
            ):
                continue
            if not SALE_PRICE_CONTEXT_RE.search(before) and NON_PRICE_CONTEXT_RE.search(suffix):
                continue
            try:
                value = numeric_value
            except ValueError:
                continue
            if 500 <= value <= 10_000_000:
                priority = 3 if PREFERRED_PRICE_CONTEXT_RE.search(before) else 2 if SALE_PRICE_CONTEXT_RE.search(before) else 1
                candidates.append((priority, -line_index, -index, value))
    if not candidates:
        return None
    return max(candidates)[3]


def _looks_like_mileage_candidate(line: str, match: re.Match[str]) -> bool:
    after = line[match.end() : match.end() + 12].lower()
    before = line[max(0, match.start() - 4) : match.start()].lower()
    return "mi" in after or "mile" in after or before.endswith("k ")


def _looks_like_postal_candidate(
    lines: list[str],
    line_index: int,
    match: re.Match[str],
    url_postal_codes: set[str],
) -> bool:
    if match.group("prefix") or SALE_PRICE_CONTEXT_RE.search(lines[line_index][: match.start()]):
        return False
    value = match.group("value").replace(",", "").split(".", 1)[0]
    if not re.fullmatch(r"\d{5}", value) or not re.fullmatch(r"\s*\d{5}\s*", lines[line_index]):
        return False
    if value in url_postal_codes:
        return True
    nearby = " ".join(lines[max(0, line_index - 1) : line_index + 2])
    return bool(POSTAL_CONTEXT_RE.search(nearby))


def _postal_codes_from_url(url: str) -> set[str]:
    if not url:
        return set()
    values = parse_qs(urlparse(url).query, keep_blank_values=False)
    result: set[str] = set()
    for key, candidates in values.items():
        normalized_key = re.sub(r"[^a-z]", "", key.casefold())
        if "zip" not in normalized_key and "postal" not in normalized_key:
            continue
        for candidate in candidates:
            match = re.fullmatch(r"\s*(\d{5})(?:-\d{4})?\s*", candidate)
            if match:
                result.add(match.group(1))
    return result


def _listing_window(lines: list[str], start: int, request: VehicleQuery, limit: int = 16) -> list[str]:
    window = [lines[start]]
    for line in lines[start + 1 : start + limit]:
        if line == "---":
            break
        if YEAR_RE.search(line) and _is_listing_header(line, request):
            break
        window.append(line)
    return window


def _is_listing_header(line: str, request: VehicleQuery) -> bool:
    year = YEAR_RE.search(line)
    if not year or SEARCH_RESULTS_HEADING_RE.search(line):
        return False
    tail_tokens = re.findall(r"[a-z0-9]+", line[year.end() :].lower())
    request_tokens = re.findall(r"[a-z0-9]+", (request.make or "").lower())
    groups = [*KNOWN_MAKE_TOKEN_GROUPS, request_tokens]
    return any(group and _contains_token_sequence(tail_tokens, group) for group in groups)


def _contains_token_sequence(haystack: list[str], needle: list[str]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    return any(haystack[index : index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def _title_from_window(lines: list[str], *, url: str = "") -> str:
    title_lines: list[str] = []
    for line in lines[:4]:
        if title_lines and (_find_price([line], url=url) is not None or MILEAGE_RE.search(line) or VIN_RE.search(line)):
            break
        if title_lines and re.search(r"\b(?:check availability|see payment|no accidents|sponsored by)\b", line, re.I):
            break
        title_lines.append(line)
    return " ".join(title_lines) if title_lines else lines[0]


def _has_credible_listing_signals(lines: list[str], price: float, url: str) -> bool:
    if _find_mileage(lines) is not None or _find_vin(lines):
        return True
    if any(LISTING_CONDITION_RE.search(line) for line in lines[:4]):
        return True
    if _price_is_explicitly_labeled(lines, price):
        return True
    return bool(DETAIL_PATH_RE.search(urlparse(url).path))


def _price_is_explicitly_labeled(lines: list[str], price: float) -> bool:
    for line in lines:
        for match in PRICE_RE.finditer(line):
            try:
                candidate = float(match.group("value").replace(",", ""))
            except ValueError:
                continue
            if candidate != price:
                continue
            if match.group("prefix") or SALE_PRICE_CONTEXT_RE.search(line[: match.start()]):
                return True
    return False


def _find_mileage(lines: list[str]) -> int | None:
    candidates: list[tuple[int, int, int]] = []
    for line_index, line in enumerate(lines):
        matches = list(MILEAGE_RE.finditer(line))
        for match_index, match in enumerate(matches):
            prefix = _local_field_prefix(line, match.start())
            next_start = matches[match_index + 1].start() if match_index + 1 < len(matches) else len(line)
            suffix = re.split(r"[|;·•]", line[match.end():next_start], maxsplit=1)[0]
            if (
                NON_MILEAGE_CONTEXT_RE.search(prefix)
                or re.search(r"\brange\s*:?\s*\d", prefix, re.I)
                or re.search(r"\b(?:mi|miles)\s+(?:away|range)\b", suffix, re.I)
            ):
                continue
            number = float(match.group(1).replace(",", ""))
            if match.group(2):
                number *= 1000
            priority = 3 if re.search(r"\b(?:odometer|mileage)\b", prefix, re.I) else 2
            candidates.append((priority, -line_index, int(number)))
    if not candidates:
        return None
    return max(candidates)[2]


def _local_field_prefix(line: str, end: int) -> str:
    prefix = line[:end]
    parts = re.split(r"[|;·•]", prefix)
    return parts[-1] if parts else prefix


def _find_vin(lines: list[str]) -> str:
    for line in lines:
        match = VIN_RE.search(line)
        if match:
            return match.group(1).upper()
    return ""


def _find_dealer(lines: list[str]) -> str:
    for line in lines:
        match = DEALER_LABEL_RE.match(line.strip())
        if not match:
            continue
        dealer = re.sub(r"\s+", " ", match.group("dealer")).strip(" -:|")
        if 2 <= len(dealer) <= 160:
            return dealer
    return ""


def _looks_new(lines: list[str]) -> bool:
    return any(
        re.search(r"^(?:brand new|new vehicle|new)(?!\s+arrival\b)\b", line.strip(), re.I)
        for line in lines[:4]
    )


def _looks_used(lines: list[str]) -> bool:
    return any(
        re.search(r"^(?:used|pre[- ]?owned)\b", line.strip(), re.I)
        for line in lines[:4]
    )


def _looks_cpo(lines: list[str]) -> bool:
    return any(
        re.search(r"\b(?:certified(?:\s+pre[- ]?owned)?|cpo)\b", line, re.I)
        for line in lines[:8]
    )


def _trim_from_title(title: str, request: VehicleQuery) -> str:
    pattern = re.compile(
        rf"\b{re.escape(request.make)}\s+{re.escape(request.model)}\b",
        re.I,
    )
    parts = pattern.split(title, maxsplit=1)
    if len(parts) == 2:
        return re.sub(r"\s+", " ", parts[1]).strip()
    return request.trim


def _append_verified_drivetrain_context(trim: str, haystack: str, request: VehicleQuery) -> str:
    requested = set(trim_tokens(request.trim))
    observed = set(trim_tokens(haystack))
    trim_identity = set(trim_tokens(trim))
    additions = []
    for token, label in (("awd", "AWD"), ("rwd", "RWD"), ("fwd", "FWD"), ("4wd", "4WD")):
        if token in requested and token in observed and token not in trim_identity:
            additions.append(label)
    return " ".join([trim, *additions]).strip()


def _dedupe(listings: list[Listing]) -> list[Listing]:
    seen = set()
    result = []
    for item in listings:
        key = (item.source, item.year, int(item.price), item.mileage, item.title.lower())
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _runtime_current_year() -> int:
    return datetime.now(timezone.utc).year
