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
