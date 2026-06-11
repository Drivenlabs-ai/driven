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
    scope = scope.resolve()
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
        # Cible sous la racine mais exclue du graphe (.claude, .tmp, _legacy) : ignorer.
        if target_rel is not None:
            return
    g.broken.append({"source": source_rel, "target": raw, "line": line, "ref_type": ref_type})


def compute_affinity(nodes: dict[str, dict[str, Any]]) -> list[Edge]:
    """Arêtes faibles entre mémoires d'un même sujet. Implémenté en Task 5."""
    return []
