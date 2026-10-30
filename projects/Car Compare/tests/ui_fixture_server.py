"""Local-only synthetic report preview. No marketplace or model calls."""
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["CAR_COMPARE_CACHE_ENABLED"] = "0"

import app
from car_compare import collector
from car_compare.collection_scope import verified_scope
from car_compare.models import Listing
from car_compare.generation_impact import GenerationResearchConfig, GenerationResearchManager


def fixture(request):
    current_year = app.datetime.now().year
    missing_baseline = request.make == "Toyota"
    rows = []
    for age in range(1, 4):
        for index in range(3):
            rows.append(Listing(source="synthetic_ui_test", year=current_year-age,
                                price=(90000 if not missing_baseline else 40000)-age*5000+index*1000,
                                title=f"Used {current_year-age} {request.display_name}", condition="used",
                                vin=f"fixture-{age}-{index}", scope=verified_scope(request)).to_dict())
    manifest = [{"id": "new", "year": current_year, "condition": "new", "status": "failed" if missing_baseline else "successful", "captured_at": app.datetime.now().timestamp()}]
    evidence = [] if missing_baseline else [{
        "source": "synthetic_ui_test", "year": current_year, "condition": "new", "num_found": 20,
        "price_stats": {"count": 20, "median": 100000}, "price_bins": [],
        "scope": verified_scope(request, partition_manifest=manifest, partition_key="new"),
    }]
    return {"query": request.raw, "status": "partial", "listings": rows,
            "evidence": evidence, "partition_manifest": manifest, "msrp": None,
            "sources": [{"source": "synthetic_ui_test", "status": "partial"}],
            "notes": ["SYNTHETIC UI TEST ONLY. These prices are not market observations."]}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="car-compare-ui-") as directory:
        collector._dry_run_result = fixture
        config = collector.CollectorConfig(root=Path(directory), cache_enabled=False, dry_run=True)
        app.COLLECTOR = collector.CollectionManager(config)
        app.COLLECTOR.availability = lambda: {"available": True, "dryRun": True, "message": "Synthetic UI test only"}
        app.GENERATION_RESEARCH = GenerationResearchManager(GenerationResearchConfig(root=Path(directory), dry_run=True, cache_enabled=False))
        app.GENERATION_RESEARCH.availability = lambda: {"available": False, "message": "Disabled in synthetic UI preview"}
        app.main()
