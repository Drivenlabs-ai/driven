# connaissance-vs-memoire : Principe pivot du routage de l'information

Avant la table de routage (`routage.md`), avant le workflow de création d'une mémoire (`memory.md`), un seul test décide où va l'information : **est-ce que c'est vrai demain ?**

Ce fichier verbalise le principe que driven applique implicitement partout. Sa lecture explicite garantit que Claude raisonne correctement même quand un cas n'est pas dans la table à 10 lignes.

## Le test pivot

> **Est-ce que c'est vrai demain ?**
>
> - **Oui** → fichier local (CLAUDE.md, RULES.md, ME.md, SOUL.md, document métier, fiche contact, brief client, etc.)
> - **Non, c'est ce qui s'est passé** → mémoire timestampée dans le `memory/` du dossier thématique

Une connaissance est **stable** : elle décrit une convention, une identité, un état durable du monde. Une mémoire est **épisodique** : elle fige un événement, une décision, une interaction à un instant T.

Le test est universel. Une convention de pricing applicable à chaque devis est vraie demain (fichier). Un accord pricing passé avec Laurent sur un projet précis ne l'est pas (mémoire — il documente que cette décision a été prise ce jour-là, pas qu'elle régit toujours).

## Trois principes fondateurs

### 1. Vrai demain ?

Test universel pour router connaissance vs mémoire. Quand Claude est sur le point d'écrire quelque chose, il se pose la question avant de choisir la cible. Si l'information décrit un comportement durable du système ou du user, c'est de la connaissance. Si elle décrit un événement révolu ou une décision contextuelle, c'est une mémoire.

Cas tordu courant : « on a décidé que désormais tous les devis Olenbee suivent la structure X ». Deux faits cohabitent. La décision (« on a décidé ce jour-là ») est une mémoire timestampée. La convention (« désormais on fait X ») est une connaissance qui va dans le RULES ou CONTRIBUTING du dossier. Faire les deux. Pas de choix forcé.

### 2. SAVOIR vs FAIRE

Un workflow répétitif n'est ni une connaissance ni une mémoire — c'est un skill custom (ou une command). Trois destinations possibles selon la nature de l'information :

- **Contexte, règles, conventions** (du SAVOIR) → fichier normatif (CLAUDE.md, RULES.md, CONTRIBUTING.md).
- **Workflow déclenché explicitement par user** (du FAIRE sur demande) → command.
- **Workflow activé automatiquement par un signal** (du FAIRE en autonomie) → skill.

Quand user décrit une tâche qu'il va refaire avec des variations (« à chaque devis envoyé j'aimerais que tu fasses X »), router vers `/skill-creator` plutôt que vers un fichier (cf `routage.md` cas 7 + `skill-creator-routing.md`).

### 3. Text > Brain

Préférer le fichier local quand l'information est stable. Le contexte de Claude est limité, le fichier ne l'est pas. Une connaissance bien rangée dans un fichier reste accessible partout, indexée par `routage.md`, lue automatiquement par le plugin selon le déclencheur.

Concrètement : quand user dit *« retiens ça »* sur une information stable (préférence durable, convention, identité), router vers le fichier local concerné, pas vers une mémoire. La mémoire timestampée capture le moment où la préférence a été exprimée — utile pour la traçabilité — mais le fichier reste la source de vérité.

## Comment Claude raisonne

Avant d'écrire, Claude pose mentalement trois questions dans cet ordre :

1. **Est-ce un workflow répétable ?** Si oui → `/skill-creator` (FAIRE). Stop.
2. **Sinon, est-ce vrai demain ?** Si oui → fichier local (SAVOIR stable). Identifier le fichier via `routage.md`.
3. **Sinon → mémoire timestampée.** Identifier le dossier via `memory.md` + `scope-check.md`.

L'ordre compte. Une convention durable mal routée en mémoire fige une règle à une date alors qu'elle devrait être lue à chaque session. Un workflow mal routé en CLAUDE.md alourdit le contexte sans automatiser le geste.

## Mapping vers la structure driven

Driven a déjà les deux mondes structurellement :

- **Fichiers normatifs** (CLAUDE.md, RULES.md, ME.md, SOUL.md, VOICE.md, ABOUT.md, CONTRIBUTING.md, documents métier) — chargés automatiquement par cascade, source de vérité stable.
- **Dossiers `memory/`** — entrées timestampées append-only, lues à la demande, historique factuel.

La table de `routage.md` (10 cas) est la **déclinaison opérationnelle** du test pivot pour les situations courantes. Quand un cas n'est pas dans la table ou semble ambigu, revenir au test pivot.

## Anti-patterns

- **Tout pousser en mémoire** : confortable parce que sans validation, mais finit en stack épisodique qui ne se charge jamais à la session suivante. Une convention durable doit aller en fichier.
- **Tout pousser en fichier** : confortable parce que toujours chargé, mais alourdit le contexte et fige des décisions ponctuelles comme des règles. Un événement révolu doit aller en mémoire.
- **Dupliquer entre les deux** : la décision est mémorisée *et* la convention qui en découle est inscrite — c'est normal et complémentaire, ce n'est pas une duplication. Duplication = même contenu, même nature, à deux endroits. Cohabitation = deux contenus différents qui pointent l'un vers l'autre.
- **Confondre traçabilité et règle** : « le 27/01 on a décidé que X » est une mémoire (traçabilité). « On fait X » est une connaissance (règle). Les deux écrits, liés l'un à l'autre.

## Cas tordus

### « Retiens que je préfère désormais Notion à Linear »

Signal d'universalité (« désormais »). C'est une convention durable du user → fichier (ME.md ou un sous-fichier de préférences outils). Une mémoire timestampée peut être créée en complément pour tracer le moment du changement de préférence, avec lien vers le fichier mis à jour.

### « On a parlé avec Laurent du pricing, il valide 8K »

Événement timestampé → mémoire dans `Clients/Olenbee/memory/`. Le fait que le pricing soit à 8K est une donnée qui appartient à ce projet précis, pas une convention générale.

### « Pour tous les devis désormais on utilise Dougs »

Signal d'universalité (« tous », « désormais »). Convention durable → RULES.md ou CONTRIBUTING.md du dossier shared concerné. Pas une mémoire.

### « Je veux qu'on extrait les insights de mes vocaux WhatsApp automatiquement »

Workflow répétable activé automatiquement → skill custom via `/skill-creator`. Ni mémoire ni connaissance.

## Liens

- `routage.md` — table à 10 cas, déclinaison opérationnelle du test pivot.
- `memory.md` — workflow de création d'une mémoire timestampée quand le test pivot pointe vers `memory/`.
- `scope-check.md` — perso vs shared avant d'écrire (orthogonal au test pivot mais toujours combiné).
- `skill-creator-routing.md` — quand router vers `/skill-creator` plutôt qu'un fichier.
