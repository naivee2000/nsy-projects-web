from pathlib import Path


def test_start_command_binds_only_to_loopback():
    script = (Path(__file__).resolve().parents[1] / "run_local.sh").read_text()
    assert "--host 127.0.0.1" in script
    assert "--host 0.0.0.0" not in script


def test_no_deployment_configuration_exists():
    root = Path(__file__).resolve().parents[1]
    assert not (root / ".openai" / "hosting.json").exists()
    assert not list(root.rglob("*cloudflare*"))
    assert not list(root.rglob("*pm2*"))

