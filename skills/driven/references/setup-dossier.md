# setup-dossier : Mise en place proactive d'un dossier sans contexte

Quand Claude ouvre un dossier nu — sans `CLAUDE.md`, sans mémoire, sans signal de structure — il est aveugle. Il devine au lieu de raisonner, et la prochaine session redémarre à zéro. Ce pattern détecte ces situations, propose une mise en place rapide, et laisse derrière lui un dossier qui parle de lui-même.

## Doctrine

Un dossier qui sert quelque chose mérite un minimum d'ancrage. Pas un setup lourd : un `CLAUDE.md` qui dit de quoi il s'agit, et un `memory/` si l'historique compte. C'est suffisant pour qu'un futur Claude (ou Alex lui-même dans deux mois) sache où il met les pieds.

Le maintien proactif d'un espace est un travail de fond du plugin. Mieux vaut poser 5 lignes utiles maintenant que laisser un dossier s'accumuler dans le flou et devoir le reconstruire plus tard. La prochaine session démarre avec contexte ou démarre aveugle — c'est ce moment qui décide.

## Quand cette ref s'active

Scope niveau 1 — **universel**. Active dans tout dossier ouvert dans Claude Code ou Cowork, pas seulement les workspaces driven (CLAUDE.md racine avec frontmatter `space-type`). Un dossier non-driven peut quand même mériter un setup minimal s'il est utilisé activement.

- cwd ou cible d'action dans un dossier sans CLAUDE.md.
- Création d'un nouveau dossier dans un workspace driven.
- Action Claude (Write / Read / Edit / Bash cd) dans un dossier qui passe pré-filtre technique ET échoue au jugement « ai-je de quoi m'orienter ? ».

## Trigger

| Type | Déclencheur |
|---|---|
| Auto | Action Claude (Write/Read/Edit/Bash `cd`) dans un dossier qui passe l'heuristique de manque de contexte ci-dessous |
| Explicite | Commande `/driven setup-dossier` |

## Heuristique de détection

### 1. Pré-filtre technique

Exclusions strictes — si l'une matche, silence immédiat, pas de proposition :

- Dossiers cachés : `.git/`, `.venv/`, `.claude/`, `.obsidian/`, `.vscode/`, `.idea/`, tout dossier commençant par `.`
- Dossiers techniques : `node_modules/`, `dist/`, `build/`, `__pycache__/`, `target/`, `out/`, `coverage/`, `.next/`
- Sous-dossiers de `memory/` (le `memory/` lui-même est touché par le pattern memory, pas par celui-ci)
- Dossiers d'archive : `_legacy/`, `_archived/`, `_archive/`, `.old/`, tout dossier préfixé `_`

Si l'un de ces filtres élimine le dossier, le pattern ne se déclenche jamais. Pas de question à se poser ensuite.

**Mode routine** : exclusion absolue. Si Claude tourne en mode autonome (sentinels `<<autonomous-loop>>` ou `<<autonomous-loop-dynamic>>` dans le prompt initial, tools `ScheduleWakeup`/`CronCreate` disponibles, sections « Autonomous loop check » dans le system prompt), ne jamais déclencher cette ref.

### 2. Jugement Claude

Si le pré-filtre laisse passer, auto-questionnement avant d'agir :

- *« Ai-je de quoi répondre intelligemment ici, ou je suis aveugle ? »*
- *« Un futur Claude qui ouvre ce dossier sans cette session saura-t-il ce qui se passe ? »*

Si Claude est confiant (il a le contexte par la conversation, ou le dossier est trivial), silence. Si le trouble persiste — le dossier semble actif mais sans repère structurant — proposition NL une seule fois.

Phrase type :

> Ce dossier est nu, je n'ai pas grand-chose pour me situer. Je te propose qu'on pose une structure rapide (un `CLAUDE.md` court + un `memory/` si pertinent). Tu veux qu'on fasse ça maintenant ?

## Workflow d'interview

Une fois la proposition NL acceptée, mini-interview via **AskUserQuestion** (3 à 5 questions, adaptatives selon le contexte). C'est l'outil qui convient ici : choix structurés, pas de friction texte libre, user répond vite.

Questions types, ordre adapté au signal :

1. **Nature du dossier** — client / projet interne / contenu / partenaire / dossier perso / autre.
2. **Contenu structurant attendu** — briefs, livrables, notes de RDV, scripts, doc technique.
3. **Besoin historique timestampé ici ?** — si oui, création de `memory/.gitkeep`.
4. **Sous-dossiers déjà prévus ?** — pour pré-câbler l'index du `CLAUDE.md`.

Si les réponses font apparaître naturellement des conventions ou workflows spécifiques à ce dossier, Claude propose immédiatement la création d'un `RULES.md` local avec ces conventions concrètes. Sinon, pas de question dédiée.

**Reformulation miroir avant écriture** :

> Pour résumer : ce dossier va contenir X, avec Y comme historique pertinent. C'est juste ?

Pas de validation = pas d'écriture. La reformulation évite de partir sur une mauvaise inférence.

## Fallback : /align

Si user accepte mais que la mini-interview reste floue (réponses ambiguës, *« j'sais pas trop »*, *« on verra plus tard »*, contradictions), basculer vers le skill `/align`. C'est conçu pour ce genre de cas où le contexte business mérite d'être clarifié en amont avant toute structuration.

## Outputs

Selon les réponses, création **minimale** :

- `CLAUDE.md` du dossier — toujours créé. Appliquer le test d'altitude (`gestion-contexte.md`) à son contenu : ce qui aide à viser le bon sous-dossier ou fichier sans l'ouvrir (routage) y reste, le reste descend d'un niveau. Plus l'index local. Reste ouvert, à enrichir au fil de l'usage.
- `memory/.gitkeep` — uniquement si la réponse à la question 3 est positive. Le dossier `memory/` lui-même se peuplera au fil des mémoires.

Pas de fichiers vides au-delà. Pas de `RULES.md` placeholder, pas de sous-dossiers anticipés, pas de templates non remplis. Ces éléments émergent au fil de l'usage par découpage progressif quand le besoin se manifeste — pas avant.

## Anti-patterns

- **Re-proposer en boucle** : après un refus user sur ce dossier, silence jusqu'à action explicite (commande `/driven setup-dossier` ou nouvelle demande directe). Pas de nouvelle tentative à chaque action.
- **Spéculer sur la structure future** : ne pas créer de sous-dossiers anticipés *au cas où*. Le découpage émerge quand un besoin concret se manifeste, pas avant.
- **Déclencher sur dossier technique** : le pré-filtre est strict pour une raison. Si un doute, c'est probablement un dossier technique — ne pas déclencher.
- **Interrompre une tâche en cours** : si user demande quelque chose de précis dans un dossier nu, traiter la demande d'abord. Proposer le setup à la pause naturelle suivante, pas au milieu de l'action.

## Recap user

Une ligne, NL pur, sans jargon :

> OK, j'ai posé la structure de ce dossier.

Pas de chemin complet, pas de mention de `.gitkeep`, pas d'explication du pattern. Le user voit le dossier prêt et passe à la suite.
