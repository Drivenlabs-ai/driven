# decoupage-progressif : Extraction des sections gonflées

Quand une section d'un fichier normatif grossit, elle mérite extraction vers un fichier dédié. Cette extraction respecte la philosophie de **progressive disclosure** : la vue racine reste stratégique, le détail vit dans des fichiers dédiés accessibles via pointeurs.

## Quand extraire

Pas de seuil chiffré strict, Claude raisonne au cas par cas. Signaux qui justifient extraction :

| Signal | Action |
|---|---|
| Section dépasse 30-50 lignes dans le CLAUDE.md racine | Extraire vers fichier dédié, garder résumé 3 lignes dans CLAUDE.md |
| Plusieurs sous-thèmes émergent dans une même section | Extraire chacun dans son fichier dédié |
| Le contenu de la section a une audience naturelle distincte du reste du CLAUDE.md (ex : conventions techniques vs stratégie) | Extraire vers le fichier qui correspond à l'audience |
| Plus de 3 modifications récentes touchent la même section | Extraire pour rendre la maintenance plus locale |

## Cibles d'extraction

| Section du CLAUDE.md | Extrait vers | Quand |
|---|---|---|
| À propos | `ABOUT.md` à la racine | Quand la mission/identité prend > 30 lignes |
| Conventions (workflows, glossaire, rituels) | `RULES.md` à la racine | Quand les conventions internes deviennent substantielles |
| Workflows et étapes par phase | `CONTRIBUTING.md` à la racine | Quand on a un workflow d'onboarding ou des étapes par type de contribution |
| Règles thématiques (naming, sécurité, voix, etc.) | `RULES/<thème>.md` | Quand RULES.md grossit ou quand un thème mérite isolement |
| Environnement, stakeholders, outils | `ENV.md` ou intégré à `ABOUT.md` | Rare en pratique |

L'extraction n'est jamais préventive, uniquement quand le besoin est manifeste.

## Workflow d'extraction

1. Identifier la section qui mérite extraction (audit ou jugement contextuel).
2. Proposer en NL au user :

> La section Conventions de CLAUDE.md fait 80 lignes, je propose d'extraire dans `RULES.md`. OK ?

3. Si user dit oui :
   - Créer le nouveau fichier (`RULES.md`) avec frontmatter `authors` + `last-updated`.
   - Y copier le contenu de la section.
   - Dans CLAUDE.md, remplacer la section par un résumé 2-3 lignes + pointeur vers le nouveau fichier.
4. Recap minimal :

> OK, j'ai sorti les conventions dans RULES.md. Le CLAUDE.md pointe vers ce fichier maintenant.

## Format du pointeur dans le CLAUDE.md

Après extraction, la section dans le CLAUDE.md ne disparaît pas, elle devient un résumé + pointeur. Format :

```markdown
## Conventions

Les conventions internes (workflows, glossaire, rituels) vivent dans `[RULES.md](RULES.md)`.
En bref : sprints de 2 semaines, retro vendredi, briefs client en structure X.
```

Le résumé est court (2-3 lignes max), suffisant pour qu'un lecteur de la racine ait l'essentiel sans cliquer.

## Extraction en cascade

Si après extraction, le fichier extrait grossit à son tour (ex : `RULES.md` qui dépasse 100 lignes), nouvelle extraction vers `RULES/<thème>.md` :

```
RULES.md (racine)
├── pointe vers RULES/naming.md
├── pointe vers RULES/voix.md
└── pointe vers RULES/sprints.md
```

Le `RULES.md` racine devient un index de règles thématiques, chaque thème dans son fichier dédié.

## Anti-pattern : pré-création vides

Ne pas créer ABOUT.md ou RULES.md ou un dossier RULES/ par défaut au SETUP. L'extraction est **organique**, déclenchée par la croissance réelle du contenu. Un fichier vide ou quasi-vide est du bruit dans le workspace.

## Anti-pattern : refonte sous prétexte d'extraction

L'extraction est un découpage **structurel**, pas une refonte de fond. Le contenu extrait reste fidèle à ce qu'il était dans le CLAUDE.md, à 100 %.

Si user demande à la fois extraction et refonte (ex : *« extrais les conventions et nettoie-les »*), traiter en deux étapes pour rester lisible :

1. Extraire d'abord (juste découpage).
2. Proposer la refonte en NL après extraction.

Sinon le user perd de vue ce qui a été déplacé vs réécrit.

## Cascade silencieuse vers les pointeurs

Quand un fichier est extrait, mettre à jour automatiquement :

- La section concernée du CLAUDE.md (remplacée par résumé + pointeur).
- L'index du CLAUDE.md racine (regen pour inclure le nouveau fichier).
- Toute autre référence au contenu déplacé dans le workspace (rare en pratique, mais à vérifier).

Cascade silencieuse, recap minimal au user.

## Cas particulier : personal space

Le personal space suit les mêmes principes. Différence pratique :

- `ME.md` racine reste compact (entry point lisible 30s).
- Quand `ME.md` grossit, créer un dossier `ME/` avec des fichiers thématiques (`ME/contexte-business.md`, `ME/relations.md`, etc.).
- `SOUL.md` reste mono-fichier sauf croissance exceptionnelle.
- `VOICE/` est déjà multi-fichiers par défaut (surfaces, registres, etc.).

## Inverse : consolidation

Le contraire de l'extraction : quand plusieurs fichiers liés se vident ou se chevauchent, les consolider dans un seul.

Trigger : audit qui révèle 2-3 fichiers normatifs qui pourraient fusionner sans perte de clarté.

Proposition NL :

> RULES/sprints.md et RULES/timeline.md disent à peu près la même chose. Je fusionne dans RULES/workflows.md ?

Exécuter si user accepte. Pas de consolidation auto sans demande.

## Récap au user

Toujours minimal.

> OK, j'ai sorti les conventions dans RULES.md.

Si tech-level haut : plus détaillé.

> OK, créé RULES.md (80 lignes), CLAUDE.md mis à jour avec résumé 3 lignes + pointeur, index regen.

Pas de description du contenu extrait sauf si user demande explicitement.
