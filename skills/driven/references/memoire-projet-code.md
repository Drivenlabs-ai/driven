# memoire-projet-code : Mémoires d'un projet code

Un projet code est un repo git hors workspace driven : aucun CLAUDE.md ancêtre ne porte de frontmatter `space-type`. Cette ref fixe où vivent les mémoires dans ce contexte ; le format des entrées reste celui de `memory.md`.

## Emplacement unique : `.memory/` à la racine du projet

Toutes les mémoires du projet — création comme lecture — vivent dans un seul dossier caché `.memory/` à la racine du repo (le dossier qui contient `.git`). Pas de `.memory/` par sous-dossier : contrairement à un workspace driven où chaque dossier thématique porte sa mémoire, un projet code est une unité cohérente — le repo entier est le périmètre thématique.

## Init systématique : dossier + gitignore, jamais l'un sans l'autre

À la première intervention dans un projet code dont le `.memory/` n'existe pas, l'initialiser : créer le dossier ET ajouter l'entrée `.memory/` au `.gitignore` du repo, dans le même geste. Les mémoires sont personnelles et épisodiques : elles ne se committent jamais, ne se poussent jamais — un repo se partage, peut devenir public, et une mémoire committée voyagerait avec lui.

La protection repose entièrement sur l'entrée `.gitignore` : avant chaque écriture dans `.memory/`, vérifier qu'elle est présente, la rétablir sinon.

## Création

Format d'entrée identique aux workspaces driven : naming `YYYY-MM-DD-HHMM-author-topic.md`, frontmatter inféré silencieusement, append-only, cross-link, recap minimal — tout vit dans `memory.md`. Seule différence : pas de choix de dossier cible (étape 2 du workflow de `memory.md`), c'est toujours `.memory/` racine.

Le test pivot s'applique inchangé : une convention durable du projet (stack, commandes, architecture, pièges connus) va dans le CLAUDE.md ou la doc du repo, pas en mémoire (cf `connaissance-vs-memoire.md`). La mémoire capte l'épisodique : décision datée, état d'une investigation, contexte d'un arbitrage technique, échange avec un client sur le projet.

## Lecture

À la reprise d'un sujet qui a pu laisser des traces — reprise de session, décision antérieure, bug déjà investigué, ou tout autre signal pertinent — lire les mémoires récentes de `.memory/` avant d'agir. Mêmes paliers de volume que l'étape 3 du workflow de `memory.md`.

## Sensibles

Même gitignorée, une mémoire reste sur la machine et dans le dossier du projet. Les 6 patterns sensibles de `memory.md` s'appliquent avant chaque écriture : un contenu sensible (RH, NDA, vie privée tiers, rémunération) va dans l'espace perso de l'utilisateur, pas dans le `.memory/` du projet.
