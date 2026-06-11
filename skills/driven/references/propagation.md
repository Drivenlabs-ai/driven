# propagation : Cascades silencieuses et proposées

Chaque écriture dans un workspace driven a des conséquences sur d'autres fichiers. Le plugin orchestre ces cascades automatiquement pour les changements triviaux, et propose en langage naturel pour les changements structurels.

## Cascade silencieuse (automatique, sans validation user)

Réservée aux changements qui ne portent pas de jugement de fond :

| Trigger | Action automatique |
|---|---|
| Write/Edit sur un fichier shared | Update du `last-updated` dans le frontmatter |
| Cross-author validé | Ajout de l'email user dans `authors` du fichier édité |
| Création / suppression / renommage d'un fichier dans un dossier | Regen de la section `## Index` du `CLAUDE.md` racine ou du dossier parent qui maintient l'index |
| Renommage de fichier | Scan des liens entrants dans le workspace + regen automatique vers le nouveau path |
| Création d'une memory entry | Auto cross-link vers mémoires connexes du voisinage (cf `references/links.md`) |

Le user voit le recap minimal : *« OK, j'ai renommé Olenbee et mis à jour les 14 liens. »* Pas de validation par cascade, le user attend ce comportement par défaut.

## Cascade proposée (langage naturel, validation user)

Réservée aux changements qui touchent à la cohérence du système ou aux conventions :

| Trigger | Proposition NL |
|---|---|
| Update d'une convention dans `RULES.md` racine | *« Cette nouvelle convention impacte aussi le `RULES.md` de Drivenlabs/. Je le mets à jour ? »* |
| Modification d'une fiche contact qui apparaît dans plusieurs dossiers business | *« Pierre Martin apparaît aussi dans Clients/Acme/. Je propage ? »* |
| Décision documentée dans une memory qui contredit un fichier normatif | *« Cette décision contredit ce qui est écrit dans `positioning.md`. Tu veux que je rafraîchisse le positioning ? »* |
| Refonte holistique d'un fichier qui pourrait casser des références | *« Cette refonte change la structure des sections de `SOUL.md`. 4 docs liés pourraient être impactés. Je propose un audit ? »* |

Une seule question, langage naturel, jamais de menu technique. Si user dit oui, exécution. Si non, abandon de la cascade, le fichier principal a été modifié, point.

## Renommage et regen des liens

Le cas le plus fréquent. Workflow :

1. User demande de renommer un fichier ou un dossier (ex `Clients/Olenbee/` → `Clients/Olenbee-Mature/`).
2. Invoquer `scripts/graph.py impact <ancien-path>` pour obtenir les liens entrants typés (cf `graphe.md`). Si le script échoue, retomber sur un grep du path littéral.
3. Avec ≤ 50 liens à regénérer : cascade silencieuse, recap minimal.
4. Avec > 50 liens : demande de validation en NL avant exécution (volume = risque).
5. Renommage effectif + regen des liens vers le nouveau path.
6. Memory entry créée dans le `memory/` du parent commun, documentant le renommage et la liste des fichiers impactés.

Le recap distingue les types d'arête : un lien `at-ref` (`@fichier`) cassé est un chargement transitif rompu, signalé plus fortement qu'un lien markdown simple. Exemple : *« renommé Olenbee, mis à jour 2 chargements obligatoires et 12 liens. »*

## Cascade vers les memory entries

Les memory entries sont append-only par construction (cf `references/memory.md`). Une cascade ne réécrit jamais une mémoire existante. Si la cascade implique une mise à jour structurelle d'un sujet déjà mémorisé, créer une **nouvelle mémoire** qui linke l'ancienne et explicite la révision :

```markdown
# Révision positioning 2026-06-12

## Contexte
Suite à l'update de `positioning.md` (refonte sur le segment PME), cette mémoire
révise la [décision positioning du 11/05](Clients/Drivenlabs/memory/2026-05-11-0900-alex-decision-positioning.md).

## Notes
[...]
```

L'historique reste lisible. Pas de mémoire muette.

## Cascade Drive Desktop (pre-write)

Avant chaque write sur un fichier shared, vérifier la présence d'une copie de conflit Drive Desktop dans le même dossier. Pattern de naming Drive (validé empiriquement) :

```
<basename> (YYYY-MM-DD [HH:MM]) - <author>.<ext>
```

Exemples :
- `CLAUDE (2026-05-12) - Mael.md`
- `pricing (2026-05-11 10:45) - Alex.md`

Si une copie de conflit est détectée pour le fichier cible :

1. **Interrompre l'écriture** en cours.
2. Proposer en NL : *« Il y a une version concurrente de ce fichier par Maël du 12/05. Je fusionne les deux avant d'écrire ? »*
3. Si user accepte : lire les deux versions, raisonner sur les divergences, proposer une version fusionnée en NL (pas un diff brut), valider, écrire la version fusionnée comme canonical, supprimer la copie conflit, créer une memory entry documentant la fusion.
4. Si user refuse : abandonner l'écriture, afficher les deux paths au user pour résolution manuelle.

Jamais d'action destructive automatique sur une copie de conflit. La détection trigger toujours une question.

## Cascade quand on supprime

Suppression d'un fichier qui a des liens entrants : demande NL. Toujours.

> Ce doc est référencé dans 4 autres fichiers. Tu confirmes la suppression ?

Si user confirme : suppression + cleanup des liens entrants (remplacés par le texte affiché en gras, pas par un lien cassé). Memory entry créée pour traçabilité.

## Pas de cascade en personal space

Le personal space n'a pas de tracking `authors`, pas de cross-author, pas de validation collective. Les cascades triviales (regen d'index, update de last-updated quand pertinent) s'appliquent. Les cascades structurelles restent proposées comme partout, la propagation est utile même en solo.

## Récap au user

Cascades silencieuses : recap minimal en une ligne à la fin de l'action principale.

> OK, j'ai renommé Olenbee, mis à jour les 14 liens et noté ça dans la mémoire.

Cascades proposées : une question NL avant exécution, puis recap minimal après.

Jamais de description détaillée de la mécanique. Le user voit le résultat, pas la machinerie.
