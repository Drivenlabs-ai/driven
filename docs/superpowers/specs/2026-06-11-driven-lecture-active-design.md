# Spec — Driven : discipline de lecture active

**Date** : 2026-06-11
**Statut** : design validé, prêt pour plan d'implémentation
**Version cible** : driven v1.10.0

## Problème

Deux faiblesses observées de driven partagent une racine unique : **driven n'a aucune discipline au moment où il lit un fichier normatif**. Tous ses déclencheurs s'activent sur une écriture, une parole de l'utilisateur, ou une commande explicite — jamais sur la lecture/le chargement d'un CLAUDE.md ou d'un normatif. Driven est passif à la lecture : il déverse ou il avale.

**Axe 1 — progressive disclosure.** Driven ne sait décider du contenu d'un CLAUDE.md que sur un seuil de lignes (30-50), jamais sur « est-ce de l'information de routage ou du détail ? ». Conséquence : des CLAUDE.md à la mauvaise altitude — trop minces pour router vers le niveau d'en dessous, ou gonflés de détails qui saturent le contexte. Le vide le plus net est sur les sous-CLAUDE.md (`claude-md-template.md` les laisse « structure libre, Claude juge » sans critère), exactement le niveau où la disclosure vers le bas se joue.

**Axe 2 — incohérences non chassées.** Quand driven lit un normatif contenant une information stale, contradictoire ou fausse, rien ne l'amène à le signaler. La détection de contradictions/règles obsolètes existe (`audit-sections.md`) mais est entièrement gatée derrière `/driven audit` explicite. Aucune ligne de la table §6.2 du SKILL.md n'a pour signal « je viens de lire X qui contredit l'état connu ». Driven ingère le contenu comme vrai par construction.

## Objectif

Rendre driven **actif quand il engage un fichier normatif** : un test d'altitude au moment d'écrire/auditer un CLAUDE.md (axe 1), et un déclencheur de cohérence au moment de lire un normatif (axe 2).

Principe de conception : **driven mange sa propre nourriture.** Chaque concept est défini une seule fois dans son propriétaire naturel (SSOT), les consommateurs pointent dessus (progressive disclosure) — le correctif applique la doctrine qu'il répare. Zéro nouveau fichier de référence.

Contrainte transverse : tous les fichiers touchés sont lus par un modèle. Chaque édition respecte les lois `writing-prompts` (clean-slate, stateless, densité, scope explicite, le pourquoi voyage avec la règle, budget d'emphase).

## Périmètre

### Dans le périmètre (V1)

1. **Test d'altitude** défini une fois dans `gestion-contexte.md`, référencé par 4 consommateurs ; seuil de lignes rétrogradé en indice secondaire.
2. **Mode lecture** (cohérence à la lecture) défini une fois dans `audit-sections.md` ; déclencheur dans la table §6.2 du SKILL.md ; symétrisation de la cascade dans `propagation.md` ; pondération par le champ `confidence`.

### Hors périmètre (V1, explicite)

- Scan préventif de tous les normatifs en début de session (interdit par la doctrine existante d'`audit-sections.md`).
- Refonte de la mécanique de chargement de `gestion-contexte.md` (saine, on s'appuie dessus).
- Modification de l'audit on-demand complet (le mode lecture est un complément léger, distinct).
- Toute nouvelle référence dédiée (les deux concepts vivent dans leurs propriétaires existants).
- Test automatisé (édition de prompts ; la validation est une relecture de cohérence + contrôle anti-drift).

## Axe 1 — Test d'altitude

### Domicile canonique : `gestion-contexte.md`

Ajouter une section qui définit le test une seule fois. Texte canonique proposé :

```markdown
## Test d'altitude — quelle information vit à quel niveau

Avant d'écrire une ligne dans un CLAUDE.md, lui appliquer le test : **aide-t-elle à choisir le bon sous-niveau sans l'ouvrir ?** Si oui, c'est de l'information de routage, elle reste à ce niveau. Si elle décrit comment faire quelque chose à l'intérieur de ce niveau, c'est du détail : il vit dans le fichier ou le sous-dossier concerné, atteint par un pointeur.

Un lecteur froid d'un CLAUDE.md de bonne altitude sait où aller chercher sans absorber ce qu'il y trouvera. La taille n'est pas le critère : un CLAUDE.md court peut être à la mauvaise altitude s'il est plein de détails opérationnels, un plus long peut être juste si tout sert à router.

Sous-CLAUDE.md d'un dossier client, bonne altitude :

`Les comptes-rendus de RDV vivent dans memory/. Le positioning est dans positioning.md, les devis dans devis/.`

Mauvaise altitude (le détail appartient à la mémoire ou au doc pricing, pas au CLAUDE.md) :

`Le tarif négocié est 8K, révisé à 10K le 14/05, Laurent veut un paiement en deux fois.`
```

### 4 pointeurs (chacun référence le test, ne le reformule pas — Loi 11)

- **`decoupage-progressif.md`** : le test d'altitude devient le critère premier de la décision d'extraction, placé avant les signaux de taille. Le seuil de lignes y est reformulé en indice secondaire : un dépassement invite à vérifier l'altitude, il ne déclenche plus l'extraction à lui seul.
- **`setup-dossier.md`** : ajouter à l'interview une question de calibration d'altitude — ce qu'un futur Claude doit savoir pour choisir le bon sous-dossier sans l'ouvrir.
- **`audit-sections.md`** : ajouter un pattern à risque « mauvaise altitude », distinct de « section gonflée » (une section peut être à la mauvaise altitude sans être gonflée). Le test détermine le diagnostic.
- **`claude-md-template.md`** : à l'endroit où la structure des sous-CLAUDE.md est laissée au jugement de Claude, pointer le test d'altitude comme critère de ce jugement.

### Rétrogradation du seuil de lignes

Partout où un seuil 30-50 lignes déclenche aujourd'hui une extraction (`decoupage-progressif.md`, `claude-md-template.md`), il devient un signal secondaire qui invite à appliquer le test d'altitude. Le test est le déclencheur ; la taille est un symptôme possible.

## Axe 2 — Cohérence à la lecture

### Domicile canonique : `audit-sections.md`, section « Mode lecture »

Ajouter une section distincte de l'audit on-demand. Texte canonique proposé :

```markdown
## Mode lecture (passif, léger)

Distinct de l'audit on-demand (complet, déclenché par l'utilisateur). Le mode lecture s'applique aux normatifs que driven lit pour la tâche courante, pas à un scan préventif de l'espace.

Quand une section d'un normatif lu contredit l'état connu, le signaler en langage naturel et proposer la mise à jour. Jamais bloquant. Trois conditions de contradiction :

- Une autre section du même fichier dit l'inverse.
- Une mémoire datée du même scope dit l'inverse.
- Un fait établi dans la session courante dit l'inverse.

Le champ `confidence` des mémoires pondère : une mémoire `verbatim` qui contredit un normatif est un signal fort (l'utilisateur l'a dicté) ; une mémoire `inferred` se mentionne avec réserve.

Calibration : le check ne tourne que sur les fichiers réellement lus pour la tâche. Un signalement par contradiction et par session, pas de répétition. Silencieux si rien ne contredit. La proposition de fix passe par les garde-fous d'écriture habituels (validation avant tout write sur un normatif).
```

### Déclencheur : table §6.2 du SKILL.md

Ajouter une ligne au tableau « Signaux de support » :

```markdown
| Lecture d'un normatif dont une section contredit l'état connu (autre section, mémoire datée du scope, ou fait établi en session) | `audit-sections.md` (mode lecture) | Signaler la contradiction en NL, proposer la mise à jour |
```

### Symétrisation : `propagation.md`

La cascade proposée « décision en mémoire qui contredit un normatif → proposer de rafraîchir le normatif » existe dans le sens mémoire→normatif (au moment d'écrire une mémoire). Ajouter le sens inverse normatif→mémoire au moment de la lecture, pointant le mode lecture d'`audit-sections.md`. Une information, un seul endroit : la logique de détection vit dans `audit-sections.md`, `propagation.md` la référence.

## Fichiers touchés

| Fichier | Nature de l'édition |
|---|---|
| `skills/driven/references/gestion-contexte.md` | Nouvelle section : test d'altitude (domicile canonique) |
| `skills/driven/references/decoupage-progressif.md` | Test d'altitude en critère premier ; seuil de lignes rétrogradé |
| `skills/driven/references/setup-dossier.md` | Question d'altitude dans l'interview |
| `skills/driven/references/audit-sections.md` | Pattern « mauvaise altitude » ; nouvelle section « Mode lecture » |
| `skills/driven/references/claude-md-template.md` | Pointeur vers le test d'altitude pour les sous-CLAUDE.md ; seuil de lignes rétrogradé |
| `skills/driven/SKILL.md` | Ligne de déclencheur dans la table §6.2 |
| `skills/driven/references/propagation.md` | Symétrisation normatif→mémoire au mode lecture |
| `.claude-plugin/plugin.json` | Bump v1.9.0 → v1.10.0 |

## Validation

Aucun test automatisé (édition de prompts). La validation par revue vérifie :

- **Anti-drift** : le test d'altitude et la logique de mode lecture n'existent chacun qu'à un seul endroit ; les autres fichiers pointent (Loi 11).
- **Conformité writing-prompts** sur chaque diff : clean-slate, stateless, densité, scope explicite, le pourquoi voyage avec la règle, budget d'emphase (≤ 1-2 emphases par fichier).
- **Cohérence** : les pointeurs visent des sections qui existent ; la rétrogradation du seuil de lignes n'a laissé aucune formulation où la taille reste un déclencheur autonome.
- **Lecteur froid** : chaque section éditée se comprend sans la conversation courante.
