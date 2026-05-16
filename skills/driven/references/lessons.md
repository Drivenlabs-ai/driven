# lessons : Capture d'apprentissages durables scopés par dossier

## Quand cette ref s'active

- Convention scopée à un dossier (universel dans le scope + intemporel + contextuellement neutre).
- Demande d'ajouter une règle qui s'applique partout sous un dossier précis.
- Énoncé d'apprentissage durable lié à un domaine (ex : « pour tous les devis Olenbee, valider avec Laurent »).
- Doute sur le scope d'une lesson (globale RULES vs local CLAUDE.md de dossier).

## Doctrine

Le plugin a 3 surfaces de capture distinctes. Une lesson est le type intermédiaire entre événement ponctuel et convention globale.

| Surface | Quand | Caractéristique |
|---|---|---|
| Mémoire timestampée (`memory/`) | Événement précis, daté | Append-only, chronologique, factuel |
| Lesson (section CLAUDE.md du dossier) | Apprentissage durable scopé au dossier | Universel dans le scope, intemporel |
| Fichier normatif racine (RULES.md, SOUL.md, etc.) | Convention globale du workspace | Universel partout |

Sans `lessons`, les apprentissages durables scopés à un dossier (« pour Olenbee, toujours valider les devis avec Marie ») se diluent dans les mémoires ou polluent les RULES racine.

## Les 3 critères stricts

Une lesson valide doit satisfaire **les 3 simultanément** :

1. **Universelle dans son scope** — vraie pour 100% des cas dans le dossier où vit le CLAUDE.md hébergeur. Une lesson dans `Clients/Olenbee/CLAUDE.md` est universelle dans le contexte Olenbee, pas globalement.
2. **Intemporelle** — pas liée à un moment précis. Pas « cette semaine on évite X », mais « X est toujours à éviter dans ce scope ».
3. **Contextuellement neutre dans son scope** — pas dépendante d'une humeur ou d'un état de session particulier.

## Test décisionnel (4 étapes)

Avant d'écrire une lesson, Claude vérifie dans cet ordre :

1. **Scope** : à quel dossier cette lesson s'applique ? Racine du workspace ? Sous-dossier client/projet ? → définit le CLAUDE.md hébergeur.
2. **Universalité** : « si je relis ça dans 100% des sessions futures concernant ce scope, est-ce que cette lesson serait juste ? »
3. **Intemporalité** : « cette lesson est-elle juste indépendamment du moment ? »
4. **Contextualité** : « cette lesson est-elle juste indépendamment de l'humeur/état de la session ? »

Si **un seul critère échoue** → pas une lesson. C'est soit une mémoire timestampée, soit une préférence ponctuelle (non capturée).

## Signaux de détection

Claude observe des patterns langagiers qui suggèrent un apprentissage durable :

- « toujours faire X ici »
- « jamais Y »
- « la règle ici c'est »
- « comme d'habitude on »
- « par défaut dans ce dossier »
- « pour [client/projet], on »

Détection → application du test des 3 critères → si valide, proposition de capture.

## Workflow de capture (doctrine Q5)

1. **Trigger** : signal d'apprentissage durable détecté.
2. **Test interne** : Claude applique les 3 critères silencieusement.
3. **Si valide** : Claude propose en NL au user :
   > Je note comme lesson dans [dossier] : "[lesson reformulée]". Conséquence : à chaque session concernant [scope], je l'appliquerai par défaut. Pas valide ailleurs. OK ?
4. **Validation** : doctrine Q5 (cf `maintenance-fichiers-racines.md`) — explication des répercussions d'usage avant écriture.
5. **Si pas valide** : Claude propose alternative (mémoire timestampée si événement, refus silencieux si préférence ponctuelle).

## Suppression directe

Si une lesson devient obsolète (scope change, apprentissage ne tient plus), Claude la retire **sans contre-règle ni archivage**. Pas de mention « anciennement on faisait X ». Clean slate strict cohérent avec doctrine du plugin (SKILL.md §3).

## Anti-patterns

| Anti-pattern | Pourquoi mauvais |
|---|---|
| Lesson dérivée d'une humeur de session (« toujours avancer structuré ») | Préférence ponctuelle, pas universelle dans le scope. Risque : impacte les conversations rapides voulues |
| Lesson trop large (« toujours réfléchir avant d'agir » dans un sous-dossier) | Vrai partout → devrait être dans SOUL.md racine, pas en lesson scopée |
| Lesson temporellement marquée (« pour ce trimestre, prioriser X ») | Pas intemporelle → mémoire ou objectif, pas lesson |
| Lesson capturée préventivement (« peut-être qu'il faut faire X ») | Pas vérifiée durablement, doctrine plugin = pas de capture préventive |
| Lesson contradictoire avec une autre dans le même CLAUDE.md | Signaler en NL + proposer refonte, pas accumulation |

## Interactions avec le reste du plugin

| Composant | Comment lessons interagit |
|---|---|
| `memory.md` | Distinct : mémoire = événement ponctuel, lesson = apprentissage durable scopé |
| `challenge-anti-recidive.md` | Consulte les lessons de la cascade (CLAUDE.md remontés) avant proposition stratégique |
| `maintenance-fichiers-racines.md` (Q5) | Ajout d'une lesson = modification structurante d'un CLAUDE.md → doctrine Q5 s'applique |
| `claude-md-template.md` | Documente la section optionnelle « Lessons » dans le squelette CLAUDE.md |

## Format dans le CLAUDE.md

Section optionnelle, format markdown libre :

```markdown
## Lessons

- Pour [scope], toujours [action].
- [Autre lesson concise et actionnable].
```

Pas plus de 5-7 lessons par CLAUDE.md. Au-delà, signe que certaines sont trop spécifiques (mémoire) ou trop génériques (RULES racine).

## Recap user après capture

> OK, j'ai noté que pour Olenbee, on valide toujours avec Marie.

NL pur, pas de jargon. Cohérent avec doctrine d'invisibilité (SKILL.md §1).
