"""Fetch the pinned public inputs for rebuilding the workbook-derived Database exercises."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from http.client import IncompleteRead
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


def fetch(task):
    destination, url, expected = task
    if destination.exists():
        if sha256(destination.read_bytes()).hexdigest() == expected:
            return
        raise ValueError(f"Existing source differs from the pinned revision: {destination}")
    for attempt in range(4):
        try:
            with urlopen(url, timeout=40) as response:
                data = response.read()
            break
        except (URLError, OSError, IncompleteRead) as error:
            if isinstance(error, HTTPError) and error.code < 500 and error.code not in (408, 429):
                raise
            if attempt == 3:
                raise
            sleep(2 ** attempt)
    if sha256(data).hexdigest() != expected:
        raise ValueError(f"Source differs from the recorded hash: {url}")
    with NamedTemporaryFile(dir=destination.parent, delete=False) as staging:
        staging.write(data)
    Path(staging.name).replace(destination)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("ids", type=int, nargs="*")
    args = parser.parse_args()
    manifest = json.loads(Path(__file__).with_name("database_authoring_sources.json").read_text())
    selected = args.ids or sorted(map(int, manifest["problems"]))
    statements = args.destination / "doocs"
    oracles = args.destination / "oracles"
    statements.mkdir(parents=True, exist_ok=True)
    oracles.mkdir(parents=True, exist_ok=True)
    tasks = []
    for key in selected:
        row = manifest["problems"][str(key)]
        source = "https://raw.githubusercontent.com/doocs/leetcode/" + manifest["doocsRevision"] + "/"
        tasks.append((statements / f"{key}.md", source + quote(row["doocsPath"]), row["doocsSHA256"]))
        if "walkcccPath" in row:
            oracle = "https://raw.githubusercontent.com/walkccc/LeetCode/" + manifest["walkcccRevision"] + "/"
            tasks.append((oracles / f"{key}.sql", oracle + quote(row["walkcccPath"]), row["walkcccSHA256"]))
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(fetch, tasks))
    print(f"Verified {len(tasks)} source files for {len(selected)} problems in {args.destination}")


if __name__ == "__main__":
    main()
