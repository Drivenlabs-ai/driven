# memoire-projet-code : Mémoire d'un projet code dans la mémoire native du repo

Un projet code est un repo git hors workspace driven : aucun CLAUDE.md ancêtre ne porte de frontmatter `space-type`. Cette ref fixe où vivent ses mémoires et comment y accéder ; le format des entrées reste celui de `memory.md`.

## Emplacement : la mémoire native du repo

Les mémoires d'un projet code vivent dans la mémoire native de Claude Code pour ce repo : `~/.claude/projects/<slug>/memory/`. Le dossier est hors du repo et machine-local — une mémoire n'y est donc jamais committée ni poussée par construction, alors qu'un repo se partage et peut devenir public.

Un seul dossier sert tout le repo : toutes les worktrees et sous-dossiers d'un même repo partagent cette mémoire native. Le repo entier est le périmètre thématique, pas de mémoire par sous-dossier.

## Résolution du chemin

Le `<slug>` encode le chemin réel du repo. L'encodage n'est pas documenté et peut dériver : ne jamais le dériver à la main. Résoudre le dossier via le helper, qui canonicalise le chemin (realpath — un repo atteint via un pôle symlinké, ex `Personal OS/Code/`, dérive son slug du chemin réel), vérifie l'existence et scanne en repli :

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/native_memory_dir.py" <repo>           # lecture : imprime le dossier, ou rien
python "${CLAUDE_PLUGIN_ROOT}/scripts/native_memory_dir.py" <repo> --create  # écriture : crée le dossier et l'imprime
```

Un dossier absent signifie « rien mémorisé encore », pas une erreur.

## Création

Format d'entrée identique aux workspaces driven : naming `YYYY-MM-DD-HHMM-author-topic.md`, frontmatter inféré, append-only, cross-link, trace des actions, recap minimal — tout vit dans `memory.md`. Deux spécificités :

- Pas de choix de dossier cible (étape 2 du workflow de `memory.md`) : c'est le dossier natif résolu (`--create`).
- Les liens vers des fichiers du repo sont des chemins absolus : la mémoire vit hors de l'arbre du repo, un chemin relatif ne porterait pas.

Le test pivot s'applique inchangé : une convention durable du projet (stack, commandes, architecture, pièges connus) va dans le CLAUDE.md ou la doc du repo, pas en mémoire (`connaissance-vs-memoire.md`). La mémoire capte l'épisodique : décision datée, état d'une investigation, contexte d'un arbitrage technique, échange avec un client sur le projet.

## Lecture

À la reprise d'un sujet susceptible d'avoir laissé des traces — reprise de session, décision antérieure, bug déjà investigué, ou tout autre signal pertinent — lire la mémoire native du repo avant d'agir : les entrées driven datées comme le `MEMORY.md` natif (index que Claude Code entretient seul) et ses fichiers-sujets. Paliers de volume : étape 3 du workflow de `memory.md`. Recherche ciblée et graphe sur cette mémoire via le flag `--project` :

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/search_memories.py" "query" --project <repo>
python "${CLAUDE_PLUGIN_ROOT}/scripts/graph.py" explain "entité" --project <repo>
```

## Pont avec un projet d'espace driven

Un même projet peut vivre en double : côté business dans un espace driven, côté technique dans un repo code. Le doc du projet, côté espace driven, déclare son repo associé via le champ `code-repo` (`frontmatter.md`) et une mention lisible dans le corps.

Quand Claude lit le contexte d'un projet d'espace driven qui porte `code-repo`, il lit aussi la mémoire native de ce repo (résolue via le helper) : le contexte technique rejoint le contexte business. Si un projet a clairement un repo associé sans que `code-repo` soit renseigné, proposer de l'ajouter (grammaire de proposition : `links.md`).

## Sensibles

La mémoire native est machine-locale mais reste sur disque. Les 6 patterns sensibles de `memory.md` s'appliquent avant chaque écriture : un contenu sensible (RH, NDA, vie privée tiers, rémunération) va dans l'espace perso de l'utilisateur, pas dans la mémoire native du repo.
