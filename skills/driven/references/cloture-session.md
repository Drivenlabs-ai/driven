# cloture-session : Clôturer une session proprement

Quand une session de travail se termine, ce qui a été produit, décidé et appris risque de s'évaporer : la session suivante repart d'un workspace qui n'a pas digéré la précédente. La clôture est le passage qui range avant de fermer — elle garde la mémoire, consolide le durable, structure ce qui a gonflé, vérifie la cohérence. Le handoff (prompt de reprise pour une nouvelle session) n'en est que l'étape finale optionnelle, pas le réflexe par défaut.

Cette ref orchestre la clôture en déléguant à des refs dédiées ; elle ne réécrit aucune de leurs règles.

## Quand cette ref s'active

L'user signale qu'on termine : « on ferme », « clôture la session », « on s'arrête là », « j'ai fini pour aujourd'hui », « on boucle », ou tout autre signal de fin de session. S'active aussi quand une saturation conversationnelle (`session-handoff.md`) est acceptée, et quand l'user demande directement un handoff (« prépare le handoff », « fais le récap pour reprendre ») — la clôture passe d'abord, le handoff suit.

## Exclusion : mode routine

Ne s'active jamais en mode routine (détection : `session-handoff.md` §mode routine). Un agent autonome exécute sa tâche et termine ; il n'y a pas de session interactive à clôturer.

## Forcing : la revue des phases ne se saute pas

Dès la clôture engagée, créer un TaskCreate `Clôture : revue des 4 phases` avant tout wrap-up, aligné sur le mécanisme de forcing du SKILL.md §7.2. Il passe à `completed` seulement après revue effective des quatre phases. Le récap final à l'user vient après. Sans ce forcing, la production d'un prompt de reprise tend à court-circuiter la substance — c'est précisément ce que la clôture empêche.

## Les quatre phases

Chaque phase est systématiquement passée en revue. Une phase sans matière est un no-op silencieux : on ne fabrique pas un audit quand rien n'a bougé, ni une structuration quand aucun normatif n'a dérivé. L'ordre compte — la mémoire d'abord, pour que la consolidation et l'audit travaillent sur un état déjà capturé.

1. **Prise de mémoire** — capturer les événements, décisions et interactions de la session non encore mémorisés, avec la trace des actions (fichiers créés / supprimés, éléments envoyés / partagés). Format et workflow : `memory.md`.
2. **Consolidation** — router les apprentissages durables au bon endroit : FAIRE répétable → skill, SAVOIR durable → fichier normatif, épisodique riche → mémoire. Doctrine et options de routage : `capitalise-workflow.md`. Une convention émergée passe le test « vrai demain ? » (`connaissance-vs-memoire.md`, `lessons.md`).
3. **Structuration** — si un fichier normatif a gonflé ou dérivé pendant la session, proposer refonte ou découpage : `maintenance-fichiers-racines.md`, `decoupage-progressif.md`.
4. **Audit** — cohérence de ce qui a été touché : sections normatives contradictoires (`audit-sections.md`), liens cassés et orphelins (`graph.py check`, `graphe.md`).

## Handoff optionnel

Le prompt de reprise n'a de sens que si le travail continue dans une nouvelle session — saturation atteinte, ou user qui enchaîne ailleurs. Après la revue des phases, le proposer dans ce seul cas :

> C'est rangé. Tu reprends ça dans une nouvelle session ? Je te prépare un prompt de reprise.

Si l'user clôt sans continuer, pas de handoff. S'il accepte ou l'a demandé d'emblée, produire le prompt selon `session-handoff.md`, qui s'appuie sur la mémoire de session déjà créée en phase 1.

## Recap minimal

Après la clôture, deux lignes maximum, NL pur, sans jargon : ce qui a été rangé, et le prompt de reprise s'il y en a un. Pas de description de la machinerie des phases.

> OK, j'ai noté l'essentiel et rangé le doc d'Acme.
