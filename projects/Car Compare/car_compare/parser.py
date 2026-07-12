from __future__ import annotations

import re

from car_compare.models import VehicleQuery
from car_compare.vehicle_catalog import (
    MERCEDES_CLASS_LETTERS,
    MAKE_ALIASES,
    MODEL_MAKE_HINTS,
    display_token,
    make_candidates,
    model_candidates,
    trim_candidates,
)

RANGE_WORDS = {"after", "since", "from", "newer", "newer-than"}
STOP_WORDS = {"depreciation", "trend", "value", "values", "price", "prices"}


def parse_vehicle_query(text: str) -> VehicleQuery:
    raw = " ".join((text or "").strip().split())
    if not raw:
        return VehicleQuery(raw="", make="", model="")

    lower = raw.lower()
    start_year = _range_year(lower)
    years = [int(item) for item in re.findall(r"\b(19\d{2}|20\d{2})\b", lower)]
    target_year = None
    if years and start_year is None:
        target_year = years[-1]

    cleaned = _split_attached_terms(lower)
    cleaned = re.sub(r"\b(19\d{2}|20\d{2})\b", " ", cleaned)
    cleaned = re.sub(r"\b(after|since|from|newer than|newer-than)\b", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9+\- ]+", " ", cleaned)
    tokens = [tok for tok in cleaned.split() if tok not in STOP_WORDS]
    corrections: list[dict[str, str]] = []

    make = ""
    make_index = 0
    make_len = 0
    for i in range(len(tokens)):
        for alias_tokens, canonical in make_candidates():
            if tokens[i : i + len(alias_tokens)] == alias_tokens:
                make = canonical
                make_index = i
                make_len = len(alias_tokens)
                break
        if make:
            break

    if not make and tokens:
        normalized_make = _exact_make_prefix(tokens)
        if normalized_make:
            make, make_len, _ = normalized_make
            make_index = 0

    # A one-token exact alias can be only the prefix of a longer make. Prefer a
    # uniquely close longer alias ("Mercedes Bnez", "Rolls Royec") but never
    # replace a complete exact make with an equal/shorter fuzzy candidate.
    longer_fuzzy_make = (
        _fuzzy_make_prefix(
            tokens,
            minimum_alias_words=make_len,
            exact_prefix=" ".join(tokens[:make_len]),
        )
        if tokens and make and make_index == 0
        else None
    )
    if longer_fuzzy_make and (not make or longer_fuzzy_make[1] > make_len):
        make, make_len, original = longer_fuzzy_make
        make_index = 0
        corrections.append(_correction("make", original, make))

    if not make and tokens and tokens[0] in MODEL_MAKE_HINTS:
        make = MODEL_MAKE_HINTS[tokens[0]]
        make_index = -1
        make_len = 0
    elif not make and tokens:
        fuzzy_make = _fuzzy_make_prefix(tokens)
        if fuzzy_make:
            make, make_len, original = fuzzy_make
            make_index = 0
            corrections.append(_correction("make", original, make))
        else:
            make = display_token(tokens[0])
            make_index = 0
            make_len = 1

    remainder = tokens[make_index + make_len :] if make_index >= 0 else tokens
    remainder = [tok for tok in remainder if tok not in RANGE_WORDS]

    model = ""
    model_len = 0
    exact_model = _exact_model_prefix(make, remainder)
    if exact_model:
        model, model_len, _ = exact_model

    if remainder:
        fuzzy_model = _fuzzy_model_prefix(make, remainder)
        if fuzzy_model and (
            not model
            or (fuzzy_model[0] != model and fuzzy_model[1] > model_len)
        ):
            model, model_len, original = fuzzy_model
            corrections.append(_correction("model", original, model))

    if not model and remainder:
        model = display_token(remainder[0])
        model_len = 1
    trim = " ".join(display_token(tok) for tok in remainder[model_len:] if tok not in STOP_WORDS)
    trim = _normalize_trim(make, model, trim)
    corrected_trim = _correct_trim_spelling(make, model, trim)
    if corrected_trim != trim:
        corrections.append(_correction("trim", trim, corrected_trim))
        trim = corrected_trim

    return VehicleQuery(
        raw=raw,
        make=make,
        model=model,
        trim=trim,
        start_year=start_year,
        target_year=target_year,
        max_age=10,
        corrections=corrections,
    )


def _correction(field: str, original: str, corrected: str) -> dict[str, str]:
    return {"field": field, "original": original, "corrected": corrected}


def _exact_make_prefix(tokens: list[str]) -> tuple[str, int, str] | None:
    candidates: list[tuple[str, str, str, int]] = []
    for alias, canonical in MAKE_ALIASES.items():
        candidates.extend(_prefix_candidates(tokens, alias, canonical))
    return _exact_prefix_match(candidates)


def _fuzzy_make_prefix(
    tokens: list[str],
    minimum_alias_words: int = 0,
    exact_prefix: str = "",
) -> tuple[str, int, str] | None:
    candidates: list[tuple[str, str, str, int]] = []
    for alias, canonical in MAKE_ALIASES.items():
        if len(re.findall(r"[a-z0-9]+", alias.lower())) <= minimum_alias_words:
            continue
        if exact_prefix and _comparison_text(alias) == _comparison_text(exact_prefix):
            continue
        # Compare against the alias being evaluated, while returning the
        # canonical make. This lets "Merceds" match "Mercedes" without being
        # unfairly scored against the longer "Mercedes-Benz" output label.
        candidates.extend(_prefix_candidates(tokens, alias, canonical))
    return _best_prefix_match(candidates, margin=0.08, exact_token_tiebreak=False)


def _exact_model_prefix(make: str, tokens: list[str]) -> tuple[str, int, str] | None:
    candidates: list[tuple[str, str, str, int]] = []
    for model_tokens, canonical in model_candidates(make):
        candidates.extend(_prefix_candidates(tokens, " ".join(model_tokens), canonical))
    return _exact_prefix_match(candidates)


def _fuzzy_model_prefix(make: str, tokens: list[str]) -> tuple[str, int, str] | None:
    candidates: list[tuple[str, str, str, int]] = []
    for model_tokens, canonical in model_candidates(make):
        candidates.extend(_prefix_candidates(tokens, " ".join(model_tokens), canonical))
    return _best_prefix_match(
        candidates,
        margin=0.08,
        exact_token_tiebreak=True,
        protect_compact_codes=True,
    )


def _prefix_candidates(
    tokens: list[str],
    comparison: str,
    canonical: str,
) -> list[tuple[str, str, str, int]]:
    """Build candidate input spans and preserve the span actually consumed.

    Vehicle names are routinely entered with spaces/hyphens added or removed
    (``Silverado1500``, ``rav 4``, ``c class``). Comparing normalized
    characters over a small range of input spans handles those forms without
    accidentally consuming a following trim token.
    """
    comparison_words = re.findall(r"[a-z0-9]+", comparison.lower())
    if not comparison_words or not tokens:
        return []
    max_span = min(len(tokens), max(2, len(comparison_words) + 1))
    return [
        (" ".join(tokens[:span]), comparison, canonical, span)
        for span in range(1, max_span + 1)
    ]


def _exact_prefix_match(
    candidates: list[tuple[str, str, str, int]],
) -> tuple[str, int, str] | None:
    matches = [
        (word_count, len(_comparison_text(comparison)), canonical, original)
        for original, comparison, canonical, word_count in candidates
        if _comparison_text(original) == _comparison_text(comparison)
    ]
    if not matches:
        return None
    # Prefer the longest input span, mirroring normal longest-prefix parsing.
    # If two distinct canonical models remain genuinely tied, do not guess.
    matches.sort(reverse=True)
    best_count, best_length = matches[0][:2]
    finalists = {
        canonical
        for count, length, canonical, _ in matches
        if count == best_count and length == best_length
    }
    if len(finalists) != 1:
        return None
    _, _, canonical, original = matches[0]
    return canonical, best_count, _display_phrase(original)


def _best_prefix_match(
    candidates: list[tuple[str, str, str, int]],
    margin: float,
    exact_token_tiebreak: bool,
    protect_compact_codes: bool = False,
) -> tuple[str, int, str] | None:
    by_canonical: dict[str, tuple[int, int, int, float, int, str]] = {}
    for original, comparison, canonical, word_count in candidates:
        left = _comparison_text(original)
        right = _comparison_text(comparison)
        if min(len(left), len(right)) < 3:
            continue
        if protect_compact_codes and _unsafe_compact_correction(left, right):
            continue
        distance = _damerau_levenshtein(left, right)
        length = max(len(left), len(right))
        score = 1 - (distance / length)
        if distance == 0 or distance > _max_typo_distance(length) or score < _minimum_typo_score(length):
            continue
        exact_tokens = _aligned_exact_tokens(original, comparison)
        token_shape = _aligned_token_shape(original, comparison)
        previous = by_canonical.get(canonical)
        rank = (exact_tokens, token_shape, distance, score, word_count, original)
        if previous is None or (
            exact_tokens,
            -distance,
            token_shape,
            score,
            word_count,
        ) > (
            previous[0],
            -previous[2],
            previous[1],
            previous[3],
            previous[4],
        ):
            by_canonical[canonical] = rank
    ranked = sorted(
        [
            (
                exact_tokens,
                token_shape,
                distance,
                score,
                canonical,
                count,
                original,
            )
            for canonical, (exact_tokens, token_shape, distance, score, count, original) in by_canonical.items()
        ],
        key=lambda row: (row[0], -row[2], row[1], row[3], row[5], row[4]),
        reverse=True,
    )
    if not ranked:
        return None
    has_exact_token_evidence = exact_token_tiebreak and ranked[0][0] > 0
    if has_exact_token_evidence:
        ranked = [row for row in ranked if row[0] == ranked[0][0]]
    minimum_distance = min(row[2] for row in ranked)
    ranked = [row for row in ranked if row[2] == minimum_distance]
    if has_exact_token_evidence and ranked[0][1] > 0:
        ranked = [row for row in ranked if row[1] == ranked[0][1]]
    if len(ranked) > 1:
        # Without an exact surviving token there is no principled way to pick
        # between two equally distant catalog models.
        if not has_exact_token_evidence:
            return None
        score_has_margin = ranked[0][3] - ranked[1][3] >= margin
        if not score_has_margin:
            return None
    _, _, _, _, canonical, word_count, original = ranked[0]
    return canonical, word_count, _display_phrase(original)


def _display_phrase(value: str) -> str:
    return " ".join(display_token(token) for token in value.split())


def _aligned_exact_tokens(left: str, right: str) -> int:
    left_tokens = re.findall(r"[a-z0-9]+", left.lower())
    right_tokens = re.findall(r"[a-z0-9]+", right.lower())
    if len(left_tokens) != len(right_tokens):
        return 0
    return sum(a == b for a, b in zip(left_tokens, right_tokens))


def _aligned_token_shape(left: str, right: str) -> int:
    left_tokens = re.findall(r"[a-z0-9]+", left.lower())
    right_tokens = re.findall(r"[a-z0-9]+", right.lower())
    if len(left_tokens) != len(right_tokens):
        return 0
    return sum(len(a) == len(b) for a, b in zip(left_tokens, right_tokens))


def _unsafe_compact_correction(left: str, right: str) -> bool:
    """Protect dense model/trim codes unless the edit is only a transposition.

    In an incomplete catalog, ILX/TLX and 320i/330i are both one edit apart
    but are different real vehicles. Numeric sequences must agree, and compact
    codes may only be rearrangements of the same characters (XES -> XSE).
    """
    if re.findall(r"\d+", left) != re.findall(r"\d+", right):
        return True
    return max(len(left), len(right)) <= 4 and sorted(left) != sorted(right)


def _minimum_typo_score(length: int) -> float:
    if length <= 3:
        return 2 / 3
    if length <= 5:
        return 0.74
    return 0.80


def _max_typo_distance(length: int) -> int:
    return 2 if length >= 10 else 1


def _damerau_levenshtein(left: str, right: str) -> int:
    """Optimal-string-alignment distance with adjacent transposition cost 1."""
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    table = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for index in range(len(left) + 1):
        table[index][0] = index
    for index in range(len(right) + 1):
        table[0][index] = index
    for i, left_char in enumerate(left, start=1):
        for j, right_char in enumerate(right, start=1):
            cost = 0 if left_char == right_char else 1
            table[i][j] = min(
                table[i - 1][j] + 1,
                table[i][j - 1] + 1,
                table[i - 1][j - 1] + cost,
            )
            if i > 1 and j > 1 and left_char == right[j - 2] and left[i - 2] == right_char:
                table[i][j] = min(table[i][j], table[i - 2][j - 2] + 1)
    return table[-1][-1]


def _correct_trim_spelling(make: str, model: str, trim: str) -> str:
    candidates = trim_candidates(make, model)
    if not trim or not candidates:
        return trim

    normalized = _comparison_text(trim)
    for candidate in candidates:
        if normalized == _comparison_text(candidate):
            return candidate

    input_tokens = trim.split()
    phrase_matches: list[tuple[float, str]] = []
    for candidate in candidates:
        candidate_tokens = candidate.split()
        if len(candidate_tokens) != len(input_tokens):
            continue
        changed_pairs = [
            (left, right)
            for left, right in zip(input_tokens, candidate_tokens)
            if _comparison_text(left) != _comparison_text(right)
        ]
        if not changed_pairs or any(min(len(_comparison_text(left)), len(_comparison_text(right))) < 4 for left, right in changed_pairs):
            continue
        if any(
            _unsafe_compact_correction(_comparison_text(left), _comparison_text(right))
            for left, right in changed_pairs
        ):
            continue
        candidate_key = _comparison_text(candidate)
        distance = _damerau_levenshtein(normalized, candidate_key)
        length = max(len(normalized), len(candidate_key))
        if distance <= _max_typo_distance(length):
            phrase_matches.append((1 - (distance / length), candidate))

    phrase_matches.sort(reverse=True)
    if phrase_matches and phrase_matches[0][0] >= _minimum_typo_score(max(len(normalized), 1)):
        second = phrase_matches[1][0] if len(phrase_matches) > 1 else 0.0
        if phrase_matches[0][0] - second >= 0.08:
            return phrase_matches[0][1]

    vocabulary = sorted({token for candidate in candidates for token in candidate.split()})
    corrected_tokens = list(input_tokens)
    for index, token in enumerate(input_tokens):
        token_key = _comparison_text(token)
        if len(token_key) < 4:
            continue
        ranked = []
        for candidate in vocabulary:
            candidate_key = _comparison_text(candidate)
            if _unsafe_compact_correction(token_key, candidate_key):
                continue
            distance = _damerau_levenshtein(token_key, candidate_key)
            length = max(len(token_key), len(candidate_key))
            if distance <= _max_typo_distance(length):
                ranked.append((1 - (distance / length), candidate))
        ranked.sort(reverse=True)
        if not ranked or ranked[0][0] < _minimum_typo_score(len(token_key)):
            continue
        second = ranked[1][0] if len(ranked) > 1 else 0.0
        if ranked[0][0] - second >= 0.1:
            corrected_tokens[index] = ranked[0][1]
    return " ".join(corrected_tokens)


def _comparison_text(value: str) -> str:
    return "".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def _range_year(lower: str) -> int | None:
    match = re.search(r"\b(after|since|from|newer than|newer-than)\s+(19\d{2}|20\d{2})\b", lower)
    if not match:
        return None
    return int(match.group(2))


def _split_attached_terms(text: str) -> str:
    replacements = {
        r"\bx\s+s\s+e\b": "xse",
        r"\bx\s+l\s+e\b": "xle",
        r"\bl\s+e\b": "le",
        r"\bs\s+e\b": "se",
        r"\bf\s*[- ]?\s*(150|250|350)\b": r"f-\1",
        r"\b(cr|hr)\s*-?\s*v\b": r"\1-v",
        r"\b(cx)\s*-?\s*(30|5|50|70|90)\b": r"\1-\2",
        r"\b(mx)\s*-?\s*5\b": r"mx-5",
        r"(?<!mazda )\bmazda\s*([36])\b": r"mazda mazda\1",
        r"\bmodel\s*([s3xy])\b": r"model \1",
        r"\bcyber\s*truck\b": "cybertruck",
        r"\bioniq\s*([569])\b": r"ioniq \1",
        r"\bid\s*\.?\s*4\b": "id.4",
        r"\bxdrive\s*(\d{2,3}i?)\b": r"xdrive \1",
        r"\bamg\s+([ces])(\d{2})\b": r"\1 \2 amg",
        r"\b(m[2345])competition\b": r"\1 competition",
        r"\b(m[2345])comp\b": r"\1 competition",
        r"\b(lc|ls|lx|rx|gx|nx|tx|is|es|rc)(\d{3}h?)\b": r"\1 \2",
        r"\b(\d{3})(i|e)\b": r"\1 \2",
        r"\b([ces])(\d{2,3})\b": r"\1 \2",
        r"\b(gl[abces])(\d{2,3})\b": r"\1 \2",
        r"\b(cla|cle)(\d{2,3})\b": r"\1 \2",
        r"\b(g)(\d{3})\b": r"\1 \2",
        r"\bx\s+drive\b": "xdrive",
        r"\bxdrive\b": "xdrive",
    }
    result = text
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result)
    return result


def _normalize_trim(make: str, model: str, trim: str) -> str:
    parts = trim.split()
    if not parts:
        return trim

    model_parts = model.split()
    if model_parts and [part.lower() for part in parts[: len(model_parts)]] == [part.lower() for part in model_parts]:
        parts = parts[len(model_parts) :]

    if make == "Mercedes-Benz" and model in MERCEDES_CLASS_LETTERS and parts[:1] == [MERCEDES_CLASS_LETTERS[model]]:
        parts = parts[1:]

    if make == "BMW" and len(parts) >= 2 and parts[0].isdigit() and parts[1].lower() in {"i", "e"}:
        parts = [parts[0] + parts[1].lower(), *parts[2:]]
    if make == "BMW" and len(parts) >= 2 and parts[0].lower() == "xdrive" and re.match(r"^\d{2,3}i?$", parts[1].lower()):
        parts = ["xDrive" + parts[1].lower(), *parts[2:]]
    if make == "Mercedes-Benz" and model == "GLE" and [part.lower() for part in parts] == ["450"]:
        parts = ["450", "4MATIC"]

    return " ".join(parts)
