"""Tests des sous-commandes et du contrat CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import graph

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "graph.py"


def test_cmd_build_stats(workspace):
    result = graph.cmd_build(workspace)
    assert result["nodes"]["normative"] >= 2
    assert result["nodes"]["memory"] == 3
    assert result["nodes"]["content"] >= 2
    assert result["edges"]["at-ref"] >= 1
    assert result["edges"]["link"] >= 1
    assert result["edges"]["affinity"] >= 1
    assert result["broken_count"] == len(result["broken"])
    assert result["broken_count"] >= 2


def test_cmd_build_ecrit_le_cache(workspace):
    graph.cmd_build(workspace)
    cache = workspace / ".claude" / "driven" / "graph.json"
    assert cache.is_file()
    data = json.loads(cache.read_text(encoding="utf-8"))
    assert "nodes" in data and "edges" in data
    assert isinstance(list(data["nodes"].values())[0], dict)


def test_cli_build_emet_du_json(workspace):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "build", "--scope", str(workspace)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["nodes"]["memory"] == 3
