#!/usr/bin/env python3
"""
search_memories.py — BM25 search across memory entries in a driven workspace.

Scans .md files with YAML frontmatter, ranks them against a query using 4 weighted
BM25 corpora (keywords ×3, topic+H1 ×2, preamble ×1, body ×1), outputs top N as JSON.

Usage:
    python search_memories.py "query expanded with synonyms" \\
        --scope=/path/to/scope --top=20 --format=json

The query should be pre-expanded with synonyms by the caller (Claude at runtime).
This script does no synonym expansion of its own — pure ranking.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import native_memory_dir

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML missing. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    print("ERROR: rank-bm25 missing. Run: pip install rank-bm25", file=sys.stderr)
    sys.exit(1)


# Field weighting — applied to per-field BM25 scores then summed.
WEIGHTS: dict[str, float] = {
    "keywords": 3.0,
    "topic_title": 2.0,
    "preamble": 1.0,
    "body": 1.0,
}

# Trivial stopwords (FR + EN). Kept minimal — rank-bm25 handles IDF.
STOPWORDS: set[str] = {
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "l",
    "et", "ou", "mais", "donc", "or", "ni", "car",
    "à", "au", "aux", "en", "dans", "sur", "pour", "par", "avec", "sans",
    "ce", "cet", "cette", "ces", "que", "qui", "quoi", "dont", "où",
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "at",
    "to", "for", "with", "by", "as", "is", "are", "was", "were",
    "this", "that", "these", "those", "it", "its",
}


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Extract YAML frontmatter from .md content.

    Returns (frontmatter_dict, body_after_frontmatter).
    If no valid frontmatter found, returns ({}, content).
    """
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


def extract_preamble(body: str) -> str:
    """
    Extract content of '## Contexte' section from a markdown body.

    Returns the section text (excluding the heading), up to the next '## ' or EOF.
    Returns '' if no '## Contexte' section found.
    """
    lines = body.split("\n")
    in_preamble = False
    preamble_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_preamble:
                # Reached next H2 — preamble ends here
                break
            # Match "## Contexte" case-insensitively
            if stripped[3:].strip().lower() == "contexte":
                in_preamble = True
                continue
        if in_preamble:
            preamble_lines.append(line)

    return "\n".join(preamble_lines).strip()


def extract_h1(body: str) -> str:
    """Extract first '# Title' line, returning the title text without the hash."""
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def tokenize(text: str) -> list[str]:
    """
    Lowercase, split on whitespace and punctuation, drop trivial stopwords.

    Returns a list of tokens. Empty list if text is empty.
    """
    if not text:
        return []
    # Lowercase + replace common punctuation with spaces
    cleaned = text.lower()
    for char in [",", ".", ";", ":", "!", "?", "(", ")", "[", "]",
                 "{", "}", '"', "'", "«", "»", "`", "/", "\\"]:
        cleaned = cleaned.replace(char, " ")
    tokens = cleaned.split()
    return [t for t in tokens if t and t not in STOPWORDS and len(t) > 1]


def parse_memory_file(filepath: Path) -> dict[str, Any] | None:
    """
    Parse a single .md memory file into a structured dict.

    Returns None if file has no valid frontmatter or fails to read.
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"WARN: skipped {filepath} ({e})", file=sys.stderr)
        return None

    fm, body = parse_frontmatter(content)

    keywords_raw = fm.get("keywords", [])
    if isinstance(keywords_raw, str):
        keywords_raw = [keywords_raw]
    elif not isinstance(keywords_raw, list):
        keywords_raw = []

    topic = str(fm.get("topic", ""))
    h1 = extract_h1(body)
    preamble = extract_preamble(body)

    # Body excluding preamble for separate scoring
    body_without_preamble = body.replace(preamble, "", 1) if preamble else body

    return {
        "path": filepath,
        "fm": fm,
        "keywords_tokens": tokenize(" ".join(str(k) for k in keywords_raw)),
        "topic_title_tokens": tokenize(f"{topic} {h1}"),
        "preamble_tokens": tokenize(preamble),
        "body_tokens": tokenize(body_without_preamble),
        "preamble_text": preamble,
        "topic": topic,
        "date": str(fm.get("date", "")),
        "type": str(fm.get("type", "")),
    }


def collect_memory_files(scope: Path) -> list[Path]:
    """
    Walk scope/**/*.md, return list of files in 'memory/' directories.

    A file is considered a memory entry if it lives inside a directory named
    'memory/' (case-insensitive). Other .md files (CLAUDE.md, RULES.md, etc.)
    are excluded.
    """
    if not scope.exists():
        print(f"ERROR: scope path does not exist: {scope}", file=sys.stderr)
        sys.exit(1)
    if not scope.is_dir():
        print(f"ERROR: scope must be a directory: {scope}", file=sys.stderr)
        sys.exit(1)

    files: list[Path] = []
    for md in scope.rglob("*.md"):
        # Skip files not in a memory/ directory
        if not any(p.name.lower() == "memory" for p in md.parents):
            continue
        files.append(md)
    return files


def search(scope: Path, query: str, top: int) -> list[dict[str, Any]]:
    """
    Main search logic.

    1. Collect memory files in scope/**/memory/*.md.
    2. Parse each into 4 token fields.
    3. Build 4 BM25 corpora (one per field).
    4. Tokenize query, rank docs against each corpus, sum weighted scores.
    5. Return top N as JSON-serializable dicts.
    """
    files = collect_memory_files(scope)
    if not files:
        return []

    docs: list[dict[str, Any]] = []
    for fp in files:
        parsed = parse_memory_file(fp)
        if parsed is not None:
            docs.append(parsed)

    if not docs:
        return []

    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    # Build 4 BM25 corpora (one per weighted field)
    fields = ["keywords_tokens", "topic_title_tokens", "preamble_tokens", "body_tokens"]
    weight_key_map = {
        "keywords_tokens": "keywords",
        "topic_title_tokens": "topic_title",
        "preamble_tokens": "preamble",
        "body_tokens": "body",
    }

    field_scores: dict[str, list[float]] = {}
    for field in fields:
        corpus = [doc[field] if doc[field] else [""] for doc in docs]
        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(query_tokens)
        field_scores[field] = list(scores)

    # Aggregate weighted scores per doc
    results: list[dict[str, Any]] = []
    for i, doc in enumerate(docs):
        total = sum(
            field_scores[field][i] * WEIGHTS[weight_key_map[field]]
            for field in fields
        )
        if total <= 0:
            continue
        results.append({
            "path": str(doc["path"].relative_to(scope) if doc["path"].is_relative_to(scope) else doc["path"]),
            "score": round(total, 3),
            "type": doc["type"],
            "date": doc["date"],
            "preamble": doc["preamble_text"],
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="BM25 search across memory entries in a driven workspace.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "query",
        help="Search query (pre-expanded with synonyms by caller).",
    )
    parser.add_argument(
        "--scope",
        type=Path,
        default=Path.cwd(),
        help="Directory to scan recursively for memory/*.md files (default: cwd).",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Code repo path: search its native memory dir "
        "(~/.claude/projects/<slug>/memory/) instead of --scope. "
        "Empty result if the repo has no native memory yet.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of top results to return (default: 20).",
    )
    parser.add_argument(
        "--format",
        choices=["json"],
        default="json",
        help="Output format (default: json).",
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparse exits with 2 on usage errors — preserve
        sys.exit(2 if e.code == 2 else 0)

    if args.project:
        memory_dir = native_memory_dir.resolve(args.project)
        if memory_dir is None:
            print(json.dumps([], ensure_ascii=False, indent=2))
            return
        scope = memory_dir
    else:
        scope = args.scope.resolve()
    results = search(scope, args.query, args.top)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
