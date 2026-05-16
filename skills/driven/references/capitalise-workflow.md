# capitalise-workflow : Sauvegarder un workflow pour la prochaine fois

Une session qui produit un workflow non-trivial — quelques scripts, des décisions tranchées, un enchaînement d'actions qui *marche* — risque de disparaître à la fermeture. La prochaine fois, le user (ou un futur Claude) repart de zéro, redécouvre les mêmes pièges, refait les mêmes choix. Ce pattern détecte ces moments en fin de session et propose de figer ce qui mérite de l'être.

## Doctrine

À la fin d'un workflow non-trivial, le plugin propose de capitaliser. La décision de *quoi* sauvegarder et *où* dérive directement de la doctrine SAVOIR vs FAIRE (voir `connaissance-vs-memoire.md`) : un workflow répétable devient un skill ou une command, une convention durable va dans un fichier normatif, un événement riche va en mémoire timestampée.

L'enjeu n'est pas de tout archiver. C'est de reconnaître quand une session a produit quelque chose qui se reperdrait à la fermeture, et de le ranger au bon endroit avant qu'il ne s'évapore.

## Quand cette ref s'active

Scope niveau 1 — **universel**. Active dans tout dossier ouvert dans Claude Code ou Cowork, pas seulement les workspaces driven. Un workflow utile mérite d'être capitalisé qu'il soit produit dans un workspace structuré ou dans un dossier ad-hoc.

Niveau 2/3 — quand un `CLAUDE.md` racine avec frontmatter `space-type` est détecté, le routage de capitalisation est enrichi : accès aux conventions du workspace (RULES.md, CONTRIBUTING.md, structure `memory/`), choix éclairé de la cible selon les patterns du dossier.

- Fin de session avec ≥ 2 signaux parmi : ≥ 5 actions structurantes même sujet, création script ad-hoc, décisions tranchées via `AskUserQuestion` ou `/align`, refactor multi-fichiers, phrases user de satisfaction.
- Demande user explicite : « capitalise », « garde ça pour la prochaine fois », « on en fait un skill ? ».

## Trigger

| Type | Déclencheur |
|---|---|
| Auto | Claude infère qu'un workflow non-trivial a été réalisé dans la session (≥ 2 signaux simultanés ci-dessous) |
| Explicite | Commande `/driven workflow` — Claude infère le workflow de la session courante depuis le contexte et déclenche la capitalisation |

## Signaux de détection

Un workflow est jugé « non-trivial » et candidat à la capitalisation quand plusieurs des signaux ci-dessous se cumulent dans la session :

- **≥ 5 actions structurantes sur un même sujet** dans la session (Write, Edit, Bash exécutifs, Agent lancés). Pas du Read exploratoire, du *faire*.
- **Création d'au moins un script ad-hoc** (Python, shell, JS) pour automatiser ou résoudre quelque chose.
- **Décisions tranchées via `AskUserQuestion` ou `/align`** dans la session — signe qu'il y a eu des arbitrages structurants à conserver.
- **Refactor multi-fichiers** (≥ 3 fichiers cohérents touchés autour d'un même objectif).
- **User dit explicitement** « ça marche », « c'est cool », « on garde ça », « ce serait dommage de perdre », ou équivalent.

**Seuil** : ≥ 2 signaux simultanés strictement. En dessous, c'est une session ordinaire — la mémoire timestampée ou les fichiers normatifs suivent leur cours naturel sans pattern dédié.

## Exclusion : mode routine

Cette ref **ne s'active jamais en mode routine**. En routine, Claude est un agent autonome qui exécute une tâche et termine — il n'y a pas d'utilisateur en interaction à qui proposer quoi que ce soit, et proposer briserait l'autonomie.

Mode routine détecté en Code via :

- Sentinel `<<autonomous-loop>>` ou `<<autonomous-loop-dynamic>>` dans le prompt initial de la session.
- Tool `ScheduleWakeup` ou `CronCreate` disponible dans la liste des tools.
- Section « Autonomous loop check » ou « Autonomous loop persistence guidance » dans le system prompt.

## Workflow de capitalisation

### 1. Proposition NL unique

Une phrase, naturelle, en fin de séquence quand les signaux sont là :

> On vient de [résumé en 1 phrase du workflow]. Tu veux qu'on sauvegarde ça pour la prochaine fois ?

Une seule proposition par session. Pas de relance si user passe à autre chose.

### 2. Si user refuse

Silence définitif pour la session. Pas de re-proposition même si d'autres signaux apparaissent ensuite. Le user a tranché.

### 3. Si user accepte → **AskUserQuestion**

Trois options de routage présentées via **`AskUserQuestion`** (insister : c'est l'outil qui convient, choix structurés, pas de friction texte libre) :

- **Option 1 — Skill custom via `/skill-creator`** : le workflow est répétable avec variations (FAIRE qui reviendra plusieurs fois). Exemple : « à chaque vocal WhatsApp d'un prospect, extrais les insights selon ce template ». Cf `skill-creator-routing.md`.
- **Option 2 — CLAUDE.md ou RULES local** : le workflow révèle une convention durable applicable à ce dossier (SAVOIR stable, vrai demain). Exemple : « désormais tous les devis Olenbee suivent la structure X ».
- **Option 3 — Mémoire timestampée détaillée** : capture épisodique riche, avec liens vers les fichiers touchés et les décisions prises. Utile quand le workflow ne se reproduira pas tel quel mais que son contexte mérite d'être préservé.

Ces 3 options dérivent directement de la doctrine SAVOIR vs FAIRE (`connaissance-vs-memoire.md`) : FAIRE répétable → skill, SAVOIR durable → fichier normatif, épisodique riche → mémoire.

### 4. Exécution selon choix

- **Option 1** → bascule vers `/skill-creator` avec le contexte de la session pré-rempli.
- **Option 2** → édition du fichier normatif cible (création si absent), validation diff avant écriture.
- **Option 3** → création d'une mémoire timestampée standard (cf `memory.md`), avec liens markdown vers les fichiers touchés dans le corps.

### 5. Recap minimal

Une ligne, NL pur, sans jargon (cf section Recap user).

## Anti-patterns

- **Proposer trop souvent** : seuil ≥ 2 signaux strict. Un seul fichier modifié ou une décision isolée ne déclenche pas. Sinon le pattern devient bruyant et le user finit par l'ignorer.
- **Capitaliser du trivial** : la mémoire timestampée naturelle et l'édition normale des fichiers normatifs couvrent déjà les petits ajustements quotidiens. Le pattern de capitalisation ne s'active que pour ce qui mérite vraiment d'être figé comme actif.
- **Forcer un type de routage** : si user dit « note juste » ou « garde une trace », ne pas pousser le skill custom — créer directement la mémoire timestampée. Respecter le signal user sur la nature de la capture.
- **Recommencer en boucle après refus** : silence définitif pour la session après un « non ». Pas de nouvelle tentative à chaque nouveau signal.

## Recap user

1 à 2 lignes max, NL pur, sans jargon. Le user voit le résultat et passe à la suite.

Exemples :

> OK, j'ai mis le process dans le doc d'Olenbee.

> OK, j'ai gardé une note détaillée pour la prochaine fois.

> OK, on a fait un nouveau skill `/extract-vocaux`.

Pas de mention de « capitalisation », de « workflow », de « skill custom » envers user. Le mot juste pour le résultat concret, rien de plus.
