"""Tests de construction du graphe."""

from __future__ import annotations

import graph


def _edges(g, etype=None):
    return [e for e in g.edges if etype is None or e.type == etype]


def test_collect_exclut_dossiers_techniques(workspace):
    files = graph.collect_md_files(workspace)
    names = {f.name for f in files}
    paths = {str(f) for f in files}
    assert "CLAUDE.md" in names
    assert not any("_legacy" in p for p in paths)
    assert not any("/.tmp/" in p for p in paths)
    assert not any("/.claude/" in p for p in paths)


def test_build_noeuds_et_kinds(workspace):
    g = graph.build_graph(workspace, workspace)
    assert g.nodes["CLAUDE.md"]["kind"] == "normative"
    assert g.nodes["Clients/Olenbee/CLAUDE.md"]["kind"] == "normative"
    assert g.nodes["Drivenlabs/positioning.md"]["kind"] == "content"
    assert g.nodes["Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md"]["kind"] == "memory"
    # Le titre H1 est capturé.
    assert g.nodes["Clients/Olenbee/CLAUDE.md"]["title"] == "Olenbee"


def test_build_arete_at_ref_valide(workspace):
    g = graph.build_graph(workspace, workspace)
    at = _edges(g, "at-ref")
    assert any(e.source == "CLAUDE.md" and e.target == "RULES.md" for e in at)


def test_build_at_ref_casse_dans_broken(workspace):
    g = graph.build_graph(workspace, workspace)
    assert any(b["ref_type"] == "at-ref" and "TOOLS.md" in b["target"] for b in g.broken)


def test_build_arete_link_valide(workspace):
    g = graph.build_graph(workspace, workspace)
    links = _edges(g, "link")
    src = "Clients/Olenbee/memory/2026-05-14-0900-mael-revision-pricing.md"
    tgt = "Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md"
    assert any(e.source == src and e.target == tgt for e in links)


def test_build_link_casse_dans_broken(workspace):
    g = graph.build_graph(workspace, workspace)
    assert any(b["ref_type"] == "link" and "brief.md" in b["target"] for b in g.broken)


def test_build_ignore_liens_externes(workspace):
    g = graph.build_graph(workspace, workspace)
    # Aucune arête ni cassé ne doit pointer vers une URL externe.
    assert all("example.com" not in e.target for e in g.edges)
    assert all("example.com" not in b["target"] for b in g.broken)


def test_build_porte_le_numero_de_ligne(workspace):
    g = graph.build_graph(workspace, workspace)
    at = [e for e in g.edges if e.type == "at-ref" and e.target == "RULES.md"]
    # Numéro de ligne absolu dans le fichier (frontmatter inclus) : @RULES.md ligne 9.
    assert at and at[0].line == 9


def test_build_lien_vers_fichier_exclu_ni_arete_ni_casse(tmp_path):
    root = tmp_path / "ws"
    (root / ".claude").mkdir(parents=True)
    (root / ".claude" / "note.md").write_text("# Note\n", encoding="utf-8")
    (root / "CLAUDE.md").write_text(
        "---\nspace-type: personal\n---\n\n# T\n\nVoir [note](.claude/note.md).\n",
        encoding="utf-8",
    )
    g = graph.build_graph(root, root)
    assert all(".claude/note.md" not in e.target for e in g.edges)
    assert all(".claude/note.md" not in b["target"] for b in g.broken)
