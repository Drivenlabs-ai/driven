# cross-author : Flow simplifié, 1 question, ajout co-auteur

Un fichier shared porte une liste `authors` dans son frontmatter. Cette liste est plate (pas de hiérarchie owner/contributeur), ordonnée par première contribution. Quand un user dont l'email n'est pas dans la liste s'apprête à éditer un fichier, le plugin déclenche le flow cross-author.

## Détection

Avant chaque `Edit` ou `Write` sur un fichier shared existant :

1. Lire le frontmatter du fichier cible.
2. Récupérer la liste `authors`.
3. Comparer l'email primaire du user courant (depuis `ME.md`) à la liste.
4. Si email présent → write direct, pas de flow.
5. Si email absent → trigger cross-author **avant** la préparation du diff.

L'activation avant le diff économise le calcul si le user refuse l'édition.

## Question type : une seule

Langage naturel, zéro jargon, deux issues possibles :

> Ce document est de [Nom des authors actuels]. Tu continues ?

Le nom est récupéré depuis la table `members:` du frontmatter du CLAUDE.md racine du shared space (cf `frontmatter.md`). Le plugin lit ce CLAUDE.md racine en début de session via remontée d'arborescence depuis le fichier ciblé, parse la table `members:`, et résout chaque email d'`authors` vers son `name`.

Si plusieurs auteurs : *« Ce document est d'Alex et Maël. Tu continues ? »*.

Si un email d'`authors` n'apparaît pas dans la table `members:` (cas exceptionnel d'un contributeur externe ou retiré), fallback sur l'email tel quel : *« Ce document est de externe@partenaire.com. Tu continues ? »*. Pas bloquant, juste moins lisible.

Pas de menu, pas d'options multiples, pas de « Es-tu sûr ? ». Une seule question, deux issues.

## Si user dit oui

1. Plugin écrit la modification demandée.
2. Email du user courant ajouté à `authors` (en fin de liste, conservant l'ordre première contribution).
3. `last-updated` mis à jour dans le frontmatter.
4. Création silencieuse d'une memory entry factuelle dans le `memory/` du dossier parent du fichier, documentant la modification (type `interaction`).
5. Recap au user :

> OK, j'ai mis à jour le doc et je t'ai ajouté en co-auteur.

Pas plus. Le user voit le résultat, pas la mécanique du frontmatter.

## Si user dit non

Pas de modification du fichier shared. Plugin propose une alternative en NL, sans utiliser le mot « perso » :

> OK, je peux mettre ça ailleurs juste pour toi. On en reparle quand tu veux.

Si user accepte : créer un fichier équivalent dans le personal space, au path parallèle (ex `~/Personal OS/<même chemin relatif>`). Log session pour traçabilité (mémoire perso si pertinent).

Si user refuse aussi cette alternative : abandon de la modification, contenu gardé dans le contexte de la session uniquement (perdu à la fin si non sauvegardé).

## Cas spéciaux

### Cross-author sur un fichier normatif (RULES, CONTRIBUTING, CLAUDE racine)

Le flow s'applique normalement, mais s'enchaîne avec la criticité du fichier normatif (cf `references/maintenance-fichiers-racines.md`). Le user peut être à la fois cross-author **et** modifiant un fichier sensible. Dans ce cas, **deux validations distinctes** :

1. Cross-author : *« Ce fichier est d'Alex. Tu continues ? »*
2. Si oui : alerte criticité : *« Et c'est un fichier de règles, modifié avec attention. Tu veux qu'on refasse cohérent ou tu ajoutes juste cette ligne ? »*

Les deux questions sont distinctes pour rester lisibles. Pas de fusion qui ferait double charge cognitive.

### Cross-author sur une memory entry

Les memory entries sont append-only par construction (cf `references/memory.md`). L'édition d'une mémoire existante par un cross-author est rare (correction de typo, ajout de lien). Si elle a lieu :

1. Flow normal (1 question, ajout `authors`).
2. Mais : si la modification est de fond (révision de l'interprétation, ajout d'éléments substantiels), refuser l'édition en NL :

> Cette mémoire est figée comme un instantané. Je crée une nouvelle mémoire qui complète celle-là ?

Pousse vers append-only même en cross-author.

### Cross-author multiple en série

Si user fait plusieurs édits successifs dans la même session sur des fichiers dont il n'est pas auteur, le flow se déclenche une fois par fichier. Pas de validation globale « tu modifies plusieurs docs d'Alex aujourd'hui, OK pour tous ? », chaque fichier mérite sa question dédiée pour rester intentionnel.

Exception : si user dit explicitement *« je fais une passe de cleanup, va sur tout »*, le plugin peut accepter une validation groupée pour la session courante. Recap après chaque fichier reste minimal.

## Ordre des authors

La liste `authors` est ordonnée par **première contribution**. Le créateur initial est toujours en premier. Les co-auteurs s'ajoutent en fin de liste dans l'ordre de leur première intervention.

Pas de tri alphabétique, pas de hiérarchie. L'ordre est un signal historique, pas une priorité.

## Suppression d'un auteur

Pas de mécanisme automatique. Si un user quitte l'équipe, son email reste dans `authors` (signal historique). Le retrait manuel est une opération de cleanup ponctuelle, hors flow cross-author standard.

Si user demande explicitement *« retire [email] de tous les docs »* : opération validée, scan workspace, retraits en cascade, memory entry pour traçabilité.

## Pas de cross-author en personal space

Le personal space est mono-user implicite. Pas de tracking `authors`, pas de flow cross-author, pas de validation collective. Le user édite ses propres fichiers librement.

## Recap user : toujours minimal

Que la modification soit triviale (correction typo) ou substantielle (refonte d'une section), le recap reste deux lignes maximum.

> OK, j'ai mis à jour le brief Olenbee et je t'ai ajouté en co-auteur.

Pas de description de la modification, pas de mention du frontmatter, pas de path complet sauf si la précision sert le user.
