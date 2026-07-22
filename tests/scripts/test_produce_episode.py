from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import scripts.produce_episode as produce_episode


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "produce_episode.py"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "episode_package" / "episode.json"


def _run(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )


def test_help_is_side_effect_free(tmp_path: Path) -> None:
    completed = _run("--help", cwd=tmp_path)

    assert completed.returncode == 0
    assert "--episode" in completed.stdout
    assert not (tmp_path / "storage").exists()


def test_validation_only_json_success(tmp_path: Path) -> None:
    completed = _run("--episode", str(FIXTURE), "--validate-only", "--json", cwd=tmp_path)

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "success"
    assert result["mode"] == "validation_only"
    assert result["scene_count"] == 9
    assert not (tmp_path / "storage").exists()


def test_invalid_package_returns_stable_json_without_traceback(tmp_path: Path) -> None:
    package_root = tmp_path / "episode"
    shutil.copytree(FIXTURE.parent, package_root)
    manifest = package_root / "episode.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["frames"][0]["speaker"] = "invalid"
    manifest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    completed = _run("--episode", str(manifest), "--json", cwd=tmp_path)

    assert completed.returncode != 0
    result = json.loads(completed.stdout)
    assert result["status"] == "error"
    assert result["error_type"] == "validation_error"
    assert result["errors"][0]["path"].startswith("$.frames")
    assert "Traceback" not in completed.stdout + completed.stderr
    assert not (tmp_path / "storage").exists()


def test_argument_errors_use_nonzero_exit_and_json(tmp_path: Path) -> None:
    completed = _run("--json", cwd=tmp_path)

    assert completed.returncode == 2
    assert json.loads(completed.stdout)["error_type"] == "argument_error"


def test_verify_package_failure_uses_stable_json_without_traceback(tmp_path: Path) -> None:
    completed = _run("--verify-package", str(tmp_path / "missing"), "--json", cwd=tmp_path)

    assert completed.returncode == 1
    result = json.loads(completed.stdout)
    assert result["status"] == "error"
    assert result["package_validation_status"] == "failed"
    assert "Traceback" not in completed.stdout + completed.stderr


def test_invalid_package_never_reaches_staging_or_renderer(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    manifest = tmp_path / "episode.json"
    manifest.write_text("{}", encoding="utf-8")

    def unexpected_stage(*args, **kwargs):
        raise AssertionError("staging/render boundary must not be reached")

    monkeypatch.setattr(produce_episode, "stage_episode_package", unexpected_stage)
    monkeypatch.setattr(
        sys,
        "argv",
        ["produce_episode.py", "--episode", str(manifest), "--json"],
    )

    assert produce_episode.main() == 1
    result = json.loads(capsys.readouterr().out)
    assert result["error_type"] == "validation_error"
