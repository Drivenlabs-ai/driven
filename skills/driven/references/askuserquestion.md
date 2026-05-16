# askuserquestion : Pattern d'interaction par défaut

## Quand cette ref s'active

- ≥ 2 actions distinctes proposées dans la même réponse user-facing.
- Décision user-facing à valider avec ≥ 2 options non-évidentes.
- Choix d'architecture, de stratégie, de routage qui nécessite l'arbitrage explicite du user.
- Avant toute phase Q&R où le user gagnerait du temps en sélectionnant plutôt qu'en rédigeant.

## Doctrine

L'utilisateur gagne du temps en sélectionnant parmi des options pré-rédigées plutôt qu'en formulant des réponses libres. Chaque question intègre les éléments de contexte nécessaires à une décision éclairée — trade-offs, conséquences, raison du choix. Le user lit, choisit, avance. Pas de friction texte libre, pas d'arbitrage à formuler de zéro.

C'est le pattern par défaut dans toutes les phases interactives du plugin driven : il rend les arbitrages explicites, les options visibles, et le coût mental d'une réponse minimal. Les questions ouvertes en texte libre restent valides pour l'exploration et la conversation, mais dès qu'un choix structuré est en jeu, on bascule sur ce pattern.

Toutes les autres refs du plugin qui ouvrent une phase interactive s'appuient sur cette doctrine (cf `setup-dossier.md` pour le pattern A, `capitalise-workflow.md` pour le pattern B, ainsi que `cross-author.md`, `interface-cli.md`, `session-handoff.md` pour leurs phases de validation).

## Quand l'utiliser

- Décisions structurantes (architecture, choix d'outil, scope)
- Validations critiques avant écriture (modification d'un fichier normatif, suppression)
- Batches de questions liées (≥ 2 questions sur un même sujet)
- Mini-interviews patterns A (`setup-dossier`) et B (`capitalise-workflow`)
- `/align` invoqué
- Tout choix pré-modélisable en 2-4 options claires

## Quand NE PAS l'utiliser

- Demandes triviales déterministes (« je supprime ce fichier ? »)
- Exploration libre, conversation naturelle continue
- Réponses qui demandent du texte libre substantiel (rédaction d'un brief, formulation d'une vision)
- Confirmation simple binaire qui suit naturellement la conversation

## Format requis

| Élément | Règle |
|---|---|
| Questions par batch | 1 à 4 max (plafond outil) |
| Options par question | 2 à 4, mutuellement exclusives sauf `multiSelect` explicitement justifié |
| Recommandation | 1ère option marquée « (Recommandé) » quand une option est clairement supérieure |
| Description option | Contexte de décision intégré : trade-offs, conséquences, raison du choix |
| Header | Court (12 chars max), identifie la question d'un coup d'œil |

## Anti-patterns

- **Options sans contexte décisionnel** : juste le label sans description claire. L'user doit pouvoir trancher sans relancer une conversation.
- **Batch > 4 questions** : découper en 2 batches successifs, avec exploration ciblée entre les deux.
- **Recommandation ambiguë** : 1ère option non marquée alors qu'elle l'est, ou marquée alors que les options sont équivalentes.
- **Options redondantes** : 2 options qui se distinguent à peine. Fusionner ou retravailler le découpage.
- **Question fermée déguisée** : 1 option = ne rien faire, l'user sent qu'il n'y a pas de vrai choix. Soit la question est légitime et l'option « ne rien faire » est réelle, soit il faut ne pas poser la question du tout.

## Cas particuliers

**Reformulation miroir avant écriture** — avant tout `Write`/`Edit` structurant sur un fichier normatif (CLAUDE.md, RULES.md, ABOUT.md, skill, etc.), présenter via `AskUserQuestion` les modifications proposées et demander confirmation. Pas de validation = pas d'écriture. Évite de partir sur une mauvaise inférence et de produire un diff qu'il faudra défaire ensuite.

**`/align` en cascade** — quand `/align` est invoqué sur une demande vague, batches de 4 questions max avec exploration ciblée entre batches. Chaque batch resserre le scope à partir des réponses précédentes. Pas de batch unique qui essaie de tout couvrir d'un coup : le user lit mieux 4 questions ciblées que 12 questions diluées.

**Batches de validation phase par phase** — pour des workflows multi-phases (ex spec → plan → execute), 1 batch de validation à chaque transition. L'user voit ce qui a été produit, valide ou redirige avant d'engager la phase suivante. Évite de découvrir un désalignement après 3 phases d'exécution, et donne un point d'inflexion explicite où le scope peut encore bouger sans coût.
