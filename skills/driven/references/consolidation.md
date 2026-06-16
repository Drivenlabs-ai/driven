# consolidation : Mémoriser = capturer ET consolider l'espace

« Mémoriser » ne se réduit pas à créer une mémoire. Une session change l'état de l'espace : une convention évolue, un outil change, des fichiers naissent. Sans maintenance, un fait durable qui change laisse des traces obsolètes ailleurs — drift, contradictions, exploration future dégradée. Ce moteur transforme « mémorise » et la clôture de session en une passe qui laisse l'espace net : sans contradiction, lié, structuré pour un progressive disclosure propre, avec des mémoires auto-suffisantes sur leur provenance.

Le moteur orchestre des refs existantes ; il ne réécrit aucune de leurs règles.

## Points d'entrée

| Déclencheur | Périmètre de base |
|---|---|
| « mémorise / retiens / capture la progression / on a basculé X→Y » | le travail immédiat |
| Clôture de session (`cloture-session.md`) | la session entière |

**Profondeur proportionnelle au périmètre** (déterminé à l'étape 2) :

- Note triviale isolée, sans enjeu de cohérence (ex « retiens que John Doe préfère les calls le matin ») → chemin léger : mémoire écrite avec ses liens et sources évidents (étapes 1, 5, 6) + recap minimal. Pas de sweep.
- Changement à périmètre large (mode de travail, outil, instruction, fichier de contexte central) → les six étapes + remontée structurée.

Jamais en mode routine (détection : `session-handoff.md` §mode routine) : un agent autonome n'a personne à consulter.

## Forcing

Dès qu'une consolidation à périmètre large est engagée, créer un TaskCreate `Consolidation : revue des 6 étapes` avant tout wrap-up ; il passe à `completed` seulement après revue effective des six étapes. Sans ce forcing, la production d'un récap ou d'un prompt de reprise court-circuite la substance (aligné SKILL.md §7.2).

## Les six étapes

Ordre contraignant — chaque étape s'appuie sur la précédente. Une étape sans matière est un no-op silencieux.

1. **Quoi** — ce qui a été travaillé : mutations et envois de la période, via la trace des actions (`memory.md`).
2. **Périmètre** — local isolé (un dossier, un client) ou large (mode de travail, outil, instruction générale, fichier central) ? Flou → AskUserQuestion. Le périmètre fixe la profondeur (ci-dessus) et le scope (§Scoping).
3. **Drift** — dans le périmètre, ce qui doit bouger au-delà du travail lui-même pour rester cohérent. Repérer l'ancien état partout où il subsiste : recherche de la valeur/du terme + `graph.py impact` pour les références fichier (`graphe.md`).
4. **Structure** — faut-il restructurer le dossier pour ancrer ces mises à jour et fluidifier l'exploration future ? `audit-sections.md`, `decoupage-progressif.md`, test d'altitude de `gestion-contexte.md`.
5. **Pivot ou clean-slate** — la mémoire porte le pivot daté (append-only, jamais effacé) ; le fichier de connaissance est clean-slate (remplace, zéro trace de l'ancien). Le pivot vit dans la mémoire, pas dans le fichier : aucune lecture future ne voit deux valeurs en conflit.
6. **Liens** — internes (cross-link notes/mémoires/fichiers, `graph.py explain`) et provenance externe (`memory.md` §Sources). La mémoire reste auto-suffisante pour retracer ses sources.

## Scoping

Plafond par défaut : l'espace courant. Si le changement est clairement universel — mode de travail, outil, instruction générale —, le signaler et proposer d'élargir (autre espace driven, global `~/.claude`, skill). L'élargissement franchit une frontière : toujours sous validation explicite, jamais en silencieux. Dans la remontée, c'est une question dédiée (« ce changement touche aussi ton CLAUDE.md global, j'élargis ? »).

## Écriture vs proposition

- Note triviale isolée → écrite d'office (append-only) + recap minimal.
- Dès qu'il y a consolidation → rien n'est écrit avant validation, mémoire de synthèse incluse. Seules les cascades triviales restent silencieuses (last-updated, index, regen de liens après renommage : `propagation.md`).

## La remontée

Quand il y a de la consolidation à valider, un message scannable précède l'AskUserQuestion :

1. **Message** : l'arborescence du périmètre ; pour chaque fichier concerné, l'information touchée par le travail et la modification proposée ; l'arborescence cible si une restructuration est proposée.
2. **AskUserQuestion** groupé par cible cohérente (≤ 4 questions). Au-delà : « tout appliquer / je sélectionne / on passe en revue un par un ».
3. Élargissement de scope (§Scoping) → question dédiée.

Format des questions et batch : `askuserquestion.md`.

## Orchestration

Le moteur appelle, sans les réécrire : `scope-check` (périmètre, ancrage cwd), `memory` (format, trace, provenance), `connaissance-vs-memoire` (test pivot), `propagation` (cascades), `audit-sections` (contradictions), `decoupage-progressif` + `gestion-contexte` (structure, altitude), `graphe` / `graph.py` (impact, explain, check), `factualite` (shared), `links` (liens), `askuserquestion` (remontée).
