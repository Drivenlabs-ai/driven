# Design — Moteur de consolidation driven

Date : 2026-06-16. Statut : design validé, prêt pour le plan d'implémentation.

## Problème

« Mémoriser » est aujourd'hui compris comme « créer une mémoire ». Or une session de travail change l'état de l'espace : des conventions évoluent, des outils changent, des fichiers se créent. Le plugin capture bien l'épisodique (mémoires timestampées, précédence par le tri lexico) mais **n'est pas instruit pour maintenir proactivement l'espace** : un fait durable qui change (ex : l'outil de design passe de Python à JavaScript) laisse des traces obsolètes ailleurs, et rien ne déclenche un audit ciblé. Claude distingue faiblement mémoire et autres markdown.

Conséquence : drift d'information, contradictions latentes, exploration future dégradée.

## Objectif

Chaque session — ou chaque « mémorise » à enjeu — laisse un espace **net** : sans contradiction, sans ambiguïté, avec des liens clairs entre fichiers, une structure pensée pour un progressive disclosure optimal, et une **vue complète de chaque mémoire** (contenu + d'où vient l'info + de quoi la retrouver).

« Mémoriser » devient donc : créer la mémoire **et** consolider ce qui doit l'être suite au travail.

## Le moteur — `consolidation.md` (nouveau ref)

Un ref-moteur unique définit le raisonnement de consolidation. Il **orchestre** des refs existantes, il ne redéfinit aucune de leurs règles (Loi 11 de `/writing-prompts`).

### Points d'entrée

| Déclencheur | Scope |
|---|---|
| « mémorise / retiens / capture la progression / on a basculé X→Y » | le travail immédiat |
| `cloture-session.md` (fin de session) | la session entière |

`cloture-session.md` est refondu en **point d'entrée** : ses 4 phases (capture / consolidation / structuration / audit) deviennent un appel au moteur avec scope = session, suivi du handoff optionnel.

### Profondeur proportionnelle au périmètre

- **Note triviale isolée** (sans enjeu de cohérence, ex « retiens que John Doe préfère les calls le matin ») → chemin léger : mémoire écrite avec ses liens et sources évidents (étapes 1, 5, 6) + recap minimal. Pas de sweep de cohérence (on saute les étapes 3 drift et 4 structure, et l'escalade).
- **Changement à périmètre large** (mode de travail, outil, instruction, fichier central) → les 6 étapes + remontée.

### Exclusion

Jamais en mode routine (détection : `session-handoff.md` §mode routine). Pas d'escalade sans humain.

## Les 6 étapes du moteur

Déroulées dans l'ordre ; une étape sans matière est un no-op silencieux.

1. **Quoi** — ce qui a été travaillé : mutations et envois de la session, via la *trace des actions* de `memory.md`.
2. **Périmètre** — local isolé (un dossier/client) vs large (mode de travail, outil, instructions générales, fichiers de contexte centraux). Si flou → AskUserQuestion. Le périmètre détecté pilote la profondeur (cf ci-dessus) et le scope (cf §Scoping).
3. **Drift** — dans le périmètre, ce qui doit bouger au-delà du travail lui-même pour rester cohérent. Détection : balayage de l'ancien état (grep valeur/contenu) + `graph.py impact` pour les références fichier. Aucun outil nouveau requis.
4. **Structure** — faut-il restructurer le dossier pour ancrer ces mises à jour et fluidifier l'exploration future ? Via `audit-sections.md`, `decoupage-progressif.md`, test d'altitude de `gestion-contexte.md`.
5. **Pivot vs clean-slate** — pour chaque changement : la **mémoire** porte le pivot daté (append-only, jamais effacé) ; le **fichier de connaissance** est clean-slate (remplace, zéro trace de l'ancien). Le pivot vit dans la mémoire, jamais dans le fichier → aucune lecture future ne voit deux valeurs en conflit.
6. **Liens** — internes (cross-link notes/mémoires/fichiers, `graph.py`) **et provenance externe** (cf §Provenance).

## Scoping

Plafond par défaut = **espace courant**. Si le changement est clairement universel (mode de travail, outil, instruction générale), Claude le signale et **propose d'élargir** (autre espace driven, global `~/.claude`, skill) — jamais sans validation explicite, jamais en silencieux. L'élargissement est une question dédiée dans la remontée (« ça touche aussi ton CLAUDE.md global, j'élargis ? »).

## Écriture vs proposition

- Note triviale isolée → **écrite** d'office (append-only) + recap minimal.
- Dès qu'il y a consolidation (périmètre large) → **tout est proposé avant écriture**, mémoire de synthèse incluse. Rien n'est appliqué avant validation. Les cascades triviales (last-updated, index, regen de liens après renommage) restent silencieuses (`propagation.md`).

## La remontée (livrable user-facing)

Quand il y a consolidation à valider :

1. **Message scannable** : arborescence du périmètre ; pour chaque fichier → l'information concernée par le travail + la modification proposée ; arborescence cible si restructuration.
2. **AskUserQuestion groupé** par cible cohérente (≤ 4 questions). Au-delà → options « tout appliquer / je sélectionne / revue 1 par 1 ».
3. Élargissement de scope → question dédiée.

## Provenance — format mémoire (`memory.md` enrichi)

Une mémoire est auto-suffisante pour retracer ses sources. Représentation :

- **Liens inline** dans `## Notes` au fil des mentions (lecture fluide), internes et externes.
- **Section `## Sources` dédiée** (quand des sources/outils externes sont en jeu) qui agrège tous les pointeurs localisables :
  - documents externes : Drive, lien de mail (permalien / Message-ID), doc partagé, URL hors Personal OS ;
  - **scripts/outils utilisés + leur chemin**, si des scripts ont servi dans la session ;
  - autres pointeurs de retour à l'information (ID document, etc.).

Le format des liens externes suit `/gws` (autorité pour bâtir un permalien Gmail, une URL Drive/Docs propre) — consulté à l'implémentation. La section `## Sources` garantit la vue d'ensemble ; l'inline garde le confort de lecture.

Distinction avec la *trace des actions* (déjà dans `memory.md`) : la trace dit ce que la session **a fait** (fichiers créés/supprimés, éléments envoyés) ; `## Sources` dit **d'où vient l'info et comment la retrouver**. Un élément envoyé apparaît naturellement dans les deux (la trace le mentionne, `## Sources` porte son lien localisable).

## Orchestration (refs appelées, non réécrites)

`scope-check` (périmètre + ancrage cwd) · `memory` (format, trace, provenance) · `propagation` (cascades) · `audit-sections` (contradictions) · `decoupage-progressif` + `gestion-contexte` (structure, altitude) · `graphe`/`graph.py` (impact, explain, check) · `connaissance-vs-memoire` (test pivot) · `factualite` (shared) · `links` (liens) · `cloture-session` (point d'entrée session).

## Câblage et fichiers touchés

- **Nouveau** : `references/consolidation.md`.
- **Édités** :
  - `memory.md` — section `## Sources` (provenance + scripts/chemins) ; renvoi au moteur pour le sweep.
  - `cloture-session.md` — délègue au moteur (scope session) + handoff optionnel.
  - `SKILL.md` — déclencheur §6.1 (« mémorise » charge `consolidation.md` ; nouvelles phrases « capture la progression », « consolide », signaux de changement durable) ; §6.2 (hook consolidation sur signal d'universalité) ; liste §12.
  - `routage.md` — pointeur vers le moteur sur la ligne mémoire.
- **Pas de nouveau script** : drift = grep (valeur) + `graph.py impact` (fichiers).
- Bump version plugin.

## Vérification

Pas de test automatique (comportement de jugement du modèle). Validation par scénarios :

- « on passe l'outil de design de Python à JS » → message structuré (arbo + fichiers impactés + propositions) puis AskUserQuestion groupé ; les fichiers obsolètes sont ciblés.
- « retiens X » trivial → écrit en silencieux, pas de sweep.
- Mémoire issue d'un mail → porte le permalien dans `## Sources` ; mémoire d'une session avec script → porte le chemin du script.
- Changement universel → propose l'élargissement de scope sous confirmation, jamais en silencieux.

La suite `pytest` des scripts reste verte (scripts non touchés).

## Hors-scope

- Pas d'automatisation du contenu des updates : le moteur propose, l'humain tranche (sauf cascades triviales).
- Pas de scan préventif périodique de l'espace (la consolidation est déclenchée, pas un rituel de fond).
- Pas de nouvelle détection cross-machine ni d'indexation persistante du drift.
