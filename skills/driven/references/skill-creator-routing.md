# skill-creator-routing : Quand router vers `/skill-creator`

Certaines demandes user signalent un workflow répétitif qui mériterait son propre skill custom plutôt qu'une exécution manuelle à chaque fois. Dans ces cas, router vers `/skill-creator` (skill Anthropic existant) avec ton pédagogique.

## Détection du signal

User décrit une **tâche qu'il va refaire plusieurs fois avec des variations**. Signaux :

| Signal | Exemple |
|---|---|
| « À chaque fois que … » | *« À chaque fois que j'envoie un devis, j'aimerais que tu fasses X »* |
| « Tous les [intervalle] » | *« Tous les lundis je veux scanner les emails et te demander de me résumer »* |
| « Pour chaque [type] » | *« Pour chaque nouveau prospect je veux un brief structuré identique »* |
| « Je le fais souvent et je veux automatiser » | *« Je fais ça souvent et c'est pénible à refaire à la main »* |
| Description d'un workflow structuré avec étapes répétables | *« Je récupère X, je vérifie Y, je génère Z dans le format W »* |

## Cas d'usage typiques

| Workflow user | Skill custom possible |
|---|---|
| Préparation hebdomadaire du contenu LinkedIn | Skill `/weekly-linkedin` qui scan les sujets de la semaine + propose 3 posts draft |
| Brief d'un nouveau prospect (structure récurrente) | Skill `/prospect-brief` qui prend un nom + une URL et génère le brief |
| Recap de fin de journée business | Skill `/eod-recap` qui scan les memory entries du jour et génère un résumé |
| Génération d'un devis depuis une demande client | Déjà couvert par `/dougs:create-quote`, mais variantes possibles |
| Audit hebdomadaire du workspace | Skill `/weekly-audit` qui scan les fichiers normatifs et propose les modifications |

## Ton de la proposition

Pédagogique sans infantiliser. Le user n'a pas besoin de connaître les détails de l'architecture skill, juste de comprendre que c'est faisable et utile.

Format type :

> Ça ressemble à un truc que tu vas refaire souvent. Tu veux qu'on en fasse un skill dédié pour que ça soit automatique la prochaine fois ?

Pas de jargon (« plugin », « skill activator », « frontmatter description »). Phrasing naturel.

## Si user dit oui

1. Inviter à invoquer `/skill-creator` (le skill Anthropic standard).
2. Optionnel : pré-charger le contexte (description du workflow, fichiers types, output attendu) dans le prompt initial pour faciliter la création.

Le plugin `driven` ne crée pas le skill lui-même, c'est `/skill-creator` qui gère.

## Si user dit non

Pas de pression. Continuer à exécuter manuellement. Re-proposer si le pattern revient plusieurs fois dans des sessions suivantes (signal qu'un skill serait vraiment utile).

## Anti-pattern : router trop systématiquement

Tout workflow répété n'est pas un candidat skill. Exclure :

- Workflows qui changent à chaque exécution (pas vraiment automatisable).
- Workflows ponctuels (un seul mois d'activité, projet temporaire).
- Workflows qui ne suivent pas un pattern reproductible.
- Workflows déjà couverts par un skill existant (vérifier la liste des skills installés avant de proposer).

Si flou, demander en NL :

> Tu fais ça comment d'habitude ? Si c'est toujours le même processus, on peut le scripter ; si ça varie, ça vaut peut-être pas le coup.

## Cas rare

Le routage vers `/skill-creator` reste **rare** en pratique. La plupart des demandes user vont vers les autres cibles de routage (memory entry, fichier normatif, doc métier). Détail : `routage.md`.

## Récap au user

Si user accepte la proposition skill : 

> OK, lance `/skill-creator` quand tu veux. Je te file le contexte du workflow.

Si user refuse : exécuter la demande manuellement, sans plus aborder le sujet skill (sauf récurrence).
