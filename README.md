# driven

Plugin compagnon pour workspaces collaboratifs Claude.

Maintient automatiquement un workspace dont le CLAUDE.md racine porte un frontmatter `space-type` :
mémoire timestampée, factualité en collectif, suivi des contributeurs, propagation
silencieuse, maintenance des fichiers normatifs.

## Install

```bash
/plugin marketplace add drivenlabs-ai/plugins
/plugin install driven@drivenlabs-ai
```

Propage automatiquement à Claude Cowork (account-level).

## Activation

Le plugin s'active dès qu'il détecte un CLAUDE.md racine avec `space-type` dans le path remonté depuis le cwd. Pas de configuration locale requise.

En mode universel, les patterns proactifs (setup-dossier, capitalise-workflow) et la doctrine AskUserQuestion s'activent partout, pas seulement dans les workspaces driven.

## Commande slash

```
/driven                    # récap contexte + actions proposées
/driven [intention en NL]  # ex: « retiens que Laurent a changé le tarif »
/driven search "query"     # recherche mémoire (BM25)
```

Rarement tapé explicitement, le plugin est trigger-driven (création de fichier,
demande de retenir une info, modification d'un fichier de règle).

## Dépendances Python (recherche mémoire)

Le script de recherche mémoire requiert `rank-bm25` et `pyyaml` dans l'environnement Python :

```bash
uv pip install rank-bm25 pyyaml
```

Pour le développement (tests), l'environnement est managé via `pyproject.toml` + `uv.lock` :

```bash
uv sync
```

Marche en Claude Code et Claude Cowork (Bash + Python disponibles dans les deux).

## Publier une nouvelle version

Le plugin est servi par le marketplace `drivenlabs-ai/plugins`, qui référence ce repo **sans version épinglée** : la version installée vient du champ `version` de `.claude-plugin/plugin.json` sur `main` (à défaut, le SHA du commit). Bumper ce champ puis merger sur `main` suffit à publier — aucune édition du `marketplace.json` ni de tag/release.

Pour qu'une session récupère la nouvelle version :

```
/plugin marketplace update drivenlabs-ai
/reload-plugins
```

- `/plugin marketplace update` re-fetch `main` et bumpe le plugin — c'est l'étape qui met à jour le cache.
- `/plugin install driven@drivenlabs-ai` sur un plugin déjà installé est un no-op : inutile pour mettre à jour.
- `autoUpdate: true` ne se déclenche qu'au démarrage de session ; la commande ci-dessus force la mise à jour immédiatement.

Vérifier la version active : le champ `installPath` de `~/.claude/plugins/installed_plugins.json` doit pointer vers `…/cache/drivenlabs-ai/driven/<version>`.

Pour figer les versions servies (releases stables plutôt que « dernier `main` »), ajouter un champ `"version"` à l'entrée `driven` du `marketplace.json` de `drivenlabs-ai/plugins` — au prix de le bumper à chaque release.

## Crédits

Maintenu par Drivenlabs.
