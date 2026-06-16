# cloture-session : Clôturer une session proprement

Quand une session de travail se termine, ce qui a été produit, décidé et appris risque de s'évaporer : la session suivante repart d'un espace qui n'a pas digéré la précédente. La clôture lance la consolidation (`consolidation.md`) sur le périmètre de toute la session, puis propose le handoff. Le handoff (prompt de reprise pour une nouvelle session) n'en est que l'étape finale optionnelle, pas le réflexe par défaut.

## Quand cette ref s'active

L'user signale qu'on termine : « on ferme », « clôture la session », « on s'arrête là », « j'ai fini pour aujourd'hui », « on boucle », ou tout autre signal de fin de session. S'active aussi quand une saturation conversationnelle (`session-handoff.md`) est acceptée, et quand l'user demande directement un handoff (« prépare le handoff », « fais le récap pour reprendre »).

## Consolidation de la session

La clôture appelle `consolidation.md` avec pour périmètre la session entière — pas seulement le dernier travail : prise de mémoire, drift, structuration, audit, liens et provenance, selon les six étapes et la remontée structurée du moteur. Le forcing, l'exclusion mode routine et la règle écriture-vs-proposition sont ceux du moteur.

## Handoff optionnel

Le prompt de reprise n'a de sens que si le travail continue dans une nouvelle session — saturation atteinte, ou user qui enchaîne ailleurs. Après la consolidation, le proposer dans ce seul cas :

> C'est rangé. Tu reprends ça dans une nouvelle session ? Je te prépare un prompt de reprise.

Si l'user clôt sans continuer, pas de handoff. S'il accepte ou l'a demandé d'emblée, produire le prompt selon `session-handoff.md`, qui s'appuie sur la mémoire de session déjà créée par la consolidation.

## Recap minimal

Deux lignes maximum, NL pur, sans jargon : ce qui a été rangé, et le prompt de reprise s'il y en a un. Pas de description de la machinerie des phases.

> OK, j'ai noté l'essentiel et rangé le doc d'Acme.
