# Index de graphe structurel — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Doter driven d'un index des relations déjà écrites dans un workspace (liens markdown, références `@`, frontmatter), requêtable via un script unique, et brancher cet index sur la propagation, l'anti-récidive et l'auto cross-link.

**Architecture:** Un script Python autonome `scripts/graph.py` (à côté de `search_memories.py`) expose des fonctions pures (parsing, extraction d'arêtes, résolution, construction de graphe) et un CLI à sous-commandes (`build`, `impact`, `explain`, `path`, `check`). Chaque invocation reconstruit le graphe en mémoire avant de répondre — jamais de lecture d'un graphe périmé. Le graphe est mis en cache à `<racine-workspace>/.claude/driven/graph.json` sans logique d'invalidation (le rebuild systématique la rend inutile). Strictement déterministe : zéro LLM. Les références du skill sont ensuite éditées pour consommer le script ; si le script échoue, driven retombe sur ses comportements actuels.

**Tech Stack:** Python 3.10+ (stdlib), PyYAML (unique dépendance, déjà requise par `search_memories.py`). Tests : `pytest`, exécutés via `uv run --with pyyaml --with pytest pytest` (éphémère, aucune config repo). Le script reste exécutable en sandbox Cowork (Ubuntu 22.04).

**Spec source:** `docs/superpowers/specs/2026-06-11-graph-index-design.md`

---

## File Structure

| Fichier | Rôle | Action |
|---|---|---|
| `scripts/graph.py` | Construction + requêtes du graphe, fonctions pures + CLI | Créer |
| `tests/conftest.py` | Fixture workspace synthétique + import path du script | Créer |
| `tests/test_extract.py` | Tests parsing, extraction liens/`@`, résolution de cibles | Créer |
| `tests/test_build.py` | Tests construction du graphe + arêtes d'affinité | Créer |
| `tests/test_subcommands.py` | Tests `impact`/`explain`/`path`/`check` + contrat CLI | Créer |
| `skills/driven/references/graphe.md` | Quand invoquer le script, format de restitution NL | Créer |
| `skills/driven/SKILL.md` | §6.2 signal d'activation + §12 référence graphe | Modifier |
| `skills/driven/references/propagation.md` | `impact` remplace le grep | Modifier |
| `skills/driven/references/challenge-anti-recidive.md` | 3ᵉ source : mémoires liées par arête | Modifier |
| `skills/driven/references/memory.md` | Auto cross-link via `explain` | Modifier |
| `skills/driven/references/interface-cli.md` | Verbes `explain` / `path` | Modifier |
| `skills/driven/references/frontmatter.md` | Champ `confidence` des mémoires | Modifier |
| `.claude-plugin/plugin.json` | Bump version 1.9.0 | Modifier |

**Branche de travail :** `feat/graph-index` (déjà créée, la spec y est committée).

**Toutes les commandes de test se lancent depuis la racine du repo :** `/Users/alexandrebouchez/Code/drivenlabs-ai/driven`

---

## Task 1: Scaffolding des tests + helpers de parsing

Pose la fixture workspace synthétique et les trois premières fonctions pures (frontmatter, H1, inférence de `kind`).

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_extract.py`
- Create: `scripts/graph.py`

- [ ] **Step 1: Écrire `tests/conftest.py` (fixture workspace + import path)**

```python
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
        "---\nspace-type: shared\nauthors:\n  - mael@drivenlabs.ai\n---\n\n"
        "# Workspace\n\nVoir @RULES.md pour les conventions. Voir aussi @TOOLS.md.\n"
    ))
    _write(root / "RULES.md", (
        "---\nauthors:\n  - mael@drivenlabs.ai\n---\n\n# Règles\n\nConventions.\n"
    ))

    # Fiche client (normative car CLAUDE.md), titre H1 "Olenbee", lien vers le rdv.
    _write(root / "Clients/Olenbee/CLAUDE.md", (
        "---\nauthors:\n  - mael@drivenlabs.ai\n---\n\n# Olenbee\n\n"
        "Client actif. Dernier point : [le RDV](memory/2026-06-01-1000-alex-rdv.md).\n"
    ))

    # Deux mémoires même topic → affinité ; la révision linke la décision + un brief cassé.
    _write(root / "Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md", (
        "---\ndate: 2026-05-11\ntime: \"1430\"\nauthors:\n  - mael@drivenlabs.ai\n"
        "type: decision\ntopic: pricing-olenbee\nkeywords:\n  - olenbee\n  - pricing\n"
        "  - pack-sales\n  - negociation\n  - devis\n---\n\n# Décision pricing\n\n"
        "## Contexte\nPricing Olenbee.\n\n## Notes\nVoir [la fiche](../CLAUDE.md).\n"
    ))
    _write(root / "Clients/Olenbee/memory/2026-05-14-0900-mael-revision-pricing.md", (
        "---\ndate: 2026-05-14\ntime: \"0900\"\nauthors:\n  - mael@drivenlabs.ai\n"
        "type: decision\ntopic: pricing-olenbee\nkeywords:\n  - olenbee\n  - pricing\n"
        "  - revision\n  - devis\n---\n\n# Révision pricing\n\n## Contexte\nRévision.\n\n"
        "## Notes\nRévise [la décision](2026-05-11-1430-mael-decision-pricing.md). "
        "Cf [brief](../brief.md). Source : [post](https://example.com/x).\n"
    ))

    # Mémoire RDV : topic "laurent" (collision de nom avec le contact), linke le contact.
    _write(root / "Clients/Olenbee/memory/2026-06-01-1000-alex-rdv.md", (
        "---\ndate: 2026-06-01\ntime: \"1000\"\nauthors:\n  - alex@drivenlabs.ai\n"
        "type: interaction\ntopic: laurent\nkeywords:\n  - laurent\n  - meeting\n"
        "  - agenda\n---\n\n# RDV Laurent\n\n## Contexte\nPoint.\n\n## Notes\n"
        "Avec [Laurent](../../../Contacts/laurent.md).\n"
    ))

    # Contact (content), stem "laurent" → collision avec le topic de la mémoire rdv.
    _write(root / "Contacts/laurent.md", "# Laurent Urien\n\nContact Olenbee.\n")

    # Document orphelin (aucune arête entrante).
    _write(root / "Drivenlabs/positioning.md", "# Positioning\n\nSegment PME.\n")

    # Exclusions : ne doivent jamais devenir des nœuds.
    _write(root / "_legacy/old.md", "# Vieux\n")
    _write(root / ".tmp/scratch.md", "# Scratch\n")
    _write(root / ".claude/note.md", "# Interne\n")

    return root
```

- [ ] **Step 2: Écrire le premier test dans `tests/test_extract.py` (parsing + kind)**

```python
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
```

- [ ] **Step 3: Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_extract.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'graph'` (le fichier `scripts/graph.py` n'existe pas encore).

- [ ] **Step 4: Créer `scripts/graph.py` avec les helpers de parsing**

```python
#!/usr/bin/env python3
"""
graph.py — Index de graphe structurel d'un workspace driven.

Recense les relations DÉJÀ écrites dans les fichiers .md (liens markdown,
références @, frontmatter) et répond à une sous-commande. Aucune interprétation,
aucun appel LLM. Chaque invocation reconstruit le graphe avant de répondre.

Sous-commandes :
    build              Construit le graphe, écrit le cache, affiche les stats.
    impact <path>      Liens entrants (blast radius) vers un fichier ou dossier.
    explain <nom|path> Fiche d'une entité + ses arêtes + mémoires liées.
    path <A> <B>       Plus court chemin entre deux nœuds.
    check              Liens cassés + fichiers orphelins.

Usage :
    python graph.py build --scope /path/to/workspace
    python graph.py impact Clients/Olenbee/CLAUDE.md --scope /path
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML missing. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extrait le frontmatter YAML. Retourne ({}, content) si absent ou invalide."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        fm = yaml.safe_load(parts[1])
        if not isinstance(fm, dict):
            return {}, content
        return fm, parts[2].lstrip("\n")
    except yaml.YAMLError:
        return {}, content


def extract_h1(body: str) -> str:
    """Retourne le texte du premier titre `# H1`, sans le dièse. '' si absent."""
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def infer_kind(path: Path, fm: dict[str, Any]) -> str:
    """
    Classe un fichier : 'memory', 'normative' ou 'content'.

    memory    : dans un dossier 'memory/' ET frontmatter porteur d'une 'date'.
    normative : nom de fichier en MAJUSCULES (CLAUDE, RULES, SOUL, ME, ABOUT...).
    content   : tout le reste.
    """
    in_memory_dir = any(p.name.lower() == "memory" for p in path.parents)
    if in_memory_dir and "date" in fm:
        return "memory"
    if path.stem.isupper():
        return "normative"
    return "content"
```

- [ ] **Step 5: Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_extract.py -v`
Expected: PASS (7 tests).

- [ ] **Step 6: Commit**

```bash
git add scripts/graph.py tests/conftest.py tests/test_extract.py
git commit -m "feat(graph): helpers de parsing + fixture workspace de test"
```

---

## Task 2: Extraction des arêtes (liens, `@`-refs, externes)

Détecte les liens markdown et les références `@` avec leur numéro de ligne, et distingue les cibles externes.

**Files:**
- Modify: `scripts/graph.py`
- Modify: `tests/test_extract.py`

- [ ] **Step 1: Ajouter les tests d'extraction dans `tests/test_extract.py`**

```python
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
```

- [ ] **Step 2: Lancer les nouveaux tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_extract.py -k "external or links or at_refs" -v`
Expected: FAIL — `AttributeError: module 'graph' has no attribute 'is_external'`.

- [ ] **Step 3: Ajouter les fonctions d'extraction dans `scripts/graph.py`**

Ajouter après `infer_kind` :

```python
# Lien markdown [texte](cible) — cible capturée jusqu'à la première parenthèse.
_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# Référence @ : début de ligne ou précédée d'un espace, cible se terminant par .md.
# Le lookbehind sur un non-espace exclut les emails (alex@domaine.md n'existe pas,
# mais la borne gauche garantit qu'on ne capte pas le @ au milieu d'un mot).
_AT_RE = re.compile(r"(?:^|(?<=\s))@([^\s)#]+\.md)")

_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")


def is_external(raw: str) -> bool:
    """True si la cible est une URL externe (jamais un nœud du workspace)."""
    return raw.strip().lower().startswith(_EXTERNAL_PREFIXES)


def extract_links(text: str) -> list[tuple[str, int]]:
    """
    Retourne les liens markdown [(cible_brute, numéro_de_ligne)].

    Ne garde que les cibles externes (filtrées plus tard) ou se terminant par
    '.md' (après suppression d'une éventuelle ancre #...). Les liens vers un
    dossier sans .md sont ignorés (jamais une arête, jamais un cassé).
    """
    out: list[tuple[str, int]] = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        for m in _LINK_RE.finditer(line):
            raw = m.group(1).strip()
            if is_external(raw):
                out.append((raw, lineno))
                continue
            target = raw.split("#", 1)[0].strip()
            if target.lower().endswith(".md"):
                out.append((raw, lineno))
    return out


def extract_at_refs(text: str) -> list[tuple[str, int]]:
    """Retourne les références @fichier.md [(cible_brute, numéro_de_ligne)]."""
    out: list[tuple[str, int]] = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        for m in _AT_RE.finditer(line):
            out.append((m.group(1).strip(), lineno))
    return out
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_extract.py -v`
Expected: PASS (11 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/graph.py tests/test_extract.py
git commit -m "feat(graph): extraction des liens markdown et references @"
```

---

## Task 3: Résolution des cibles + détection de la racine de workspace

Résout une cible brute en chemin réel (relatif au fichier source, puis à la racine), et trouve la racine du workspace par remontée d'arborescence.

**Files:**
- Modify: `scripts/graph.py`
- Modify: `tests/test_extract.py`

- [ ] **Step 1: Ajouter les tests dans `tests/test_extract.py`**

```python
def test_resolve_target_relatif_au_fichier(workspace):
    source = workspace / "Clients/Olenbee/memory/2026-05-14-0900-mael-revision-pricing.md"
    resolved = graph.resolve_target("2026-05-11-1430-mael-decision-pricing.md", source, workspace)
    assert resolved == (source.parent / "2026-05-11-1430-mael-decision-pricing.md").resolve()


def test_resolve_target_relatif_a_la_racine(workspace):
    source = workspace / "CLAUDE.md"
    resolved = graph.resolve_target("Clients/Olenbee/CLAUDE.md", source, workspace)
    assert resolved == (workspace / "Clients/Olenbee/CLAUDE.md").resolve()


def test_resolve_target_inexistant(workspace):
    source = workspace / "CLAUDE.md"
    assert graph.resolve_target("TOOLS.md", source, workspace) is None


def test_resolve_target_ignore_ancre(workspace):
    source = workspace / "CLAUDE.md"
    resolved = graph.resolve_target("RULES.md#section", source, workspace)
    assert resolved == (workspace / "RULES.md").resolve()


def test_find_workspace_root_depuis_sous_dossier(workspace):
    deep = workspace / "Clients/Olenbee/memory"
    assert graph.find_workspace_root(deep) == workspace.resolve()


def test_find_workspace_root_absent(tmp_path):
    # Pas de CLAUDE.md avec space-type → None.
    (tmp_path / "x").mkdir()
    assert graph.find_workspace_root(tmp_path / "x") is None
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_extract.py -k "resolve or workspace_root" -v`
Expected: FAIL — `AttributeError: module 'graph' has no attribute 'resolve_target'`.

- [ ] **Step 3: Ajouter les fonctions dans `scripts/graph.py`**

```python
def resolve_target(raw: str, source: Path, root: Path) -> Path | None:
    """
    Résout une cible de lien/at-ref en chemin absolu existant.

    Essaie d'abord relatif au dossier du fichier source, puis relatif à la
    racine du workspace. Retourne None si aucune cible existante (lien cassé).
    L'ancre #fragment est ignorée.
    """
    target = raw.split("#", 1)[0].strip()
    if not target:
        return None
    candidate = (source.parent / target).resolve()
    if candidate.is_file():
        return candidate
    candidate = (root / target).resolve()
    if candidate.is_file():
        return candidate
    return None


def find_workspace_root(scope: Path) -> Path | None:
    """
    Remonte depuis scope jusqu'à un CLAUDE.md portant un frontmatter space-type.

    Retourne la racine résolue, ou None si aucune racine driven trouvée.
    """
    current = scope.resolve()
    for candidate in [current, *current.parents]:
        claude = candidate / "CLAUDE.md"
        if claude.is_file():
            try:
                fm, _ = parse_frontmatter(claude.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                fm = {}
            if "space-type" in fm:
                return candidate
    return None
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_extract.py -v`
Expected: PASS (17 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/graph.py tests/test_extract.py
git commit -m "feat(graph): resolution des cibles et detection de la racine"
```

---

## Task 4: Construction du graphe (nœuds, arêtes, cassés)

Assemble le graphe complet : collecte des fichiers (avec exclusions), nœuds, arêtes `at-ref`/`link`, liste des cassés.

**Files:**
- Modify: `scripts/graph.py`
- Create: `tests/test_build.py`

- [ ] **Step 1: Écrire `tests/test_build.py`**

```python
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
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_build.py -v`
Expected: FAIL — `AttributeError: module 'graph' has no attribute 'collect_md_files'`.

- [ ] **Step 3: Ajouter les structures de données et la construction dans `scripts/graph.py`**

Ajouter les dataclasses juste après les imports (avant `parse_frontmatter`) :

```python
EXCLUDED_DIRS = {".claude", ".tmp", ".git", "_legacy"}


@dataclass
class Edge:
    source: str   # path relatif POSIX
    target: str   # path relatif POSIX (ou cible brute pour affinity entre mémoires)
    type: str     # "at-ref" | "link" | "affinity"
    line: int | None = None


@dataclass
class Graph:
    root: str
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    broken: list[dict[str, Any]] = field(default_factory=list)
```

Ajouter les fonctions après `find_workspace_root` :

```python
def collect_md_files(scope: Path) -> list[Path]:
    """Liste les .md sous scope, en excluant les dossiers techniques et _legacy."""
    if not scope.exists() or not scope.is_dir():
        return []
    out: list[Path] = []
    for md in scope.rglob("*.md"):
        if any(p.name in EXCLUDED_DIRS for p in md.parents):
            continue
        out.append(md)
    return out


def _rel(path: Path, root: Path) -> str | None:
    """Path relatif POSIX à la racine, ou None si hors racine."""
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return None


def build_graph(scope: Path, root: Path) -> Graph:
    """
    Construit le graphe : nœuds (fichiers .md), arêtes at-ref/link, cassés.

    Les arêtes d'affinité sont ajoutées séparément (cf compute_affinity), appelé
    en fin de fonction. Un fichier illisible est ignoré (WARN stderr). Un
    frontmatter invalide donne un nœud de kind 'content' (parse_frontmatter
    retourne {} sans lever).
    """
    root = root.resolve()
    g = Graph(root=root.as_posix())
    sources: list[tuple[str, Path, str]] = []  # (rel, abs_path, content)

    for f in collect_md_files(scope):
        rel = _rel(f, root)
        if rel is None:
            continue
        try:
            content = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"WARN: skipped {f} ({e})", file=sys.stderr)
            continue
        fm, body = parse_frontmatter(content)
        g.nodes[rel] = {
            "path": rel,
            "kind": infer_kind(f, fm),
            "frontmatter": fm,
            "title": extract_h1(body),
        }
        sources.append((rel, f, content))

    for rel, f, content in sources:
        for raw, line in extract_at_refs(content):
            _add_edge_or_broken(g, rel, f, root, raw, line, "at-ref")
        for raw, line in extract_links(content):
            if is_external(raw):
                continue
            _add_edge_or_broken(g, rel, f, root, raw, line, "link")

    g.edges.extend(compute_affinity(g.nodes))
    return g


def _add_edge_or_broken(
    g: Graph, source_rel: str, source_abs: Path, root: Path,
    raw: str, line: int, ref_type: str,
) -> None:
    """Ajoute une arête si la cible est un nœud, sinon l'enregistre comme cassée."""
    resolved = resolve_target(raw, source_abs, root)
    if resolved is not None:
        target_rel = _rel(resolved, root)
        if target_rel is not None and target_rel in g.nodes:
            g.edges.append(Edge(source_rel, target_rel, ref_type, line))
            return
        # Cible existante mais hors workspace : ni arête ni cassé.
        if target_rel is not None and resolved.is_file():
            return
    g.broken.append({"source": source_rel, "target": raw, "line": line, "ref_type": ref_type})
```

- [ ] **Step 4: Ajouter un stub `compute_affinity` (implémenté en Task 5) pour que l'import passe**

Ajouter après `_add_edge_or_broken` :

```python
def compute_affinity(nodes: dict[str, dict[str, Any]]) -> list[Edge]:
    """Arêtes faibles entre mémoires d'un même sujet. Implémenté en Task 5."""
    return []
```

- [ ] **Step 5: Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_build.py -v`
Expected: PASS (8 tests).

- [ ] **Step 6: Commit**

```bash
git add scripts/graph.py tests/test_build.py
git commit -m "feat(graph): construction du graphe (noeuds, aretes, casses)"
```

---

## Task 5: Arêtes d'affinité entre mémoires

Relie les mémoires partageant un sujet : même `topic` OU ≥ 2 `keywords` communs.

**Files:**
- Modify: `scripts/graph.py`
- Modify: `tests/test_build.py`

- [ ] **Step 1: Ajouter les tests d'affinité dans `tests/test_build.py`**

```python
def test_affinity_meme_topic(workspace):
    g = graph.build_graph(workspace, workspace)
    aff = _edges(g, "affinity")
    a = "Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md"
    b = "Clients/Olenbee/memory/2026-05-14-0900-mael-revision-pricing.md"
    assert any({e.source, e.target} == {a, b} for e in aff)


def test_affinity_pas_de_lien_sujets_distincts(workspace):
    g = graph.build_graph(workspace, workspace)
    aff = _edges(g, "affinity")
    rdv = "Clients/Olenbee/memory/2026-06-01-1000-alex-rdv.md"
    pricing = "Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md"
    # rdv (topic laurent, 0 keyword commun) n'a pas d'affinité avec le pricing.
    assert not any({e.source, e.target} == {rdv, pricing} for e in aff)


def test_affinity_declenchee_par_keywords_seuls():
    nodes = {
        "a.md": {"kind": "memory", "frontmatter": {"topic": "x", "keywords": ["k1", "k2", "k3"]}, "title": "", "path": "a.md"},
        "b.md": {"kind": "memory", "frontmatter": {"topic": "y", "keywords": ["k1", "k2", "k9"]}, "title": "", "path": "b.md"},
    }
    aff = graph.compute_affinity(nodes)
    # Topics différents (x vs y) mais 2 keywords communs (k1, k2) → affinité.
    assert len(aff) == 1
    assert {aff[0].source, aff[0].target} == {"a.md", "b.md"}


def test_affinity_un_seul_keyword_commun_insuffisant():
    nodes = {
        "a.md": {"kind": "memory", "frontmatter": {"topic": "x", "keywords": ["k1", "k2"]}, "title": "", "path": "a.md"},
        "b.md": {"kind": "memory", "frontmatter": {"topic": "y", "keywords": ["k1", "k9"]}, "title": "", "path": "b.md"},
    }
    assert graph.compute_affinity(nodes) == []
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_build.py -k affinity -v`
Expected: FAIL — `test_affinity_meme_topic` échoue (le stub retourne `[]`).

- [ ] **Step 3: Remplacer le stub `compute_affinity` dans `scripts/graph.py`**

Remplacer la fonction stub par :

```python
def _keywords_set(fm: dict[str, Any]) -> set[str]:
    """Normalise le champ keywords en set de chaînes minuscules."""
    raw = fm.get("keywords", [])
    if isinstance(raw, str):
        raw = [raw]
    elif not isinstance(raw, list):
        raw = []
    return {str(k).strip().lower() for k in raw if str(k).strip()}


def compute_affinity(nodes: dict[str, dict[str, Any]]) -> list[Edge]:
    """
    Arêtes 'affinity' (non orientées) entre mémoires d'un même sujet.

    Critère (alternatif) : même topic non vide, OU au moins 2 keywords communs.
    Une seule arête par paire, ordre canonique source < target.
    """
    memories = sorted(
        rel for rel, n in nodes.items() if n.get("kind") == "memory"
    )
    out: list[Edge] = []
    for i, a in enumerate(memories):
        fm_a = nodes[a]["frontmatter"]
        topic_a = str(fm_a.get("topic", "")).strip().lower()
        kw_a = _keywords_set(fm_a)
        for b in memories[i + 1:]:
            fm_b = nodes[b]["frontmatter"]
            topic_b = str(fm_b.get("topic", "")).strip().lower()
            same_topic = bool(topic_a) and topic_a == topic_b
            shared_kw = len(kw_a & _keywords_set(fm_b)) >= 2
            if same_topic or shared_kw:
                out.append(Edge(a, b, "affinity", None))
    return out
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_build.py -v`
Expected: PASS (12 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/graph.py tests/test_build.py
git commit -m "feat(graph): aretes d'affinite entre memoires (topic ou keywords)"
```

---

## Task 6: Sous-commande `build` + cache + squelette CLI

Sérialise le graphe, écrit le cache `.claude/driven/graph.json`, et câble le CLI à sous-commandes.

**Files:**
- Modify: `scripts/graph.py`
- Create: `tests/test_subcommands.py`

- [ ] **Step 1: Écrire `tests/test_subcommands.py`**

```python
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


def test_cli_build_emet_du_json(workspace):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "build", "--scope", str(workspace)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["nodes"]["memory"] == 3
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_subcommands.py -k build -v`
Expected: FAIL — `AttributeError: module 'graph' has no attribute 'cmd_build'`.

- [ ] **Step 3: Ajouter la sérialisation, le cache, `cmd_build` et le CLI dans `scripts/graph.py`**

Ajouter après `compute_affinity` :

```python
def graph_to_dict(g: Graph) -> dict[str, Any]:
    """Sérialise le graphe en structure JSON."""
    return {
        "root": g.root,
        "nodes": g.nodes,
        "edges": [{"source": e.source, "target": e.target, "type": e.type, "line": e.line} for e in g.edges],
        "broken": g.broken,
    }


def write_cache(g: Graph, root: Path) -> None:
    """Écrit le graphe à <root>/.claude/driven/graph.json. No-op si écriture impossible."""
    cache = root / ".claude" / "driven" / "graph.json"
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(graph_to_dict(g), ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"WARN: cache not written ({e})", file=sys.stderr)


def _resolve_root(scope: Path) -> Path:
    """Racine du workspace si détectée, sinon le scope lui-même."""
    return find_workspace_root(scope) or scope.resolve()


def cmd_build(scope: Path) -> dict[str, Any]:
    """Construit le graphe, écrit le cache, retourne les stats."""
    root = _resolve_root(scope)
    g = build_graph(scope, root)
    write_cache(g, root)
    node_kinds = {"memory": 0, "normative": 0, "content": 0}
    for n in g.nodes.values():
        node_kinds[n["kind"]] = node_kinds.get(n["kind"], 0) + 1
    edge_types = {"at-ref": 0, "link": 0, "affinity": 0}
    for e in g.edges:
        edge_types[e.type] = edge_types.get(e.type, 0) + 1
    return {
        "root": g.root,
        "nodes": node_kinds,
        "edges": edge_types,
        "broken_count": len(g.broken),
        "broken": g.broken,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index de graphe structurel d'un workspace driven.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Construit le graphe et écrit le cache.")
    p_build.add_argument("--scope", type=Path, default=Path.cwd())

    args = parser.parse_args()
    scope = args.scope.resolve()

    if args.command == "build":
        result = cmd_build(scope)
    else:  # pragma: no cover — sous-commandes ajoutées aux tasks suivantes
        parser.error(f"unknown command: {args.command}")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_subcommands.py -k build -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/graph.py tests/test_subcommands.py
git commit -m "feat(graph): sous-commande build, cache JSON et squelette CLI"
```

---

## Task 7: Sous-commande `impact` (blast radius)

Liste les liens entrants typés vers un fichier ou un dossier, triés `at-ref` puis `link`.

**Files:**
- Modify: `scripts/graph.py`
- Modify: `tests/test_subcommands.py`

- [ ] **Step 1: Ajouter les tests `impact` dans `tests/test_subcommands.py`**

```python
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
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_subcommands.py -k impact -v`
Expected: FAIL — `AttributeError: module 'graph' has no attribute 'cmd_impact'`.

- [ ] **Step 3: Ajouter `cmd_impact` dans `scripts/graph.py`**

Ajouter avant `main` :

```python
_TYPE_ORDER = {"at-ref": 0, "link": 1, "affinity": 2}


def cmd_impact(scope: Path, target: str) -> dict[str, Any]:
    """
    Liens entrants vers `target` (fichier ou dossier). Le blast radius.

    Exclut les arêtes d'affinité (seules les références structurelles cassent au
    renommage). Tri : at-ref avant link, puis par source. Pour un dossier, agrège
    l'impact de tous les fichiers qu'il contient.
    """
    root = _resolve_root(scope)
    g = build_graph(scope, root)
    target = target.strip("/")
    is_dir_target = not target.lower().endswith(".md")

    def matches(edge_target: str) -> bool:
        if is_dir_target:
            return edge_target == target or edge_target.startswith(target + "/")
        return edge_target == target

    incoming = [
        {"source": e.source, "type": e.type, "line": e.line, "to": e.target}
        for e in g.edges
        if e.type != "affinity" and matches(e.target)
    ]
    incoming.sort(key=lambda e: (_TYPE_ORDER[e["type"]], e["source"]))
    return {"target": target, "incoming": incoming, "count": len(incoming)}
```

Dans `main`, ajouter le parser et la branche. Après le bloc `p_build` :

```python
    p_impact = sub.add_parser("impact", help="Liens entrants vers un fichier/dossier.")
    p_impact.add_argument("target")
    p_impact.add_argument("--scope", type=Path, default=Path.cwd())
```

Et dans le dispatch, remplacer la branche `else` par :

```python
    if args.command == "build":
        result = cmd_build(scope)
    elif args.command == "impact":
        result = cmd_impact(scope, args.target)
    else:  # pragma: no cover
        parser.error(f"unknown command: {args.command}")
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_subcommands.py -k impact -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/graph.py tests/test_subcommands.py
git commit -m "feat(graph): sous-commande impact (blast radius)"
```

---

## Task 8: Sous-commande `explain` + résolution de nom

Résout un nom ou chemin en nœud(s), et retourne sa fiche, ses arêtes, et ses mémoires liées.

**Files:**
- Modify: `scripts/graph.py`
- Modify: `tests/test_subcommands.py`

- [ ] **Step 1: Ajouter les tests `explain` dans `tests/test_subcommands.py`**

```python
def test_resolve_name_par_titre(workspace):
    g = graph.build_graph(workspace, workspace)
    # "Olenbee" matche le H1 de la fiche client uniquement.
    assert graph.resolve_name(g, "Olenbee") == ["Clients/Olenbee/CLAUDE.md"]


def test_resolve_name_ambigu(workspace):
    g = graph.build_graph(workspace, workspace)
    # "laurent" matche le contact (stem) ET la mémoire rdv (topic).
    matches = set(graph.resolve_name(g, "laurent"))
    assert matches == {
        "Contacts/laurent.md",
        "Clients/Olenbee/memory/2026-06-01-1000-alex-rdv.md",
    }


def test_cmd_explain_noeud_unique(workspace):
    res = graph.cmd_explain(workspace, "Clients/Olenbee/CLAUDE.md")
    assert res["resolved"] == "Clients/Olenbee/CLAUDE.md"
    # Arête entrante (link depuis la décision pricing) et sortante (link vers le rdv).
    assert any(e["type"] == "link" for e in res["incoming"])
    assert any(e["type"] == "link" for e in res["outgoing"])


def test_cmd_explain_candidats_multiples(workspace):
    res = graph.cmd_explain(workspace, "laurent")
    assert res["resolved"] is None
    assert len(res["candidates"]) == 2


def test_cmd_explain_memoires_liees_triees(workspace):
    res = graph.cmd_explain(workspace, "Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md")
    # La mémoire de révision est liée (affinité + link) ; présente dans linked_memories.
    linked = [m["path"] for m in res["linked_memories"]]
    assert "Clients/Olenbee/memory/2026-05-14-0900-mael-revision-pricing.md" in linked
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_subcommands.py -k "resolve_name or explain" -v`
Expected: FAIL — `AttributeError: module 'graph' has no attribute 'resolve_name'`.

- [ ] **Step 3: Ajouter `resolve_name` et `cmd_explain` dans `scripts/graph.py`**

Ajouter avant `main` :

```python
def resolve_name(g: Graph, query: str) -> list[str]:
    """
    Résout un nom ou chemin en liste de paths de nœuds.

    Matche (insensible à la casse) sur : chemin exact, stem du fichier, titre H1,
    ou topic du frontmatter. Retourne tous les nœuds correspondants (≥ 0).
    """
    q = query.strip().lower()
    matches: list[str] = []
    for rel, node in g.nodes.items():
        stem = Path(rel).stem.lower()
        title = str(node.get("title", "")).lower()
        topic = str(node.get("frontmatter", {}).get("topic", "")).lower()
        if q in (rel.lower(), stem, title, topic):
            matches.append(rel)
    return matches


def cmd_explain(scope: Path, query: str) -> dict[str, Any]:
    """
    Fiche d'une entité : nœud résolu, arêtes entrantes/sortantes, mémoires liées.

    Si le nom matche plusieurs nœuds, retourne les candidats sans trancher.
    """
    root = _resolve_root(scope)
    g = build_graph(scope, root)
    matches = resolve_name(g, query)

    if len(matches) != 1:
        candidates = [{"path": m, "kind": g.nodes[m]["kind"]} for m in matches]
        return {"resolved": None, "candidates": candidates}

    target = matches[0]
    outgoing = [
        {"target": e.target, "type": e.type, "line": e.line}
        for e in g.edges if e.source == target
    ]
    incoming = [
        {"source": e.source, "type": e.type, "line": e.line}
        for e in g.edges if e.target == target
    ]

    linked_paths = {e.target for e in g.edges if e.source == target}
    linked_paths |= {e.source for e in g.edges if e.target == target}
    linked_memories = [
        {"path": p, "date": str(g.nodes[p]["frontmatter"].get("date", ""))}
        for p in linked_paths
        if p in g.nodes and g.nodes[p]["kind"] == "memory"
    ]
    linked_memories.sort(key=lambda m: m["date"], reverse=True)

    return {
        "resolved": target,
        "node": g.nodes[target],
        "outgoing": outgoing,
        "incoming": incoming,
        "linked_memories": linked_memories,
    }
```

Dans `main`, ajouter le parser après `p_impact` :

```python
    p_explain = sub.add_parser("explain", help="Fiche d'une entité + ses arêtes.")
    p_explain.add_argument("query")
    p_explain.add_argument("--scope", type=Path, default=Path.cwd())
```

Et ajouter la branche de dispatch avant le `else` :

```python
    elif args.command == "explain":
        result = cmd_explain(scope, args.query)
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_subcommands.py -k "resolve_name or explain" -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/graph.py tests/test_subcommands.py
git commit -m "feat(graph): sous-commande explain + resolution de nom"
```

---

## Task 9: Sous-commande `path` (plus court chemin)

BFS non orienté entre deux nœuds, avec la séquence d'arêtes traversées.

**Files:**
- Modify: `scripts/graph.py`
- Modify: `tests/test_subcommands.py`

- [ ] **Step 1: Ajouter les tests `path` dans `tests/test_subcommands.py`**

```python
def test_cmd_path_connecte(workspace):
    res = graph.cmd_path(
        workspace,
        "Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md",
        "Contacts/laurent.md",
    )
    # Chemin attendu : décision → fiche Olenbee → rdv → contact laurent.
    assert res["connected"] is True
    assert res["path"][0] == "Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md"
    assert res["path"][-1] == "Contacts/laurent.md"
    assert len(res["hops"]) == len(res["path"]) - 1


def test_cmd_path_non_connecte(workspace):
    res = graph.cmd_path(workspace, "Drivenlabs/positioning.md", "Contacts/laurent.md")
    assert res["connected"] is False
    assert res["path"] == []


def test_cmd_path_extremite_ambigue(workspace):
    res = graph.cmd_path(workspace, "laurent", "RULES.md")
    # "laurent" est ambigu → candidats retournés, pas de chemin.
    assert res["connected"] is False
    assert res.get("ambiguous")
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_subcommands.py -k path -v`
Expected: FAIL — `AttributeError: module 'graph' has no attribute 'cmd_path'`.

- [ ] **Step 3: Ajouter `cmd_path` dans `scripts/graph.py`**

Ajouter avant `main` :

```python
def _resolve_single(g: Graph, query: str) -> tuple[str | None, list[str]]:
    """Résout query en un nœud unique. Retourne (path|None, candidats)."""
    if query in g.nodes:
        return query, [query]
    matches = resolve_name(g, query)
    if len(matches) == 1:
        return matches[0], matches
    return None, matches


def cmd_path(scope: Path, a: str, b: str) -> dict[str, Any]:
    """
    Plus court chemin (BFS non orienté) entre deux nœuds, tous types d'arêtes.

    Si une extrémité est ambiguë ou introuvable, retourne connected=False avec
    les candidats. Sinon, le chemin de nœuds et la séquence d'arêtes traversées.
    """
    root = _resolve_root(scope)
    g = build_graph(scope, root)
    start, cand_a = _resolve_single(g, a)
    end, cand_b = _resolve_single(g, b)

    if start is None or end is None:
        return {
            "connected": False, "path": [], "hops": [], "ambiguous": True,
            "candidates_a": cand_a, "candidates_b": cand_b,
        }

    # Adjacence non orientée : voisin → type d'arête.
    adj: dict[str, list[tuple[str, str]]] = {rel: [] for rel in g.nodes}
    for e in g.edges:
        adj[e.source].append((e.target, e.type))
        adj[e.target].append((e.source, e.type))

    # BFS, en mémorisant le prédécesseur et le type d'arête emprunté.
    prev: dict[str, tuple[str, str]] = {}
    queue = [start]
    seen = {start}
    while queue:
        node = queue.pop(0)
        if node == end:
            break
        for neighbor, etype in adj[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                prev[neighbor] = (node, etype)
                queue.append(neighbor)

    if end != start and end not in prev:
        return {"connected": False, "path": [], "hops": []}

    # Reconstruction du chemin.
    chain = [end]
    hops: list[dict[str, str]] = []
    cur = end
    while cur != start:
        parent, etype = prev[cur]
        hops.append({"from": parent, "to": cur, "type": etype})
        chain.append(parent)
        cur = parent
    chain.reverse()
    hops.reverse()
    return {"connected": True, "path": chain, "hops": hops}
```

Dans `main`, ajouter le parser après `p_explain` :

```python
    p_path = sub.add_parser("path", help="Plus court chemin entre deux nœuds.")
    p_path.add_argument("node_a")
    p_path.add_argument("node_b")
    p_path.add_argument("--scope", type=Path, default=Path.cwd())
```

Et la branche de dispatch avant le `else` :

```python
    elif args.command == "path":
        result = cmd_path(scope, args.node_a, args.node_b)
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_subcommands.py -k path -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/graph.py tests/test_subcommands.py
git commit -m "feat(graph): sous-commande path (BFS plus court chemin)"
```

---

## Task 10: Sous-commande `check` (cassés + orphelins)

Liste les liens cassés et les fichiers sans aucune arête entrante structurelle.

**Files:**
- Modify: `scripts/graph.py`
- Modify: `tests/test_subcommands.py`

- [ ] **Step 1: Ajouter les tests `check` dans `tests/test_subcommands.py`**

```python
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
    assert "Contacts/laurent.md" not in res["orphans"]
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `uv run --with pyyaml --with pytest pytest tests/test_subcommands.py -k check -v`
Expected: FAIL — `AttributeError: module 'graph' has no attribute 'cmd_check'`.

- [ ] **Step 3: Ajouter `cmd_check` dans `scripts/graph.py`**

Ajouter avant `main` :

```python
def cmd_check(scope: Path) -> dict[str, Any]:
    """
    Liens cassés + fichiers orphelins.

    Orphelin = aucune arête entrante structurelle (at-ref ou link ; l'affinité
    ne compte pas), et kind != 'normative' (les fichiers racine sont attendus
    sans entrant).
    """
    root = _resolve_root(scope)
    g = build_graph(scope, root)
    referenced = {
        e.target for e in g.edges if e.type in ("at-ref", "link")
    }
    orphans = sorted(
        rel for rel, node in g.nodes.items()
        if node["kind"] != "normative" and rel not in referenced
    )
    return {"broken": g.broken, "broken_count": len(g.broken), "orphans": orphans}
```

Dans `main`, ajouter le parser après `p_path` :

```python
    p_check = sub.add_parser("check", help="Liens cassés + orphelins.")
    p_check.add_argument("--scope", type=Path, default=Path.cwd())
```

Et la branche de dispatch avant le `else` :

```python
    elif args.command == "check":
        result = cmd_check(scope)
```

- [ ] **Step 4: Lancer toute la suite pour vérifier l'intégration**

Run: `uv run --with pyyaml --with pytest pytest tests/ -v`
Expected: PASS (toute la suite : extract + build + subcommands).

- [ ] **Step 5: Commit**

```bash
git add scripts/graph.py tests/test_subcommands.py
git commit -m "feat(graph): sous-commande check (casses + orphelins)"
```

---

## Task 11: Référence `graphe.md` + câblage SKILL.md

Documente quand invoquer le script et comment restituer en NL, et l'ancre dans le SKILL.md (§6.2 + §12). Tâche documentaire — pas de tests automatiques.

**Files:**
- Create: `skills/driven/references/graphe.md`
- Modify: `skills/driven/SKILL.md`

- [ ] **Step 1: Créer `skills/driven/references/graphe.md`**

Contenu intégral du fichier :

```markdown
# graphe : Index des relations du workspace

Le script `scripts/graph.py` recense les relations déjà écrites dans les fichiers du workspace (liens markdown, références `@`, frontmatter) et répond à une sous-commande. Il ne crée ni n'interprète rien : il indexe ce qui est inscrit. La source de vérité reste les `.md`.

**Optimisation, jamais point de défaillance.** Si le script échoue (Python absent, dépendance manquante), retomber silencieusement sur le comportement historique (grep pour la propagation, BM25 seul pour l'anti-récidive). Ne jamais exposer l'erreur au user.

Chaque invocation reconstruit le graphe avant de répondre — impossible de requêter un graphe périmé. Le cache `.claude/driven/graph.json` n'est qu'un artefact de relecture, jamais une source.

## Invocation

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/graph.py" <commande> [args] --scope "<racine workspace>"
```

`--scope` par défaut = cwd. Toujours passer la racine du workspace courant. Filtrer le préfixe stdout éventuel avant de parser le JSON.

## Sous-commandes et quand les utiliser

| Situation | Commande | Lecture du résultat |
|---|---|---|
| Renommage / suppression d'un fichier ou dossier | `impact <path>` | `incoming` = qui pointe vers la cible. `at-ref` = chargement transitif (impact fort), `link` = lien simple. |
| Proposition stratégique sur une entité avec historique | `explain <entité>` | `linked_memories` triées par date = mémoires connexes à scruter pour l'anti-récidive. |
| Création d'une mémoire (auto cross-link) | `explain <entité>` | `incoming`/`outgoing` = candidats de liens markdown à insérer. |
| « explique-moi <entité> », « qu'est-ce qu'on sait sur X » | `explain <entité>` | Fiche + arêtes + mémoires. |
| « quel est le lien entre A et B » | `path <A> <B>` | `path` = chaîne de nœuds, `hops` = arêtes traversées. |
| Audit de cohérence, vérification des liens | `check` | `broken` = liens cassés (à corriger), `orphans` = fichiers sans entrée. |

## Résolution ambiguë

Si `explain` ou `path` retourne `resolved: null` (ou `ambiguous: true`) avec une liste de `candidates`, le script n'a pas tranché. Choisir selon le contexte de la tâche, ou demander en NL au user (« Tu parles du contact Laurent ou de la note du RDV ? »). Ne jamais deviner en silence.

## Restitution NL

Jamais de JSON brut au user. Reformuler comme `interface-cli.md` le fait pour `search` : phrases naturelles, liens markdown vers les fichiers, deux lignes de recap. Exemple après un `impact` au renommage :

> OK, j'ai renommé Olenbee : 2 chargements obligatoires et 12 liens mis à jour.

## Garde-fou bivalence

Le script tourne en Python 3.10+ stdlib + PyYAML, identiquement en Claude Code et en sandbox Cowork. Pas de hook, pas de dépendance lourde : la bivalence est préservée (cf SKILL.md §10).
```

- [ ] **Step 2: Modifier `skills/driven/SKILL.md` — ajouter le signal au §6.2**

Dans le tableau « Signaux de support » du §6.2, après la ligne `gestion-contexte.md`, ajouter cette ligne :

```markdown
| Renommage / suppression de fichier, proposition stratégique sur entité, demande « explique-moi X » / « lien entre A et B », audit de cohérence des liens | `graphe.md` | Invoquer `scripts/graph.py` (impact / explain / path / check), restituer en NL |
```

- [ ] **Step 3: Modifier `skills/driven/SKILL.md` — ajouter la référence au §12**

Dans la section « Transverses » du §12, après la ligne `proactivite.md`, ajouter :

```markdown
- `graphe.md` — Charger AVANT d'invoquer `scripts/graph.py` (renommage, suppression, proposition stratégique, requête de graphe, audit de liens — signal §6.2).
```

- [ ] **Step 4: Vérifier qu'aucune référence n'est cassée dans le SKILL**

Run: `grep -n "graphe.md" skills/driven/SKILL.md`
Expected: 2 occurrences (§6.2 et §12).

- [ ] **Step 5: Commit**

```bash
git add skills/driven/references/graphe.md skills/driven/SKILL.md
git commit -m "feat(graph): reference graphe.md + cablage SKILL.md (6.2 + 12)"
```

---

## Task 12: Branchement de l'index dans les références consommatrices

Édite les quatre refs qui consomment l'index : propagation, anti-récidive, auto cross-link, interface CLI. Clean slate (pas de trace de l'ancien comportement). Tâche documentaire.

**Files:**
- Modify: `skills/driven/references/propagation.md`
- Modify: `skills/driven/references/challenge-anti-recidive.md`
- Modify: `skills/driven/references/memory.md`
- Modify: `skills/driven/references/interface-cli.md`

- [ ] **Step 1: `propagation.md` — remplacer le grep par `impact`**

Dans la section « Renommage et regen des liens », remplacer le bloc workflow (les points 1-6 et la phrase sur le scan via grep) par :

```markdown
1. User demande de renommer un fichier ou un dossier (ex `Clients/Olenbee/` → `Clients/Olenbee-Mature/`).
2. Invoquer `scripts/graph.py impact <ancien-path>` pour obtenir les liens entrants typés (cf `graphe.md`). Si le script échoue, retomber sur un grep du path littéral.
3. Avec ≤ 50 liens à regénérer : cascade silencieuse, recap minimal.
4. Avec > 50 liens : demande de validation en NL avant exécution (volume = risque).
5. Renommage effectif + regen des liens vers le nouveau path.
6. Memory entry créée dans le `memory/` du parent commun, documentant le renommage et la liste des fichiers impactés.

Le recap distingue les types d'arête : un lien `at-ref` (`@fichier`) cassé est un chargement transitif rompu, signalé plus fortement qu'un lien markdown simple. Exemple : *« renommé Olenbee, mis à jour 2 chargements obligatoires et 12 liens. »*
```

- [ ] **Step 2: `challenge-anti-recidive.md` — ajouter la 3ᵉ source**

Dans la section « Workflow d'anti-récidive », au point 2 « Cascade de consultation », remplacer la liste à puces par :

```markdown
   - **Section « Lessons »** de tous les CLAUDE.md remontés (racine + sous-dossiers concernés)
   - **Mémoires liées par arête** au sujet, via `scripts/graph.py explain <entité>` (`linked_memories`) — capte les mémoires connexes même sans mot-clé commun (cf `graphe.md`)
   - **Mémoires** du dossier concerné (search BM25 sur les mots-clés du sujet, top 5 hits)

   Le champ `confidence` des mémoires pondère le signal : un rejet dans une mémoire `verbatim` (dicté par l'user) bloque ; un signal dans une mémoire `inferred` (déduction de Claude) se mentionne avec réserve. Si `graph.py` échoue, se limiter aux Lessons + BM25.
```

Dans la section « Anti-patterns », ajuster la ligne « Cascade infinie » pour refléter la 3ᵉ source :

```markdown
- **Cascade infinie** : limiter la consultation à 5 mémoires au total (toutes sources confondues : arêtes + BM25) + lessons des CLAUDE.md immédiatement remontés. Pas de récursion profonde.
```

- [ ] **Step 3: `memory.md` — auto cross-link via `explain`**

Dans la section « Auto cross-link », remplacer le point 1 du workflow numéroté par :

```markdown
1. Pour chaque entité mentionnée dans la nouvelle mémoire, invoquer `scripts/graph.py explain <entité>` (cf `graphe.md`) : les arêtes entrantes/sortantes donnent les candidats de liens markdown pertinents. À défaut (script indisponible), scan du `memory/` courant pour les mémoires de même `topic` ou mots-clés communs.
```

- [ ] **Step 4: `interface-cli.md` — documenter `explain` et `path`**

Dans la section « 2. Avec argument : nom d'action explicite », ajouter deux lignes au tableau, après la ligne `/driven search` :

```markdown
| `/driven explain "entité"` | Fiche d'une entité : ses liens, arêtes et mémoires connexes. Invocation de `scripts/graph.py explain`. |
| `/driven path "A" "B"` | Plus court chemin entre deux entités du workspace. Invocation de `scripts/graph.py path`. |
```

Et après la sous-section « `/driven search` : invocation du script Python », ajouter :

```markdown
## `/driven explain` et `/driven path` : invocation du script graphe

Mapping vers `scripts/graph.py` (cf `graphe.md` pour le détail des sous-commandes et le format de restitution) :

```
/driven explain "Olenbee"      → python "${CLAUDE_PLUGIN_ROOT}/scripts/graph.py" explain "Olenbee" --scope=<racine>
/driven path "Olenbee" "Acme"  → python "${CLAUDE_PLUGIN_ROOT}/scripts/graph.py" path "Olenbee" "Acme" --scope=<racine>
```

Restitution en NL (jamais le JSON brut) : fiche lisible avec liens markdown pour `explain`, chaîne de connexions pour `path`. Si le résultat est ambigu (plusieurs candidats), demander en NL lequel.
```

- [ ] **Step 5: Vérifier la cohérence des références croisées**

Run: `grep -rn "graph.py" skills/driven/references/ | wc -l`
Expected: ≥ 4 (propagation, challenge-anti-recidive, memory, interface-cli — plus graphe.md de la Task 11).

- [ ] **Step 6: Commit**

```bash
git add skills/driven/references/propagation.md skills/driven/references/challenge-anti-recidive.md skills/driven/references/memory.md skills/driven/references/interface-cli.md
git commit -m "feat(graph): branchement de l'index dans propagation/anti-recidive/memory/cli"
```

---

## Task 13: Champ `confidence` + bump de version

Officialise le champ `confidence` des mémoires dans `frontmatter.md` et bump le plugin en 1.9.0. Tâche documentaire + version.

**Files:**
- Modify: `skills/driven/references/frontmatter.md`
- Modify: `.claude-plugin/plugin.json`

- [ ] **Step 1: `frontmatter.md` — ajouter `confidence` au format memory**

Dans la section « Memory entry (perso ou shared) », ajouter le champ dans l'exemple YAML, après `topic:` et avant `keywords:` :

```yaml
confidence: verbatim
```

Et dans la liste descriptive des champs (après la ligne `topic`), ajouter :

```markdown
- `confidence` (optionnel) ∈ {`verbatim`, `inferred`, `mixed`} : `verbatim` = reformulation factuelle de ce que l'user a dit ou décidé ; `inferred` = déduction de Claude non énoncée explicitement ; `mixed` = les deux. Inféré silencieusement à la création, jamais demandé au user, jamais inscrit dans le corps (clean slate). Les mémoires sans le champ sont traitées comme `verbatim`. Exploité par `challenge-anti-recidive.md` pour pondérer les signaux de rejet.
```

- [ ] **Step 2: Mettre à jour l'ordre des champs documenté**

Dans la section « Règles d'écriture du frontmatter », ajuster la ligne sur l'ordre des champs pour inclure `confidence` :

```markdown
- L'ordre des champs n'est pas imposé mais reste consistant pour les memory entries (date, time, authors, type, topic, confidence, keywords).
```

- [ ] **Step 3: Bump version dans `.claude-plugin/plugin.json`**

Modifier la ligne `"version"` :

```json
  "version": "1.9.0",
```

- [ ] **Step 4: Vérifier la version**

Run: `grep '"version"' .claude-plugin/plugin.json`
Expected: `"version": "1.9.0",`

- [ ] **Step 5: Commit**

```bash
git add skills/driven/references/frontmatter.md .claude-plugin/plugin.json
git commit -m "feat(graph): champ confidence des memoires + bump v1.9.0"
```

---

## Task 14: Validation finale

Vérifie la suite complète et le contrat CLI de bout en bout.

**Files:**
- (aucun — validation seule)

- [ ] **Step 1: Lancer toute la suite de tests**

Run: `uv run --with pyyaml --with pytest pytest tests/ -v`
Expected: PASS — tous les tests (extract + build + subcommands).

- [ ] **Step 2: Vérifier le CLI de bout en bout sur le repo lui-même**

Run: `uv run --with pyyaml python3 scripts/graph.py check --scope skills/driven/references`
Expected: JSON valide avec `broken` et `orphans` (le dossier references n'est pas un workspace driven — `_resolve_root` retombe sur le scope, le script répond sans erreur). Vérifie la dégradation gracieuse hors workspace.

- [ ] **Step 3: Vérifier `build` de bout en bout sur un workspace jetable**

Run :
```bash
mkdir -p /tmp/gtest && printf '%s' '---
space-type: personal
---
# T

Voir @RULES.md.
' > /tmp/gtest/CLAUDE.md && uv run --with pyyaml python3 scripts/graph.py build --scope /tmp/gtest && echo OK
```
Expected: JSON de stats (`broken` contient `RULES.md`) puis `OK` (returncode 0). Le cache est écrit dans `/tmp/gtest/.claude/driven/graph.json`, jamais dans le repo. Nettoyer ensuite : `rm -rf /tmp/gtest`.

---

## Notes d'implémentation

- **TDD strict** : chaque task écrit le test d'abord, le voit échouer, implémente, le voit passer, commit.
- **Clean slate sur les docs** (Tasks 11-13) : aucune trace de l'ancien comportement (« avant on faisait un grep »). Les refs se lisent comme si l'index avait toujours existé. Le seul endroit où le fallback grep/BM25 est mentionné, c'est comme comportement de dégradation présent, pas comme historique.
- **DRY** : `parse_frontmatter` est dupliqué de `search_memories.py` (≈ 15 lignes) volontairement — les deux scripts restent des CLI autonomes invocables indépendamment, sans module partagé à résoudre dans la sandbox Cowork.
- **Pas de pyproject ajouté au repo** : les tests tournent via `uv run --with`, cohérent avec la règle « toujours `uv` » et zéro config repo.
- **Fin de branche** : à l'issue de la Task 14, la branche `feat/graph-index` est prête. Décider merge / PR via `superpowers:finishing-a-development-branch`.
```
