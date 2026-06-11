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


def graph_to_dict(g: Graph) -> dict[str, Any]:
    """Sérialise le graphe en structure JSON."""
    return {
        "root": g.root,
        "nodes": g.nodes,
        "edges": [{"source": e.source, "target": e.target, "type": e.type, "line": e.line} for e in g.edges],
        "broken": g.broken,
    }


def _json_default(o: Any) -> Any:
    """Sérialise les types non-JSON-natifs (date, datetime) en chaîne ISO."""
    if hasattr(o, "isoformat"):
        return o.isoformat()
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


def write_cache(g: Graph, root: Path) -> None:
    """Écrit le graphe à <root>/.claude/driven/graph.json. No-op si écriture impossible."""
    cache = root / ".claude" / "driven" / "graph.json"
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(graph_to_dict(g), ensure_ascii=False, indent=2, default=_json_default)
        cache.write_text(text, encoding="utf-8")
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index de graphe structurel d'un workspace driven.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Construit le graphe et écrit le cache.")
    p_build.add_argument("--scope", type=Path, default=Path.cwd())

    p_impact = sub.add_parser("impact", help="Liens entrants vers un fichier/dossier.")
    p_impact.add_argument("target")
    p_impact.add_argument("--scope", type=Path, default=Path.cwd())

    args = parser.parse_args()
    scope = args.scope.resolve()

    if args.command == "build":
        result = cmd_build(scope)
    elif args.command == "impact":
        result = cmd_impact(scope, args.target)
    else:  # pragma: no cover
        parser.error(f"unknown command: {args.command}")

    print(json.dumps(result, ensure_ascii=False, indent=2, default=_json_default))


if __name__ == "__main__":
    main()
