# audit-sections : Audit holistique des fichiers normatifs

Quand un fichier normatif (CLAUDE.md, RULES.md, CONTRIBUTING.md, SOUL.md, ABOUT.md) grossit ou accumule des modifications, un audit permet de vérifier sa cohérence interne et d'identifier ce qui mérite refonte ou extraction.

L'audit est explicitement invoqué par user via `/driven audit` ou en NL (« audite SOUL.md », « regarde si RULES.md est encore cohérent »).

## Workflow d'audit

1. **Lire le fichier intégralement**, sans skim.
2. **Mapper les sections**, quelles sections, quelle longueur, quel rôle.
3. **Détecter les patterns à risque** (cf liste ci-dessous).
4. **Proposer en NL** au user, pas un rapport technique, une discussion.
5. **Exécuter** ce que user valide. Pas plus.

## Patterns à risque détectés

### Contradictions internes

Deux passages du même fichier disent des choses opposées.

```
[Section Voice]
- Sois familier et direct.

[Section Interaction Style]
- Garde une distance professionnelle.
```

Signalement :

> Il y a deux passages qui se contredisent sur le ton (Voice dit familier, Interaction Style dit distance pro). Tu veux qu'on tranche ?

### Sections gonflées

Une section qui dépasse 30-50 lignes ou qui pourrait vivre dans un fichier dédié.

> La section Conventions fait 80 lignes, ça mériterait d'extraire en `RULES.md`. OK ?

Détail extraction : `references/decoupage-progressif.md`.

### Stacks de patchs

3+ ajouts ad-hoc sur le même thème, accumulés sans refonte.

> 4 directives différentes sur la voix dans SOUL.md. Je propose une refonte cohérente plutôt que d'en ajouter une 5ème ?

### Règles obsolètes

Mention de pratiques, outils, contacts ou conventions qui ne sont plus à jour (signal : memory entries récentes contredisent, ou user mentionne explicitement).

> RULES.md mentionne encore la convention sprint 2 semaines, mais on a basculé à sprint 1 semaine en avril (cf mémoire 2026-04-15). Je rafraîchis ?

### Micromanagement

Règles trop ciblées qui biaisent Claude dans des cas où elles ne devraient pas s'appliquer.

> Cette règle sur les emojis vient d'une session précise. C'est encore d'actualité ou on peut la retirer (état neutre = pas de mention) ?

### Redondance

Plusieurs sections qui disent la même chose avec des mots différents.

> La section À propos et la section Mission disent la même chose. On consolide ?

## Anti-pattern d'audit

### Ne pas auditer pour le plaisir

L'audit n'est pas un rituel. Il se fait sur demande explicite, ou quand un user ouvre un fichier normatif qui a manifestement dérivé. Pas de scan préventif quotidien.

### Ne pas surcharger user de questions

Si l'audit révèle 10 problèmes, ne pas faire 10 questions séquentielles. Présenter le résumé en NL :

> J'ai regardé SOUL.md. 3 trucs notables : contradiction sur le ton (Voice vs Interaction Style), section Voice gonflée (refonte ?), règle sur les emojis qui date d'il y a 2 mois (encore valable ?). Tu veux qu'on tranche tout maintenant ou on prend les points un par un ?

Le user choisit le rythme. Si « tout maintenant » : enchaîner sans demander confirmation à chaque étape.

### Ne pas auditer un fichier sain

Si le fichier est cohérent et concis, le dire en deux lignes :

> SOUL.md est cohérent et compact. Rien à signaler.

Pas de rapport pour le rapport.

## Présentation du diagnostic

Format type d'un retour d'audit :

```
J'ai audité [fichier]. Ce qui ressort :

- **[Pattern]** : [phrase concrète]
- **[Pattern]** : [phrase concrète]

On commence par quoi ?
```

Ton concis, anti-corporate. Pas de jargon (« inconsistencies », « anti-patterns », « refactoring opportunities »). Phrases en français naturel.

## Audit d'un CLAUDE.md racine d'un shared

Le CLAUDE.md racine est le point d'entrée du shared, plus stratégique que les autres normatifs. L'audit ici vérifie :

- La section À propos est-elle lisible en 30 secondes par un nouveau contributeur ?
- L'Index est-il à jour ?
- Les Conventions sont-elles toujours d'actualité ?
- Les pointeurs vers les fichiers extraits (ABOUT, RULES, CONTRIBUTING, RULES/) sont-ils encore valides ?

Si la racine pointe vers des fichiers qui n'existent plus, signaler et nettoyer.

## Audit d'un SOUL.md

Le SOUL.md gère la posture Claude. Patterns spécifiques à vérifier :

- Contradictions sur le ton (familier vs neutre vs distant).
- Stack de directives sur les emojis, le tutoiement, le niveau de challenge, etc.
- Règles trop ciblées qui ne devraient pas être en SOUL (mais en VOICE/surfaces).

L'audit SOUL est sensible, c'est l'identité de Claude vis-à-vis du user. À chaque modification, refonte holistique > ajout.

## Audit d'un RULES.md

Vérifier :

- Cohérence avec les memory entries récentes (les décisions documentées dans `memory/` sont-elles reflétées ?).
- Pertinence des règles avec l'état actuel du business.
- Granularité (règles trop spécifiques vs trop générales).

## Pas d'audit en personal space sans demande

Le personal space est privé. Pas d'audit non sollicité. Si user demande explicitement *« audite mon ME.md »*, exécuter normalement.

## Récap après audit

Une ligne par action exécutée.

> OK, j'ai refondu la section Voice de SOUL.md, retiré la règle emoji et mis à jour l'index. Le fichier est cohérent maintenant.

Pas de description détaillée des changements. Si user veut voir le diff, il demande explicitement.
