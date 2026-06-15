"""Fixture: un workspace driven synthétique couvrant tous les cas du graphe."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Rendre scripts/graph.py importable comme module `graph`.
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """
    Construit un workspace shared miniature et retourne sa racine.

    Couvre : kinds (memory/normative/content), at-ref ok + cassé,
    link ok + cassé, lien externe ignoré, affinité oui/non, orphelin,
    exclusions (.claude / .tmp / _legacy), résolution de nom ambiguë.
    """
    root = tmp_path / "ws"

    # Racine normative avec un at-ref valide (RULES.md) et un cassé (TOOLS.md absent).
    _write(root / "CLAUDE.md", (
        "---\nspace-type: shared\nauthors:\n  - jane@drivenlabs.ai\n---\n\n"
        "# Workspace\n\nVoir @RULES.md pour les conventions. Voir aussi @TOOLS.md.\n"
    ))
    _write(root / "RULES.md", (
        "---\nauthors:\n  - jane@drivenlabs.ai\n---\n\n# Règles\n\nConventions.\n"
    ))

    # Fiche client (normative car CLAUDE.md), titre H1 "Acme", lien vers le rdv.
    _write(root / "Clients/Acme/CLAUDE.md", (
        "---\nauthors:\n  - jane@drivenlabs.ai\n---\n\n# Acme\n\n"
        "Client actif. Dernier point : [le RDV](memory/2026-06-01-1000-alex-rdv.md).\n"
    ))

    # Deux mémoires même topic → affinité ; la révision linke la décision + un brief cassé.
    _write(root / "Clients/Acme/memory/2026-05-11-1430-jane-decision-pricing.md", (
        "---\ndate: 2026-05-11\ntime: \"1430\"\nauthors:\n  - jane@drivenlabs.ai\n"
        "type: decision\ntopic: pricing-acme\nkeywords:\n  - acme\n  - pricing\n"
        "  - pack-sales\n  - negociation\n  - devis\n---\n\n# Décision pricing\n\n"
        "## Contexte\nPricing Acme.\n\n## Notes\nVoir [la fiche](../CLAUDE.md).\n"
    ))
    _write(root / "Clients/Acme/memory/2026-05-14-0900-jane-revision-pricing.md", (
        "---\ndate: 2026-05-14\ntime: \"0900\"\nauthors:\n  - jane@drivenlabs.ai\n"
        "type: decision\ntopic: pricing-acme\nkeywords:\n  - acme\n  - pricing\n"
        "  - revision\n  - devis\n---\n\n# Révision pricing\n\n## Contexte\nRévision.\n\n"
        "## Notes\nRévise [la décision](2026-05-11-1430-jane-decision-pricing.md). "
        "Cf [brief](../brief.md). Source : [post](https://example.com/x).\n"
    ))

    # Mémoire RDV : topic "john-doe" (collision de nom avec le contact), linke le contact.
    _write(root / "Clients/Acme/memory/2026-06-01-1000-alex-rdv.md", (
        "---\ndate: 2026-06-01\ntime: \"1000\"\nauthors:\n  - alex@drivenlabs.ai\n"
        "type: interaction\ntopic: john-doe\nkeywords:\n  - john-doe\n  - meeting\n"
        "  - agenda\n---\n\n# RDV John Doe\n\n## Contexte\nPoint.\n\n## Notes\n"
        "Avec [John Doe](../../../Contacts/john-doe.md).\n"
    ))

    # Contact (content), stem "john-doe" → collision avec le topic de la mémoire rdv.
    _write(root / "Contacts/john-doe.md", "# John Doe\n\nContact Acme.\n")

    # Document orphelin (aucune arête entrante).
    _write(root / "Drivenlabs/positioning.md", "# Positioning\n\nSegment PME.\n")

    # Exclusions : ne doivent jamais devenir des nœuds.
    _write(root / "_legacy/old.md", "# Vieux\n")
    _write(root / ".tmp/scratch.md", "# Scratch\n")
    _write(root / ".claude/note.md", "# Interne\n")

    return root
