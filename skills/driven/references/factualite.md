# factualite : Reformulation silencieuse en shared space

En shared space, les mémoires et documents collectifs doivent être lisibles isolément 6 mois plus tard par un contributeur qui n'était pas dans la conversation. Les jugements personnels, émotions du rédacteur, hors-scope projet et spéculations comme certitudes brouillent cette lisibilité.

La RULE de factualité est **active en shared space, désactivée en personal space**. Le plugin reformule silencieusement les passages non-factuels avant écriture, clean slate, sans laisser de trace de la formulation originale.

## 4 heuristiques de détection

### 1. Jugements sur des personnes

Évaluation subjective d'une capacité ou d'un comportement.

| Avant | Après |
|---|---|
| « X est lent à répondre » | « Le suivi de X prend en moyenne 3 jours par message (3 derniers échanges). » |
| « Y manque de rigueur sur les chiffres » | « Le devis de Y présente 2 erreurs de calcul sur les 3 derniers envois. » |
| « Z est compétent » | « Z a livré les 4 derniers projets dans les délais avec retours client positifs. » |

Remplacer le jugement par le fait observable qui aurait pu le produire. Si pas de fait disponible, supprimer le jugement entièrement.

### 2. Émotions du rédacteur

Tonalité affective qui colore la mémoire (tendu, stressé, ravi, agacé, frustré).

| Avant | Après |
|---|---|
| « RDV tendu avec John Doe » | « RDV avec John Doe sur le pricing. Désaccord exprimé sur la borne haute (12K), John Doe propose 8K. » |
| « Réunion super productive avec l'équipe » | « Réunion équipe : 3 décisions prises (pricing pack, timeline Acme, embauche stagiaire). » |
| « J'étais déçu du retour client » | « Retour client : 2 points négatifs (délai, qualité du brief). 1 point positif (réactivité). » |

L'émotion est remplacée par la description du fait qui l'a produite. Plus utile pour la lecture future.

### 3. Hors-scope projet

Contexte personnel, météo, apparence, santé, etc. qui n'apporte rien à la décision business.

| Avant | Après |
|---|---|
| « RDV avec John Doe, il pleuvait, il avait l'air fatigué » | « RDV avec John Doe sur le pricing pack Acme. Décision : alignement à 8K. » |
| « Call avec Jane Doe, je venais juste de finir mon café » | « Call avec Jane Doe sur le brief Acme. Validation des 3 axes. » |

Le hors-scope est supprimé. Pas reformulé, on coupe.

### 4. Spéculation présentée comme fait

Intention future ou hypothèse présentée comme certitude.

| Avant | Après |
|---|---|
| « John Doe va valider le devis » | « John Doe doit confirmer le devis d'ici fin de semaine (échange du 11/05). » |
| « On va signer avec Acme la semaine prochaine » | « Acme a indiqué une intention de signer la semaine prochaine. Pas de confirmation écrite. » |
| « Le pricing pack va plaire » | « Le pricing pack répond aux 3 critères exprimés par Acme le 11/05. Validation attendue. » |

La spéculation est rendue explicite (« doit confirmer », « a indiqué », « attendue »). Le fait reste, l'extrapolation est tempérée.

## Workflow de reformulation silencieuse

1. User demande à Claude de retenir une info.
2. Claude détecte que c'est shared space (cf `scope-check.md`).
3. Avant écriture, scan le contenu prévu contre les 4 heuristiques.
4. Reformulation silencieuse des passages détectés.
5. Écriture de la mémoire avec le contenu factuel.
6. Recap minimal au user, pas de mention de la reformulation. Le document apparaît comme s'il avait toujours été factuel (cf clean slate, SKILL.md §4).

Aucune note de bas de fichier (« reformulé pour factualité »), aucun flag frontmatter, aucun commentaire HTML. Le clean slate est strict.

## Option « mets ça dans l'espace perso »

Si le user insiste sur le subjectif, ou si la reformulation supprime un élément qu'il veut garder (frustration, ressenti, intuition non factualisable), proposer en NL :

> Si tu veux garder ce que tu ressens, je peux mettre ça ailleurs juste pour toi.

Si user accepte : créer une mémoire dans le personal space miroir (path parallèle), gardant la formulation brute. Si user refuse : la version shared factuelle reste, l'élément subjectif est perdu pour la mémoire collective (assumé).

## Cas hybride

Une note peut avoir une part factuelle légitime en shared et une part subjective qui irait mieux en perso. Dans ce cas :

1. Extraire la part factuelle vers la mémoire shared.
2. Proposer en NL : *« Je mets le contexte personnel dans l'espace perso, et l'essentiel dans l'espace partagé Drivenlabs Team. »*
3. Créer les deux mémoires, avec lien réciproque (markdown standard).

## Désactivation en personal space

En personal space, la RULE est désactivée. Les mémoires gardent émotion, jugement, hors-scope, spéculation. Le personal space est la zone d'écriture brute, sans filtre.

Si user demande d'écrire en personal une note qui finira probablement reformulée en shared plus tard (brouillon préparatoire), pas de reformulation à ce stade. La reformulation se fera quand le mouvement perso → shared aura lieu (cf `cross-author.md` flow migration).

## Heuristiques additionnelles (à raisonner cas par cas)

Au-delà des 4 catégories explicites, Claude peut détecter d'autres patterns problématiques :

- **Données personnelles d'un tiers** (santé, situation familiale, sexualité), demande NL : *« Ces infos sur John Doe, on les garde dans l'espace perso ou dans l'espace partagé ? »*
- **Conflit avec un partenaire** : détection contextuelle, propose perso ou reformulation neutre.
- **Critique implicite de l'équipe** : souvent un mélange jugement + émotion, traiter via 1+2.

Pas de table exhaustive. Claude raisonne sur le contexte et propose en cas de doute.

## Différence avec stop-slop

`/stop-slop` filtre les patterns d'écriture IA et corporate avant un contenu à partage externe (post LinkedIn, email commercial, brief client). La RULE de factualité filtre les jugements/émotions/spéculation dans le contenu interne du workspace shared.

Les deux sont complémentaires : factualité = clarté du contenu interne pour les contributeurs ; stop-slop = qualité du contenu externe pour les destinataires. Détail : `references/stop-slop-routing.md`.
