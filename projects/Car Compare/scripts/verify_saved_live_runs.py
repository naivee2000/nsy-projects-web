#!/usr/bin/env python3
"""Read-only price/scope checks against the same session's saved browser cards.

Does not contact marketplaces, refresh timestamps, or open a runtime cache.
"""
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from car_compare.collection_scope import scope_is_verified
from car_compare.collector import listings_from_result
from car_compare.depreciation import build_report
from car_compare.models import MSRP
from car_compare.parser import parse_vehicle_query


def detail_key(url):
    parts = urlsplit(url)
    return (parts.hostname or "").removeprefix("www."), parts.path.rstrip("/")


def card_price(text):
    for line in text.splitlines():
        if re.search(r"msrp|month|payment|lease|finance|down|fees?", line, re.I):
            continue
        match = re.fullmatch(r"\s*\$?\s*(\d{1,3}(?:,\d{3})+)(?:\.00)?\s*", line)
        if match:
            return float(match[1].replace(",", ""))
    return None


def aggregate_checks(report, snapshots):
    """Independent pooling check via connected overlapping whole-bin intervals."""
    used=[snapshots[item["index"]] for item in report["evidence"]["aggregateDiagnostics"] if item["status"]=="used"]
    checks=[]
    for bucket in report["buckets"]:
        if not bucket["aggregate_count"]:
            continue
        rows=[row for row in used if row["year"]==bucket["model_year"] and (row["condition"]=="new")== (bucket["age"]==0)]
        unique={json.dumps([row["source"],row["year"],row["condition"],row.get("scope",{}).get("partition_key")]):row for row in rows}
        rows=list(unique.values())
        valid=bool(rows) and sum(row["price_stats"]["count"] for row in rows)==bucket["aggregate_count"]
        if len(rows)==1:
            valid=valid and round(rows[0]["price_stats"]["median"],2)==bucket["market_median"]
        elif rows:
            intervals=sorted((item["lower"],item["upper"],item["count"]) for row in rows for item in row.get("price_bins",[]) if item["count"]>0)
            valid=valid and all(sum(item["count"] for item in row.get("price_bins",[]))==row["price_stats"]["count"] for row in rows)
            groups=[]
            for low,high,count in intervals:
                if groups and low<groups[-1][1]:
                    groups[-1][1]=max(high,groups[-1][1]);groups[-1][2]+=count
                else:
                    groups.append([low,high,count])
            target=bucket["aggregate_count"]/2
            cumulative=0
            for low,high,count in groups:
                if cumulative+count>=target:
                    estimate=round(low+(high-low)*(target-cumulative)/count,2) if (high-low)/((high+low)/2)<=.2 else None
                    valid=valid and bucket["median_interval"]==[low,high] and bucket["market_median"]==estimate
                    break
                cumulative+=count
        checks.append({"year":bucket["model_year"],"population":bucket["population_scope"],"matched":bool(valid)})
    return checks


def verify(directory):
    output = []
    for job_dir in sorted((directory / "jobs").iterdir()):
        path = job_dir / "collector_result.json"
        if not path.exists():
            continue
        result = json.loads(path.read_text())
        request = parse_vehicle_query(result["query"])
        report = build_report(request, listings_from_result(result), MSRP(0,"Reference","reference",""), aggregate_snapshots=result.get("evidence",[]))
        cards = {}
        for capture_path in job_dir.glob("host_chrome_*.json"):
            capture = json.loads(capture_path.read_text())
            for index in capture.get("scope_validation",{}).get("accepted_pages",[]):
                page = capture["pages"][index]
                for card in page.get("cards",[]):
                    cards.setdefault(detail_key(card["url"]),[]).append(card["text"])
        for capture_path in job_dir.glob("browser_capture_*.json"):
            capture = json.loads(capture_path.read_text())
            for page in capture.get("page_records",[]):
                if not scope_is_verified(page.get("scope")):
                    continue
                for card in page.get("cards",[]):
                    cards.setdefault(detail_key(card["url"]),[]).append(card["text"])
        checks = []
        for row in report["listings"]:
            if "facet" in row["source"] or "aggregate" in row["source"]:
                continue
            texts = [text for url in row.get("url","").split(" | ") for text in cards.get(detail_key(url),[])]
            checks.append({"source":row["source"],"year":row["year"],"price":row["price"],
                           "scope_verified":scope_is_verified(row.get("scope"),request),
                           "card_price_matches":any(card_price(text)==row["price"] and re.search(rf"\b{row['year']}\b",text) for text in texts)})
        source_path = job_dir / "source-comparison.json"
        comparisons = json.loads(source_path.read_text()) if source_path.exists() else []
        pooled_checks=aggregate_checks(report,result.get("evidence",[]))
        aggregate_matches = sum(item["status"]=="matched" for item in comparisons)
        matched = sum(item["scope_verified"] and item["card_price_matches"] for item in checks)
        errors = [item for item in checks if not item["scope_verified"] or not item["card_price_matches"]]
        row = {"query":request.raw,"readiness":report["summary"]["readiness"],"priced_years":report["summary"]["pricedYearCount"],
               "baseline_year":report["summary"]["baselineModelYear"],"baseline_price":report["buckets"][0]["market_median"],
               "browser_prices_matched":matched,"browser_prices_checked":len(checks),"browser_mismatches":errors,
               "aggregate_partitions_matched":aggregate_matches,"aggregate_partitions_checked":len(comparisons),
               "aggregate_report_checks":pooled_checks,
               "source_outcomes":[{key:item.get(key) for key in ("source","status","stop_reason")} for item in result.get("sources",[])],
               "qualified_result_verified":bool(report["summary"]["pricedYearCount"] and (matched or aggregate_matches or pooled_checks) and not errors and all(item["status"]=="matched" for item in comparisons) and all(item["matched"] for item in pooled_checks))}
        output.append(row)
    return output


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.directory),indent=2))
