"""Tests du pont vers la mémoire native : --project sur search/graph + liens cross-tree."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import graph
import native_memory_dir as nmd
import search_memories

_MEMORY = (
    "---\ndate: 2026-05-11\ntime: \"1430\"\ntype: decision\n"
    "topic: pricing-olenbee\nkeywords:\n  - olenbee\n  - pricing\n  - devis\n---\n\n"
    "# Décision pricing\n\n## Contexte\nPricing Olenbee.\n\n## Notes\nAligné à 8K.\n"
)


def _seed_native_memory(tmp_path: Path, monkeypatch) -> Path:
    """Redirige ~/.claude/projects vers tmp et retourne un repo prêt à recevoir sa mémoire."""
    projects = tmp_path / "home" / ".claude" / "projects"
    projects.mkdir(parents=True)
    monkeypatch.setattr(nmd, "default_projects_root", lambda: projects)
    repo = tmp_path / "repo"
    repo.mkdir()
    return repo


def _memory_dir(repo: Path) -> Path:
    return nmd.resolve(repo, create=True)


def _distractor(topic: str, *keywords: str) -> str:
    kw = "".join(f"  - {k}\n" for k in keywords)
    return (
        f"---\ndate: 2026-05-10\ntime: \"0900\"\ntype: memory\ntopic: {topic}\n"
        f"keywords:\n{kw}---\n\n# {topic}\n\n## Contexte\n{topic}.\n\n## Notes\nRAS.\n"
    )


def test_search_project_trouve_la_memoire_native(tmp_path, monkeypatch, capsys):
    repo = _seed_native_memory(tmp_path, monkeypatch)
    mem = _memory_dir(repo)
    # Cible + distracteurs : BM25 a besoin d'un corpus où les termes discriminent.
    (mem / "2026-05-11-1430-alex-pricing.md").write_text(_MEMORY, encoding="utf-8")
    (mem / "2026-05-10-0900-alex-infra.md").write_text(
        _distractor("infra", "serveur", "deploy", "ci"), encoding="utf-8")
    (mem / "2026-05-09-0900-alex-design.md").write_text(
        _distractor("design", "figma", "maquette", "couleur"), encoding="utf-8")
    (mem / "2026-05-08-0900-alex-rh.md").write_text(
        _distractor("rh", "recrutement", "entretien", "onboarding"), encoding="utf-8")

    monkeypatch.setattr(
        sys, "argv",
        ["search_memories.py", "pricing olenbee devis", "--project", str(repo)],
    )
    search_memories.main()
    results = json.loads(capsys.readouterr().out)
    assert results, "la mémoire pricing doit ressortir"
    assert results[0]["path"].endswith("alex-pricing.md")
    assert results[0]["type"] == "decision"


def test_search_project_vide_si_pas_de_memoire_native(tmp_path, monkeypatch, capsys):
    repo = _seed_native_memory(tmp_path, monkeypatch)  # aucune mémoire écrite

    monkeypatch.setattr(
        sys, "argv", ["search_memories.py", "pricing", "--project", str(repo)],
    )
    search_memories.main()
    assert json.loads(capsys.readouterr().out) == []


def test_graph_build_project_sur_dossier_natif(tmp_path, monkeypatch, capsys):
    repo = _seed_native_memory(tmp_path, monkeypatch)
    mem = _memory_dir(repo)
    (mem / "2026-05-11-1430-alex-decision.md").write_text(_MEMORY, encoding="utf-8")
    revision = _MEMORY.replace("Décision pricing", "Révision pricing").replace(
        "## Notes\nAligné à 8K.\n",
        "## Notes\nRévise [la décision](2026-05-11-1430-alex-decision.md).\n",
    )
    (mem / "2026-05-14-0900-alex-revision.md").write_text(revision, encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["graph.py", "build", "--project", str(repo)])
    graph.main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["nodes"]["memory"] == 2
    # Même topic → affinité, et le lien interne → arête link.
    assert payload["edges"]["affinity"] >= 1
    assert payload["edges"]["link"] >= 1


def test_graph_build_project_vide_si_pas_de_memoire(tmp_path, monkeypatch, capsys):
    repo = _seed_native_memory(tmp_path, monkeypatch)  # aucune mémoire écrite

    monkeypatch.setattr(sys, "argv", ["graph.py", "build", "--project", str(repo)])
    graph.main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["nodes"] == {"memory": 0, "normative": 0, "content": 0}


def test_lien_absolu_hors_racine_ni_arete_ni_casse(tmp_path):
    # Une mémoire native linke un fichier du repo par chemin absolu (cross-tree).
    root = tmp_path / "native"
    outside = tmp_path / "repo" / "src" / "main.py.md"
    outside.parent.mkdir(parents=True)
    outside.write_text("# fichier repo\n", encoding="utf-8")

    note = (
        "---\ndate: 2026-05-11\ntime: \"1430\"\ntype: insight\ntopic: refacto\n"
        "keywords:\n  - refacto\n---\n\n# Note\n\n## Contexte\nX.\n\n"
        f"## Notes\nVoir [le module]({outside}).\n"
    )
    note_path = root / "memory" / "2026-05-11-1430-alex-refacto.md"
    note_path.parent.mkdir(parents=True)
    note_path.write_text(note, encoding="utf-8")

    g = graph.build_graph(root, root)
    # Lien absolu résolu mais hors racine : pas un cassé, pas une arête.
    assert all(str(outside) not in b["target"] for b in g.broken)
    assert all(e.type != "link" for e in g.edges)
