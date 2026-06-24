# recuperation-contexte : Charger le contexte d'un sujet avant de bosser dessus

Avant de commencer à travailler sur un sujet, Claude rassemble en une passe le contexte qui le rend pertinent : cadre normatif, contexte interne du workspace, canaux externes pointés par cet interne. Démarrer informé évite de raisonner depuis le seul message courant — proposer ce qui a déjà été écarté, contredire une décision documentée, refaire un travail entamé.

## Quand cette ref s'active

Signal central : **une intention de démarrer ou reprendre un travail sur un sujet ou un dossier.** Les formulations varient — « récupère le contexte », « charge le contexte », « prends connaissance du dossier X », « reprends le travail sur X », « on attaque X » — ou toute autre tournure équivalente. C'est l'intention qui déclenche, pas une formule figée. Action explicite équivalente : `/driven context <sujet>` (`interface-cli.md`).

En début de session (premiers tours de la conversation — seuil défini au §2 du SKILL.md), le contexte du sujet pas encore chargé, ce réflexe est prioritaire : dès que user signale le sujet sur lequel il veut travailler, prendre connaissance du contexte avant de produire, sans attendre une demande explicite. Démarrer informé prime sur une réponse immédiate hors-sol.

Proportionner la passe à l'intention :

- Démarrage ou reprise de travail sur un sujet → passe complète.
- Question rétrospective ciblée (« on en était où sur X ? ») → search ciblé suffit (`comprehension-contextuelle.md`), pas la passe complète.
- Demande triviale orthogonale à tout dossier → pas de passe.
- Sujet déjà chargé en session (suite de conversation) → pas de re-chargement.

Elle orchestre les deux patterns de lecture qu'elle ne remplace pas — `lecture-arborescente.md` (chargement large d'un dossier) et `comprehension-contextuelle.md` (pré-trigger ciblé avant une action) — et ajoute l'étape canaux externes.

## Objectif de la passe

Les axes ci-dessous sont les graines d'une passe ouverte, pas une checklist fermée : Claude détermine ce qui fait sens pour le sujet, au-delà de ce qui est listé.

### Cadre normatif

Remonter la cascade des fichiers normatifs pertinents au scope (CLAUDE.md racine et sous-dossiers, RULES / CONTRIBUTING / ME / SOUL / ABOUT selon l'espace), via la cascade `@` et `lecture-arborescente.md`. Le cadre avant le détail : sans lui, le contexte chargé n'est pas interprété dans les bonnes conventions.

### Contexte interne du workspace

Le dossier du sujet : conventions, dernières mémoires, fichiers thématiques (`lecture-arborescente.md`). Puis le ciblage du sujet précis : search BM25 sur les mémoires (`scripts/search_memories.py`), graphe d'entités si des entités structurent le sujet (`scripts/graph.py`), fiches contact liées (`comprehension-contextuelle.md`).

### Canaux externes pointés par l'interne

Quand le contexte interne cite une source hors workspace — thread Gmail (Message-ID), URL, document, repo code (champ `code-repo`, cf `memoire-projet-code.md`), transcript — aller la chercher quand elle éclaire le sujet. La pertinence se juge sur le sujet courant, pas sur la présence du pointeur : un lien cité ne s'ouvre pas s'il n'apporte rien à la tâche.

### Tout le reste qui fait sens

Si un autre angle rend Claude plus pertinent (RDV à venir sur le sujet, état d'un projet code lié, dossier dont dépend le sujet, ou toute autre source pertinente), le charger. Le périmètre est ouvert ; le seul garde-fou est la pertinence au sujet.

## Profondeur : pertinence, pas exhaustivité

La passe charge ce qui sert le sujet, pas tout ce qui existe. Une fiche, quelques mémoires récentes et une source externe directement liée suffisent dans la plupart des cas (`comprehension-contextuelle.md` §anti-pattern sur-charge). Si le sujet est large et que beaucoup de contexte est utile, déléguer l'exploration à un sub-agent (Code) plutôt que saturer la session principale.

## Restitution

Synthèse NL de l'état des lieux, jamais un dump du contenu chargé : ce qu'on sait du sujet, les décisions passées, ce qui est en cours, les sources clés liées avec liens markdown pour le détail. Pas de description de la machinerie de chargement (format de `comprehension-contextuelle.md` §restitution). Terminer par l'amorce de travail : ce que user voulait faire sur le sujet, désormais informé.

## Exclusion : mode routine

Ne s'active pas en mode routine (§6.3 du SKILL.md) : un agent autonome charge le contexte dont sa tâche a besoin sans qu'un user le lui demande.
