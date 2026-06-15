"""Tests du résolveur de dossier de mémoire native (native_memory_dir.py)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import native_memory_dir as nmd

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "native_memory_dir.py"


def test_encode_slug_basique():
    assert nmd.encode_slug("/Users/alex/Code/foo") == "-Users-alex-Code-foo"


def test_encode_slug_remplace_les_points():
    # '/' et '.' deviennent tous deux '-' : /.claude → --claude.
    assert nmd.encode_slug("/Users/alex/.claude/x") == "-Users-alex--claude-x"


def test_encode_slug_preserve_les_tirets_existants():
    assert nmd.encode_slug("/a/drivenlabs-ai/driven") == "-a-drivenlabs-ai-driven"


def test_candidate_slugs_avec_underscore():
    cands = nmd.candidate_slugs("/a/b_c")
    assert cands == ["-a-b_c", "-a-b-c"]


def test_candidate_slugs_sans_underscore():
    assert nmd.candidate_slugs("/a/bc") == ["-a-bc"]


def test_resolve_project_dir_slug_primaire(tmp_path):
    projects = tmp_path / "projects"
    repo = tmp_path / "repo"
    repo.mkdir()
    slug = nmd.encode_slug(nmd.canonical_path(repo))
    (projects / slug).mkdir(parents=True)

    resolved, exists = nmd.resolve_project_dir(repo, projects)
    assert exists is True
    assert resolved == projects / slug


def test_resolve_project_dir_variante_underscore(tmp_path):
    # Le projet sur disque a les underscores convertis en tirets (bug #30828).
    projects = tmp_path / "projects"
    repo = tmp_path / "my_repo"
    repo.mkdir()
    real = nmd.canonical_path(repo)
    variant = nmd.encode_slug(real).replace("_", "-")
    (projects / variant).mkdir(parents=True)

    resolved, exists = nmd.resolve_project_dir(repo, projects)
    assert exists is True
    assert resolved == projects / variant


def test_resolve_project_dir_absent_retourne_cible_canonique(tmp_path):
    projects = tmp_path / "projects"
    projects.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    slug = nmd.encode_slug(nmd.canonical_path(repo))

    resolved, exists = nmd.resolve_project_dir(repo, projects)
    assert exists is False
    assert resolved == projects / slug


def test_scan_existing_normalise_underscore_et_tiret(tmp_path):
    projects = tmp_path / "projects"
    # Mélange : un underscore conservé, un converti — n'est aucun candidat exact
    # mais normalise vers le même nom.
    (projects / "-a-b_c-d").mkdir(parents=True)
    found = nmd._scan_existing(projects, ["-a-b_c_d", "-a-b-c-d"])
    assert found == projects / "-a-b_c-d"


def test_resolve_lecture_dossier_existant(tmp_path):
    projects = tmp_path / "projects"
    repo = tmp_path / "repo"
    repo.mkdir()
    slug = nmd.encode_slug(nmd.canonical_path(repo))
    mem = projects / slug / "memory"
    mem.mkdir(parents=True)

    assert nmd.resolve(repo, projects) == mem


def test_resolve_lecture_sans_dossier_memory_retourne_none(tmp_path):
    projects = tmp_path / "projects"
    repo = tmp_path / "repo"
    repo.mkdir()
    slug = nmd.encode_slug(nmd.canonical_path(repo))
    (projects / slug).mkdir(parents=True)  # projet existe, mais pas de memory/

    assert nmd.resolve(repo, projects) is None


def test_resolve_lecture_rien_retourne_none(tmp_path):
    projects = tmp_path / "projects"
    projects.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    assert nmd.resolve(repo, projects) is None


def test_resolve_create_cree_le_dossier(tmp_path):
    projects = tmp_path / "projects"
    repo = tmp_path / "repo"
    repo.mkdir()
    slug = nmd.encode_slug(nmd.canonical_path(repo))

    mem = nmd.resolve(repo, projects, create=True)
    assert mem == projects / slug / "memory"
    assert mem.is_dir()


def test_resolve_create_sous_projet_existant_sans_fragmenter(tmp_path):
    # Un projet variante existe déjà : l'écriture s'y fait, pas sous un nouveau slug.
    projects = tmp_path / "projects"
    repo = tmp_path / "my_repo"
    repo.mkdir()
    variant = nmd.encode_slug(nmd.canonical_path(repo)).replace("_", "-")
    (projects / variant).mkdir(parents=True)

    mem = nmd.resolve(repo, projects, create=True)
    assert mem == projects / variant / "memory"
    assert mem.is_dir()


def test_canonical_path_resout_les_symlinks(tmp_path):
    real = tmp_path / "realrepo"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    assert nmd.canonical_path(link) == nmd.canonical_path(real)


def test_resolve_suit_le_symlink_vers_le_chemin_reel(tmp_path):
    projects = tmp_path / "projects"
    real = tmp_path / "realrepo"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    slug = nmd.encode_slug(nmd.canonical_path(real))
    mem = projects / slug / "memory"
    mem.mkdir(parents=True)

    # Résolu via le symlink → trouve le dossier du chemin réel.
    assert nmd.resolve(link, projects) == mem


def test_cli_imprime_le_dossier_existant(tmp_path):
    projects = tmp_path / "projects"
    repo = tmp_path / "repo"
    repo.mkdir()
    slug = nmd.encode_slug(nmd.canonical_path(repo))
    mem = projects / slug / "memory"
    mem.mkdir(parents=True)

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--projects-root", str(projects)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == str(mem)


def test_cli_silencieux_si_absent(tmp_path):
    projects = tmp_path / "projects"
    projects.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--projects-root", str(projects)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == ""


def test_cli_create(tmp_path):
    projects = tmp_path / "projects"
    repo = tmp_path / "repo"
    repo.mkdir()
    slug = nmd.encode_slug(nmd.canonical_path(repo))

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--projects-root", str(projects), "--create"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == str(projects / slug / "memory")
    assert (projects / slug / "memory").is_dir()
