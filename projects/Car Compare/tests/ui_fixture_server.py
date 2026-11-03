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


class PreviewHandler(app.CarCompareHandler):
    def do_GET(self):
        if self.path == "/mobile-preview":
            body = b'<!doctype html><title>Isolated 390px mobile preview</title><iframe title="Mobile Car Compare" src="/" style="width:390px;height:844px;border:1px solid #888"></iframe>'
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


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
    if request.make == "Ford":
        rows, evidence = [], []
    return {"query": request.raw, "status": "partial", "listings": rows,
            "evidence": evidence, "partition_manifest": manifest, "msrp": None,
            "sources": [{"source": "synthetic_ui_test", "status": "partial"}],
            "notes": ["SYNTHETIC UI TEST ONLY. These prices are not market observations."]}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="car-compare-ui-") as directory:
        app.CarCompareHandler = PreviewHandler
        collector._dry_run_result = fixture
        config = collector.CollectorConfig(root=Path(directory), cache_enabled=False, dry_run=True)
        app.COLLECTOR = collector.CollectionManager(config)
        app.COLLECTOR.availability = lambda: {"available": True, "dryRun": True, "message": "Synthetic UI test only"}
        app.GENERATION_RESEARCH = GenerationResearchManager(GenerationResearchConfig(root=Path(directory), dry_run=True, cache_enabled=False))
        app.GENERATION_RESEARCH.availability = lambda: {"available": True, "dryRun": True, "message": "Synthetic UI scenario only"}
        app.main()
