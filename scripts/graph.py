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
    python graph.py impact Clients/Acme/CLAUDE.md --scope /path
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import native_memory_dir

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
    """Liste les .md sous scope, en excluant les dossiers techniques et _legacy.

    L'exclusion porte sur les dossiers SOUS le scope, pas sur ses ancêtres : un
    scope lui-même situé sous `.claude` (cas du dossier de mémoire native
    `~/.claude/projects/<slug>/memory/`) reste parcouru normalement.
    """
    if not scope.exists() or not scope.is_dir():
        return []
    scope = scope.resolve()
    out: list[Path] = []
    for md in scope.rglob("*.md"):
        rel = md.resolve().relative_to(scope)
        if any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
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
        # Cible résolue mais hors graphe — dossier exclu (.claude, .tmp, _legacy)
        # ou fichier hors racine (lien absolu vers un repo depuis une mémoire
        # native) : ni arête ni cassé.
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


def _project_scope(repo_path: str) -> Path:
    """Scope = dossier de mémoire native d'un repo (cf native_memory_dir).

    Si la mémoire native n'existe pas encore, retourne la cible canonique : le
    graphe se construit alors vide, sans erreur.
    """
    memory_dir = native_memory_dir.resolve(repo_path)
    if memory_dir is not None:
        return memory_dir
    project_dir, _ = native_memory_dir.resolve_project_dir(repo_path)
    return project_dir / "memory"


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


def resolve_name(g: Graph, query: str) -> list[str]:
    """
    Résout un nom ou chemin en liste de paths de nœuds.

    Matche (insensible à la casse) sur : chemin exact, stem du fichier, titre H1,
    ou topic du frontmatter. Retourne tous les nœuds correspondants (≥ 0).
    """
    q = query.strip().lower()
    if not q:
        return []
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

    Si le nom matche 0 ou plusieurs nœuds, retourne {"resolved": None, "candidates": [...]}
    (clés node/outgoing/incoming/linked_memories absentes). Si exactement 1 nœud,
    retourne la fiche complète. Les arêtes entrantes/sortantes incluent l'affinité
    (contrairement à impact, qui ne compte que les références structurelles).
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index de graphe structurel d'un workspace driven.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    project_help = (
        "Code repo path: graph its native memory dir "
        "(~/.claude/projects/<slug>/memory/) instead of --scope."
    )

    p_build = sub.add_parser("build", help="Construit le graphe et écrit le cache.")
    p_build.add_argument("--scope", type=Path, default=Path.cwd())
    p_build.add_argument("--project", default=None, help=project_help)

    p_impact = sub.add_parser("impact", help="Liens entrants vers un fichier/dossier.")
    p_impact.add_argument("target")
    p_impact.add_argument("--scope", type=Path, default=Path.cwd())
    p_impact.add_argument("--project", default=None, help=project_help)

    p_explain = sub.add_parser("explain", help="Fiche d'une entité + ses arêtes.")
    p_explain.add_argument("query")
    p_explain.add_argument("--scope", type=Path, default=Path.cwd())
    p_explain.add_argument("--project", default=None, help=project_help)

    p_path = sub.add_parser("path", help="Plus court chemin entre deux nœuds.")
    p_path.add_argument("node_a")
    p_path.add_argument("node_b")
    p_path.add_argument("--scope", type=Path, default=Path.cwd())
    p_path.add_argument("--project", default=None, help=project_help)

    p_check = sub.add_parser("check", help="Liens cassés + orphelins.")
    p_check.add_argument("--scope", type=Path, default=Path.cwd())
    p_check.add_argument("--project", default=None, help=project_help)

    args = parser.parse_args()
    scope = _project_scope(args.project) if args.project else args.scope.resolve()

    if args.command == "build":
        result = cmd_build(scope)
    elif args.command == "impact":
        result = cmd_impact(scope, args.target)
    elif args.command == "explain":
        result = cmd_explain(scope, args.query)
    elif args.command == "path":
        result = cmd_path(scope, args.node_a, args.node_b)
    elif args.command == "check":
        result = cmd_check(scope)
    else:  # pragma: no cover
        parser.error(f"unknown command: {args.command}")

    print(json.dumps(result, ensure_ascii=False, indent=2, default=_json_default))


if __name__ == "__main__":
    main()
