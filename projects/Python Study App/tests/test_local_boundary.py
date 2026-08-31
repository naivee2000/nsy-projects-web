from pathlib import Path


def test_start_command_binds_only_to_loopback():
    script = (Path(__file__).resolve().parents[1] / "run_local.sh").read_text()
    assert "--host 127.0.0.1" in script
    assert "--host 0.0.0.0" not in script


def test_deployment_template_stays_loopback_and_uses_persistent_data():
    root = Path(__file__).resolve().parents[1]
    assert not (root / ".openai" / "hosting.json").exists()
    assert not list(root.rglob("*cloudflare*"))
    template = (root / "ops" / "pm2-python-study.example.cjs").read_text()
    assert '"127.0.0.1"' in template
    assert '"0.0.0.0"' not in template
    assert "CODE_PRACTICE_DATA_DIR" in template
    assert "CODE_PRACTICE_SEED_DB" in template
    assert "CODE_PRACTICE_SESSION_SECRET" in template
