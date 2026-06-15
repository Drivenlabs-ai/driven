#!/usr/bin/env python3
"""
native_memory_dir.py — Résout le dossier de mémoire native Claude Code d'un repo.

La mémoire native (auto memory) d'un projet vit dans
    ~/.claude/projects/<slug>/memory/
où <slug> = chemin réel du repo, chaque '/' et '.' remplacés par '-'. Le chemin
absolu commençant par '/', le slug commence par '-'.

L'encodage n'est pas documenté et un bug ouvert (anthropics/claude-code#30828)
peut faire dériver le traitement des underscores : ne jamais s'y fier à l'aveugle.
La résolution canonicalise le chemin (realpath — les pôles d'un workspace peuvent
être des symlinks, et c'est le chemin réel qui dérive le slug), dérive les slugs
candidats, vérifie leur existence sur disque, et à défaut scanne
~/.claude/projects/ pour la correspondance robuste aux variantes '_'/'-'.

Usage :
    python native_memory_dir.py /path/to/repo            # imprime le dossier, ou rien
    python native_memory_dir.py /path/to/repo --create   # crée le dossier si absent
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def default_projects_root() -> Path:
    """Racine des projets Claude Code : ~/.claude/projects/."""
    return Path.home() / ".claude" / "projects"


def encode_slug(real_path: str) -> str:
    """Encode un chemin absolu réel en nom de dossier sous ~/.claude/projects/.

    Règle observable : chaque '/' et '.' devient '-' ; le reste est préservé.
    Ex : /Users/alex/Code/foo → -Users-alex-Code-foo.
    """
    return "".join("-" if c in "/." else c for c in real_path)


def canonical_path(repo_path: str | os.PathLike[str]) -> str:
    """Chemin réel canonique du repo : ~ développé, symlinks résolus.

    `os.path.realpath` résout les composants symboliques existants même si la
    feuille n'existe pas, ce qui couvre un repo référencé via un pôle symlinké
    (ex `Personal OS/Code/` → `/Users/.../Code/`).
    """
    return os.path.realpath(os.path.expanduser(str(repo_path)))


def candidate_slugs(real_path: str) -> list[str]:
    """Slugs candidats : l'encodage primaire, plus la variante '_' → '-'.

    La variante couvre le bug #30828 où les underscores du chemin sont
    sanitizés en tirets côté Claude Code.
    """
    primary = encode_slug(real_path)
    out = [primary]
    variant = primary.replace("_", "-")
    if variant != primary:
        out.append(variant)
    return out


def _norm(name: str) -> str:
    """Normalise un nom de dossier pour comparer underscores et tirets."""
    return name.replace("_", "-")


def _scan_existing(projects_root: Path, candidates: list[str]) -> Path | None:
    """Scanne projects_root pour un dossier correspondant à un candidat.

    Comparaison normalisée '_'/'-' : absorbe une dérive d'encodage des
    underscores sans dépendre d'un décodage exact (l'encodage étant lossy).
    """
    if not projects_root.is_dir():
        return None
    wanted = {_norm(c) for c in candidates}
    for entry in sorted(projects_root.iterdir()):
        if entry.is_dir() and _norm(entry.name) in wanted:
            return entry
    return None


def resolve_project_dir(
    repo_path: str | os.PathLike[str],
    projects_root: str | os.PathLike[str] | None = None,
) -> tuple[Path, bool]:
    """Résout le dossier projet ~/.claude/projects/<slug> d'un repo.

    Retourne (chemin, existe). Si aucun dossier existant n'est trouvé, le chemin
    est la cible canonique (slug primaire) avec existe=False, prête à créer.
    """
    root = Path(projects_root) if projects_root is not None else default_projects_root()
    real = canonical_path(repo_path)
    candidates = candidate_slugs(real)

    for slug in candidates:
        candidate = root / slug
        if candidate.is_dir():
            return candidate, True

    scanned = _scan_existing(root, candidates)
    if scanned is not None:
        return scanned, True

    return root / candidates[0], False


def resolve(
    repo_path: str | os.PathLike[str],
    projects_root: str | os.PathLike[str] | None = None,
    create: bool = False,
) -> Path | None:
    """Dossier de mémoire native (<projet>/memory) d'un repo.

    Lecture (create=False) : retourne le dossier s'il existe, sinon None — une
    mémoire native non encore peuplée n'est pas une erreur.
    Écriture (create=True) : crée le dossier (sous le projet existant s'il y en
    a un, sinon sous le slug canonique) et le retourne.
    """
    project_dir, exists = resolve_project_dir(repo_path, projects_root)
    memory_dir = project_dir / "memory"
    if create:
        memory_dir.mkdir(parents=True, exist_ok=True)
        return memory_dir
    if exists and memory_dir.is_dir():
        return memory_dir
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Résout le dossier de mémoire native Claude Code d'un repo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("repo_path", help="Chemin du repo (peut être symlinké).")
    parser.add_argument(
        "--create",
        action="store_true",
        help="Crée le dossier de mémoire s'il est absent.",
    )
    parser.add_argument(
        "--projects-root",
        default=None,
        help="Racine des projets Claude Code (défaut : ~/.claude/projects).",
    )
    args = parser.parse_args()

    memory_dir = resolve(args.repo_path, args.projects_root, create=args.create)
    if memory_dir is not None:
        print(memory_dir)


if __name__ == "__main__":
    main()
