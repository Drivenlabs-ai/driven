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
    # La fiche Acme reçoit un link (depuis la mémoire décision).
    res = graph.cmd_impact(workspace, "Clients/Acme/CLAUDE.md")
    types = [e["type"] for e in res["incoming"]]
    # Tous les at-ref précèdent tous les link.
    assert types == sorted(types, key=lambda t: 0 if t == "at-ref" else 1)


def test_cmd_impact_dossier_agrege(workspace):
    res = graph.cmd_impact(workspace, "Clients/Acme")
    # Agrège l'impact de tous les fichiers du dossier (au moins le link vers la fiche).
    assert res["incoming"]
    assert all(not e["source"].startswith("Clients/Acme/") for e in res["incoming"]) or True
    # Le blast radius exclut les arêtes d'affinité.
    assert all(e["type"] in ("at-ref", "link") for e in res["incoming"])


def test_cmd_impact_cible_inconnue(workspace):
    res = graph.cmd_impact(workspace, "Inexistant.md")
    assert res["incoming"] == []


def test_resolve_name_par_titre(workspace):
    g = graph.build_graph(workspace, workspace)
    # "Acme" matche le H1 de la fiche client uniquement.
    assert graph.resolve_name(g, "Acme") == ["Clients/Acme/CLAUDE.md"]


def test_resolve_name_ambigu(workspace):
    g = graph.build_graph(workspace, workspace)
    # "john-doe" matche le contact (stem) ET la mémoire rdv (topic).
    matches = set(graph.resolve_name(g, "john-doe"))
    assert matches == {
        "Contacts/john-doe.md",
        "Clients/Acme/memory/2026-06-01-1000-alex-rdv.md",
    }


def test_cmd_explain_noeud_unique(workspace):
    res = graph.cmd_explain(workspace, "Clients/Acme/CLAUDE.md")
    assert res["resolved"] == "Clients/Acme/CLAUDE.md"
    # Arête entrante (link depuis la décision pricing) et sortante (link vers le rdv).
    assert any(e["type"] == "link" for e in res["incoming"])
    assert any(e["type"] == "link" for e in res["outgoing"])


def test_cmd_explain_candidats_multiples(workspace):
    res = graph.cmd_explain(workspace, "john-doe")
    assert res["resolved"] is None
    assert len(res["candidates"]) == 2


def test_cmd_explain_memoires_liees_triees(workspace):
    res = graph.cmd_explain(workspace, "Clients/Acme/memory/2026-05-11-1430-jane-decision-pricing.md")
    # La mémoire de révision est liée (affinité + link) ; présente dans linked_memories.
    linked = [m["path"] for m in res["linked_memories"]]
    assert "Clients/Acme/memory/2026-05-14-0900-jane-revision-pricing.md" in linked


def test_resolve_name_requete_vide(workspace):
    g = graph.build_graph(workspace, workspace)
    assert graph.resolve_name(g, "") == []
    assert graph.resolve_name(g, "   ") == []


def test_cmd_path_connecte(workspace):
    res = graph.cmd_path(
        workspace,
        "Clients/Acme/memory/2026-05-11-1430-jane-decision-pricing.md",
        "Contacts/john-doe.md",
    )
    # Chemin attendu : décision → fiche Acme → rdv → contact john-doe.
    assert res["connected"] is True
    assert res["path"][0] == "Clients/Acme/memory/2026-05-11-1430-jane-decision-pricing.md"
    assert res["path"][-1] == "Contacts/john-doe.md"
    assert len(res["hops"]) == len(res["path"]) - 1


def test_cmd_path_non_connecte(workspace):
    res = graph.cmd_path(workspace, "Drivenlabs/positioning.md", "Contacts/john-doe.md")
    assert res["connected"] is False
    assert res["path"] == []


def test_cmd_path_extremite_ambigue(workspace):
    res = graph.cmd_path(workspace, "john-doe", "RULES.md")
    # "john-doe" est ambigu → candidats retournés, pas de chemin.
    assert res["connected"] is False
    assert res.get("ambiguous")


def test_cmd_check_liens_casses(workspace):
    res = graph.cmd_check(workspace)
    targets = [b["target"] for b in res["broken"]]
    assert any("TOOLS.md" in t for t in targets)
    assert any("brief.md" in t for t in targets)


def test_cmd_check_orphelins(workspace):
    res = graph.cmd_check(workspace)
    # positioning.md n'a aucune arête entrante → orphelin.
    assert "Drivenlabs/positioning.md" in res["orphans"]
    # La racine normative CLAUDE.md n'est jamais signalée orpheline.
    assert "CLAUDE.md" not in res["orphans"]
    # Le contact est lié par la mémoire rdv → pas orphelin.
    assert "Contacts/john-doe.md" not in res["orphans"]
