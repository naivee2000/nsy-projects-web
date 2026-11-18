"""Read published table examples from the Doocs Database snapshot used for the study workbook.

This is an offline authoring utility. Website submissions only use packaged fixtures.
"""

import html
from datetime import datetime
import re
from pathlib import Path


def plain(raw):
    return html.unescape(re.sub(r"</?[a-zA-Z][^>]*>", "", raw)).replace("\xa0", " ").strip()


def grids(raw):
    block = []
    for line in (plain(raw) + "\n").split("\n"):
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            values = [v.strip() for v in line[1:-1].split("|")]
            if any(v.strip("-: ") for v in values):
                block.append(values)
        elif block and not re.fullmatch(r"[+\-\s]+", line):
            yield block
            block = []
    if block:
        yield block


TYPES = {
    "int": "INT",
    "integer": "INT",
    "bigint": "BIGINT",
    "varchar": "VARCHAR(512)",
    "text": "TEXT",
    "enum": "VARCHAR(100)",
    "decimal": "DECIMAL(22,6)",
    "float": "DECIMAL(22,6)",
    "bool": "BOOLEAN",
    "date": "DATE",
    "datetime": "DATETIME",
    "time": "TIME",
    "id": "INT",
}


def typed(value, kind):
    if value.lower() in {"null", "none"}:
        return None
    if kind in {"BOOLEAN", "INT", "BIGINT"}:
        if value.lower() in ("true", "false"):
            return int(value.lower() == "true")
        return int(value)
    if kind.startswith("DECIMAL"):
        return float(value)
    if kind == "DATE" and "/" in value:
        fmt = "%Y/%m/%d" if len(value.split("/")[0]) == 4 else "%m/%d/%Y"
        return datetime.strptime(value, fmt).date().isoformat()
    return value


def read_source(path):
    raw = Path(path).read_text()
    desc = raw.split("<!-- description:start -->")[1].split("<!-- description:end -->")[0]
    heading = re.search(r"<strong[^>]*>\s*Example\s*\d*\s*:", desc, re.I)
    first = desc[: heading.start()]
    schema = {}
    for match in re.finditer(r"<pre[^>]*>(.*?)</pre>", first, re.S):
        names = re.findall(
            r"(?:Table|View)\s*:?\s+([\w]+)\s*:?(?:\n|$)", plain(first[: match.start()]), re.I
        )
        table = names[-1] if names else None
        for grid in grids(match[1]):
            cols = [(name, TYPES[kind.lower()]) for name, kind in grid if kind.lower() in TYPES]
            if Path(path).stem == "2687":
                cols = [(k, "VARCHAR(64)" if k == "bike_number" else t) for k, t in cols]
            if cols and table:
                schema[table] = cols
    examples = []
    sections = re.split(r"<strong[^>]*>\s*Example\s*\d*\s*:", desc[heading.start() :], flags=re.I)[1:]
    for section in sections:
        text = plain(re.sub(r"</(?:p|pre|div)>", "\n", section, flags=re.I))
        if not re.search(r"^\s*Output\s*:?\s*$", text, re.I | re.M):
            continue
        inp, out = re.split(r"^\s*Output\s*:?\s*$", text, maxsplit=1, flags=re.I | re.M)
        result = next(grids(re.split(r"Explanation\s*:", out, flags=re.I)[0]), None)
        text_tables = list(grids(inp))
        if not result or len(text_tables) != len(schema):
            continue
        tables = {}
        for n, grid in enumerate(text_tables):
            similar = {
                name
                for name, cols in schema.items()
                if {s.casefold() for s, _ in cols} == {s.casefold() for s in grid[0]}
            }
            if list(schema)[n] in similar:
                name = list(schema)[n]
            elif len(similar) == 1:
                name = next(iter(similar))
            else:
                raise ValueError((path, "example columns", grid[0], schema))
            index = {s.casefold(): i for i, s in enumerate(grid[0])}
            data = []
            for row in grid[1:]:
                if Path(path).stem in {"3150", "2738"} and not row[0] and data:
                    data[-1][1] += " " + row[1]
                else:
                    data.append([typed(row[index[k.casefold()]], dt) for k, dt in schema[name]])
            tables[name] = data
        examples.append({"tables": tables, "columns": result[0], "output": result[1:]})
    return schema, examples
