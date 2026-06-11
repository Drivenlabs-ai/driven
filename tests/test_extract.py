"""Tests des fonctions pures de parsing et d'inférence de graph.py."""

from __future__ import annotations

from pathlib import Path

import graph


def test_parse_frontmatter_valid():
    content = "---\ntopic: pricing\n---\n\n# Titre\n\nCorps.\n"
    fm, body = graph.parse_frontmatter(content)
    assert fm == {"topic": "pricing"}
    assert body.startswith("# Titre")


def test_parse_frontmatter_absent():
    content = "# Pas de frontmatter\n"
    fm, body = graph.parse_frontmatter(content)
    assert fm == {}
    assert body == content


def test_parse_frontmatter_corrompu_ne_leve_pas():
    content = "---\ntopic: [unclosed\n---\n\n# Titre\n"
    fm, body = graph.parse_frontmatter(content)
    assert fm == {}
    assert body == content


def test_extract_h1():
    assert graph.extract_h1("Intro\n\n# Mon Titre\n\n## Section\n") == "Mon Titre"
    assert graph.extract_h1("Pas de titre.\n") == ""


def test_infer_kind_memory():
    p = Path("Clients/Olenbee/memory/2026-05-11-1430-mael-decision.md")
    assert graph.infer_kind(p, {"date": "2026-05-11"}) == "memory"


def test_infer_kind_normative():
    assert graph.infer_kind(Path("RULES.md"), {}) == "normative"
    assert graph.infer_kind(Path("Clients/Acme/CLAUDE.md"), {}) == "normative"


def test_infer_kind_content():
    assert graph.infer_kind(Path("Drivenlabs/positioning.md"), {}) == "content"
    # Un fichier dans memory/ SANS date n'est pas une mémoire.
    assert graph.infer_kind(Path("x/memory/draft.md"), {}) == "content"


def test_is_external():
    assert graph.is_external("https://example.com/x") is True
    assert graph.is_external("http://x.y") is True
    assert graph.is_external("mailto:a@b.c") is True
    assert graph.is_external("../CLAUDE.md") is False


def test_extract_links_avec_lignes():
    text = "ligne 1\nVoir [la fiche](../CLAUDE.md) ici.\nRien.\n[post](https://x.io)\n"
    links = graph.extract_links(text)
    assert ("../CLAUDE.md", 2) in links
    assert ("https://x.io", 4) in links


def test_extract_links_ignore_non_md():
    # Une cible sans extension .md n'est pas une arête candidate.
    text = "[dossier](Clients/Olenbee) et [doc](notes.md)\n"
    targets = [t for t, _ in graph.extract_links(text)]
    assert "notes.md" in targets
    assert "Clients/Olenbee" not in targets


def test_extract_at_refs():
    text = "Voir @RULES.md et @Espace/CLAUDE.md.\nMail alex@drivenlabs.ai à ignorer.\n"
    refs = graph.extract_at_refs(text)
    targets = [t for t, _ in refs]
    assert "RULES.md" in targets
    assert "Espace/CLAUDE.md" in targets
    # Un email ne doit pas être capté comme at-ref.
    assert all("drivenlabs.ai" not in t for t in targets)
