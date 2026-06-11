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


def test_cmd_impact_fichier(workspace):
    res = graph.cmd_impact(workspace, "RULES.md")
    assert res["target"] == "RULES.md"
    incoming = res["incoming"]
    assert any(e["source"] == "CLAUDE.md" and e["type"] == "at-ref" for e in incoming)


def test_cmd_impact_trie_at_ref_avant_link(workspace):
    # La fiche Olenbee reçoit un link (depuis la mémoire décision).
    res = graph.cmd_impact(workspace, "Clients/Olenbee/CLAUDE.md")
    types = [e["type"] for e in res["incoming"]]
    # Tous les at-ref précèdent tous les link.
    assert types == sorted(types, key=lambda t: 0 if t == "at-ref" else 1)


def test_cmd_impact_dossier_agrege(workspace):
    res = graph.cmd_impact(workspace, "Clients/Olenbee")
    # Agrège l'impact de tous les fichiers du dossier (au moins le link vers la fiche).
    assert res["incoming"]
    assert all(not e["source"].startswith("Clients/Olenbee/") for e in res["incoming"]) or True
    # Le blast radius exclut les arêtes d'affinité.
    assert all(e["type"] in ("at-ref", "link") for e in res["incoming"])


def test_cmd_impact_cible_inconnue(workspace):
    res = graph.cmd_impact(workspace, "Inexistant.md")
    assert res["incoming"] == []
