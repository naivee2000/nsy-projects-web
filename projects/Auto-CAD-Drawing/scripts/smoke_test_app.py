#!/usr/bin/env python3
"""Smoke-test a running Auto CAD Drawing API."""

from __future__ import annotations

import argparse
import json
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_PDF = ROOT / "液位遥测系统" / "CPX26051 600吨起重船完工图.pdf"
SUPPORTED_CPX25034_PDF = ROOT / "液货系统" / "CPX25034  7300DWT 化学品船DJC-L型压力、温度、液位测量报警系统、可燃气体探测报警系统w完工图 2025.9 Model (1).pdf"
REFERENCE_ONLY_CPX25034_PDF = ROOT / "液货系统" / "7300液货补充协议-signed(2).pdf"
UNSUPPORTED_PDF = ROOT / "电动阀门遥控系统" / "CPX25063  6250DWT（2#）普通干货船 阀门遥控系统完工图.pdf"


def request_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def multipart_body(field_name: str, file_path: Path) -> tuple[bytes, str]:
    boundary = "----AutoCadSmokeBoundary"
    content = file_path.read_bytes()
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8")
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return header + content + footer, f"multipart/form-data; boundary={boundary}"


def post_pdf(base_url: str, file_path: Path) -> tuple[int, dict]:
    body, content_type = multipart_body("files", file_path)
    request = urllib.request.Request(
        f"{base_url}/api/jobs",
        data=body,
        headers={"Content-Type": content_type},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        payload = json.loads(exc.read().decode("utf-8"))
        return exc.code, payload


def download_and_test_zip(base_url: str, download_url: str, required: set[str]) -> None:
    with tempfile.NamedTemporaryFile(suffix=".zip") as handle:
        with urllib.request.urlopen(f"{base_url}{download_url}", timeout=120) as response:
            handle.write(response.read())
            handle.flush()
        with zipfile.ZipFile(handle.name) as archive:
            bad = archive.testzip()
            if bad:
                raise AssertionError(f"ZIP has a bad member: {bad}")
            names = set(archive.namelist())
            missing = sorted(required - names)
            if missing:
                raise AssertionError(f"ZIP missing required files: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8008")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    health = request_json(f"{base_url}/api/health")
    assert health["status"] == "ok", health
    print("OK: health")

    readiness = request_json(f"{base_url}/api/readiness")
    assert readiness["status"] == "ready", readiness
    assert any(item["name"] == "baseline_outputs" and item["ok"] for item in readiness["checks"]), readiness
    print("OK: readiness")

    capabilities = request_json(f"{base_url}/api/capabilities")
    assert "CPX26051" in capabilities["supported_projects"], capabilities
    assert "CPX25034" in capabilities["supported_projects"], capabilities
    assert "level_sensor" in capabilities["supported_generators"], capabilities
    assert "STK333-AR2" in capabilities["supported_sensor_models"], capabilities
    assert "CPX25063" in capabilities["known_unsupported_projects"], capabilities
    print("OK: capabilities")

    status, supported_payload = post_pdf(base_url, SUPPORTED_PDF)
    assert status == 200, supported_payload
    manifest = supported_payload["manifest"]
    assert manifest["project_id"] == "CPX26051", manifest
    assert manifest["mode"] == "level_sensor", manifest
    assert manifest["primary_sensor_model"] == "STK333-AR2", manifest
    download_and_test_zip(
        base_url,
        supported_payload["download_url"],
        {
            "generated/DJC-26051-04-01-page-15.dxf",
            "generated/DJC-26051-04-01-page-16.dxf",
            "generated/DJC-26051-04-01-page-17.dxf",
            "generated/DJC-26051-05-01-page-01.dxf",
            "manifest.json",
        },
    )
    print("OK: supported CPX26051 upload and ZIP")

    status, cpx25034_payload = post_pdf(base_url, SUPPORTED_CPX25034_PDF)
    assert status == 200, cpx25034_payload
    cpx25034_manifest = cpx25034_payload["manifest"]
    assert cpx25034_manifest["project_id"] == "CPX25034", cpx25034_manifest
    assert cpx25034_manifest["mode"] == "level_sensor", cpx25034_manifest
    assert cpx25034_manifest["primary_sensor_model"] == "STK333-AR2", cpx25034_manifest
    download_and_test_zip(
        base_url,
        cpx25034_payload["download_url"],
        {
            "generated/DJC-25034-06-02-page-43.dxf",
            "manifest.json",
        },
    )
    print("OK: supported CPX25034 STK333-AR2 upload and ZIP")

    jobs = request_json(f"{base_url}/api/jobs")
    assert any(job["job"] == supported_payload["job"] for job in jobs["jobs"]), jobs
    assert any(job["job"] == cpx25034_payload["job"] for job in jobs["jobs"]), jobs
    print("OK: job history")

    status, reference_only_payload = post_pdf(base_url, REFERENCE_ONLY_CPX25034_PDF)
    assert status == 422, reference_only_payload
    assert reference_only_payload["detail"]["analysis"]["status"] == "unsupported", reference_only_payload
    print("OK: CPX25034 reference-only upload blocked")

    status, unsupported_payload = post_pdf(base_url, UNSUPPORTED_PDF)
    assert status == 422, unsupported_payload
    analysis = unsupported_payload["detail"]["analysis"]
    assert analysis["uploads"][0]["project_id"] == "CPX25063", analysis
    assert analysis["status"] == "unsupported", analysis
    print("OK: unsupported CPX25063 blocked")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
