# driven

Plugin compagnon pour workspaces collaboratifs Claude.

Maintient automatiquement un workspace dont le CLAUDE.md racine porte un frontmatter `space-type` :
mémoire timestampée, factualité en collectif, suivi des contributeurs, propagation
silencieuse, maintenance des fichiers normatifs.

## Install

```bash
claude plugin install driven@driven-alex-plugins
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

```bash
pip install rank-bm25 pyyaml
```

Marche en Claude Code et Claude Cowork (Bash + Python disponibles dans les deux).

## Crédits

Maintenu par Drivenlabs.
