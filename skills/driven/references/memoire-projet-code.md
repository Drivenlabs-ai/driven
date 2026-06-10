# memoire-projet-code : Mémoires d'un projet code

Un projet code est un repo git hors workspace driven : aucun CLAUDE.md ancêtre ne porte de frontmatter `space-type`. Cette ref fixe où vivent les mémoires dans ce contexte ; le format des entrées reste celui de `memory.md`.

## Emplacement unique : `memory/` à la racine du projet

Toutes les mémoires du projet — création comme lecture — vivent dans un seul dossier `memory/` à la racine du repo (le dossier qui contient `.git`). Pas de `memory/` par sous-dossier : contrairement à un workspace driven où chaque dossier thématique porte sa mémoire, un projet code est une unité cohérente — le repo entier est le périmètre thématique. Créer le dossier à la première mémoire, jamais préventivement.

## Création

Format d'entrée identique aux workspaces driven : naming `YYYY-MM-DD-HHMM-author-topic.md`, frontmatter inféré silencieusement, append-only, cross-link, recap minimal — tout vit dans `memory.md`. Seule différence : pas de choix de dossier cible (étape 2 du workflow de `memory.md`), c'est toujours `memory/` racine.

Le test pivot s'applique inchangé : une convention durable du projet (stack, commandes, architecture, pièges connus) va dans le CLAUDE.md ou la doc du repo, pas en mémoire (cf `connaissance-vs-memoire.md`). La mémoire capte l'épisodique : décision datée, état d'une investigation, contexte d'un arbitrage technique, échange avec un client sur le projet.

## Lecture

À la reprise d'un sujet qui a pu laisser des traces — reprise de session, décision antérieure, bug déjà investigué, ou tout autre signal pertinent — lire les mémoires récentes de `memory/` avant d'agir. Mêmes paliers de volume que l'étape 3 du workflow de `memory.md`.

## Sensibles : jamais dans le repo

Un repo se pousse, se partage, peut devenir public ; une mémoire committée voyage avec lui. La détection des 6 patterns sensibles de `memory.md` s'applique avant chaque écriture : un contenu sensible (RH, NDA, vie privée tiers, rémunération) va dans l'espace perso de l'utilisateur, jamais dans le `memory/` du repo.
