# maintenance-fichiers-racines : Refactor for coherence

⭐ Pattern critique contre la dérive long-terme des fichiers normatifs. Le défi : sans cette discipline, les CLAUDE/RULES/CONTRIBUTING/ME/SOUL/VOICE deviennent des stacks de micro-règles contradictoires accumulées au fil des sessions, et finissent par biaiser fortement Claude dans des directions non voulues.

## Principe central

> **Refactor for coherence, not add one more rule.**

Chaque modification d'un fichier normatif doit lire comme si la nouvelle vision avait toujours existé. Pas d'accumulation de patchs. Pas d'ajout au bout d'un fichier pour répondre à un input ponctuel. La cohérence interne du fichier compte plus que la trace de l'historique.

## Anti-pattern à bannir

```
[fichier SOUL.md, ajout en bas au fil des sessions]

## Voice
- Sois familier avec le user.

[2 semaines plus tard]

## Voice (suite)
- Ne sois pas trop familier.

[1 mois plus tard]

## Notes
- En fait, sois neutre.
```

Conséquences :
- Trois règles qui se contredisent.
- Claude raisonne sur la stack et adopte le ton selon laquelle il lit en dernier.
- Le fichier devient un journal d'erreurs, pas un état du monde.
- À 6 mois, le contenu est ingérable.

## Pattern attendu

Refonte holistique du fichier, sections cohérentes :

```
[SOUL.md, refondu]

## Voice & Tone
[Description du ton, refondu pour exclure la familiarité, ton neutre cohérent
dans tout le fichier. Pas de mention de l'ancienne directive.]

## Operational Constraints
[Cohérent avec le nouveau ton.]

## Interaction Style
[Cohérent.]
```

Le fichier final lit comme s'il avait toujours dit « ton neutre ». Pas de traces de la familiarité antérieure ni de la directive intermédiaire. Clean slate strict.

## Heuristique de détection : quand refondre vs quand ajouter

### Refondre (réécriture holistique)

Quand l'input user est de la forme :

- *« tu es trop X »*, *« sois moins Y »*, *« change ta posture sur Z »*
- *« on n'utilise plus ce ton »*, *« cette approche ne marche plus »*

→ **Refonte du fichier dans son ensemble**. Identifier les passages qui produisent le comportement à corriger, refondre leurs formulations dans une logique globale.

### Ajouter (modification locale)

Quand l'input user est de la forme :

- *« voici une nouvelle convention »*, *« ajoute cette règle »*, *« désormais on fait X »*
- Convention qui n'est pas en conflit avec l'existant

→ **Ajout possible**, mais Claude vérifie qu'aucun ajout antérieur ne la contredit avant d'écrire. Si conflit détecté, signaler en NL :

> Tu m'avais dit l'inverse il y a 2 mois dans le même fichier. On garde la nouvelle version et on retire l'ancienne, ou tu veux qu'elles cohabitent ?

### Refondre même si l'input est additif

Si plusieurs ajouts antérieurs touchent déjà le même domaine, **refonte recommandée même si l'input courant est additif**. Le bruit accumulé mérite un nettoyage.

Heuristique chiffrée : si 3+ règles sur le même thème dans un fichier → propose refonte plutôt que 4ème ajout.

## Anti-micromanagement

Les règles trop ciblées biaisent fortement Claude. Privilégier la compréhension globale plutôt que le micromanagement.

### Règle d'or

**Une règle ne s'ajoute que si user le demande explicitement et durablement.**

Pas de captures préventives. Pas d'écriture « au cas où ». Pas d'extrapolation d'une demande ponctuelle en règle générale.

### Neutre = rien

**L'absence de règle = état neutre.**

Si user dit « finalement on retire X », le fichier final ne mentionne plus X du tout. Pas de :

- « Anciennement on évitait X »
- « Note : la règle X a été retirée le 11/05 »
- Commentaire HTML qui garde trace

Le retrait est définitif et silencieux. Cohérent avec clean slate (cf SKILL.md §3).

### Exemple

User dit pendant une session : *« évite les emojis dans mes posts »*. Claude met à jour `VOICE/surfaces/linkedin.md`.

3 jours plus tard, user dit : *« finalement les emojis c'était bien, remets-les »*. Claude retire la directive du fichier, le fichier final ne mentionne **plus du tout** les emojis (ni pour, ni contre, ni en historique).

État neutre = état par défaut.

## Garde-fous opérationnels

### Avant modif d'un fichier normatif

Validation explicite en langage naturel via **AskUserQuestion** (doctrine du plugin, cf `askuserquestion.md`). Pas de question ouverte texte libre, mais des options pré-rédigées avec contexte décisionnel.

### Explication des répercussions d'usage avant validation

Avant chaque modification structurante d'un fichier normatif racine (CLAUDE.md, RULES.md, ME.md, SOUL.md, VOICE.md, CONTRIBUTING.md, ABOUT.md), Claude explique en langage naturel haut niveau **les conséquences concrètes d'usage** de la modification. Pas juste « tu confirmes ? » mais « voici ce qui changera dans ma manière de t'aider si on fait ça. OK ? ».

L'objectif : un user non-tech doit comprendre l'impact concret sur son quotidien avant de valider, pas juste cocher une case.

#### Exemples concrets

- **Retrait d'un fichier de la liste « à charger impérativement »** :

   > Attention, si on retire la lecture de `VOICE/VOICE.md`, je ne lirai plus ce fichier à chaque session. Les supports que je rédigerai pour tes contacts externes (mails, posts LinkedIn, brouillons) pourront ne pas refléter ta manière de parler. Tu es sûr ?

- **Suppression d'une section du CLAUDE.md racine** :

   > Si on supprime la section Conventions, les workflows internes qu'elle contient (revues, validation des devis, escalation) ne seront plus chargés d'office. Je devrai les redécouvrir à chaque session via la cascade, ce qui peut prendre du temps et créer des incohérences. OK pour quand même ?

- **Changement du `space-type` du workspace** :

   > Si on passe le workspace de personal à shared, la règle de factualité s'active sur toutes les mémoires créées ensuite (zéro émotion, zéro jugement) et chaque écriture tracera qui en est l'auteur. C'est une bascule structurante, pensée pour le collectif. C'est ce que tu veux ?

- **Ajout d'un fichier critique à la liste « à charger impérativement »** :

   > Si on ajoute la lecture de ce fichier à chaque session, il pèsera dans mon contexte tout le temps. Si son contenu évolue beaucoup, ça peut me biaiser dans des directions non voulues. Tu es sûr de vouloir le rendre obligatoire, ou tu préfères qu'il soit chargé seulement quand c'est pertinent ?

- **Retrait de la liste « members » d'un workspace shared** :

   > Si on retire ce membre de la liste, je ne pourrai plus le mentionner par son nom quand tu cites son email (ex : `alex@drivenlabs.ai`). Il continuera d'apparaître comme co-auteur des fichiers existants, mais nouveaux fichiers n'auront plus la résolution automatique. OK ?

#### Pattern d'invocation

Claude présente l'explication en bloc texte (pas dans une option AskUserQuestion — trop long), puis pose **une question AskUserQuestion** avec 2 options :

- « OK, applique cette modif »
- « Annuler, on en reste à l'existant »

Optionnellement une 3ème option : « Ajuste, voilà ce que je préfère » avec champ texte libre.

User dit oui → exécution. User dit non → silence et retour à l'état précédent.

### Pour les fichiers à criticité élevée

Alerte renforcée pour `RULES.md` racine d'un shared, `CONTRIBUTING.md` racine d'un shared, `CLAUDE.md` racine d'un shared :

> Ce fichier est réservé aux personnes plus expertes en gestion du système. Tu es sûr ?

Si user passe : continuer. Si user hésite : proposer de noter la demande en memory entry pour que la modif soit réfléchie plus tard.

### Pour les autres normatifs (ME, SOUL, VOICE, sous-CLAUDE)

Validation simple, pas d'alerte renforcée. Mais toujours la phrase explicite avant modif :

> Je mets ça dans SOUL.md. OK ?

### Pour la refonte holistique

Présenter le **résumé d'intention** avant d'écrire, pas un diff brut. Le diff brut est illisible pour un user non-tech.

> Je propose de refondre la section Voice & Tone pour qu'elle dise plutôt [résumé en 2-3 phrases]. OK ?

User valide l'intention, Claude écrit. Si user veut voir le détail avant exécution, il demande explicitement.

## Inspirations

Le pattern « refactor for coherence » est documenté dans plusieurs sources :

- **Ruben Hassid, RAPSE** (Repeat, Add, Permute, Suppress, Edit) : framework de manipulation de texte qui favorise la refonte sur l'addition.
- **Continue.dev, Issue #11671** : discussion sur la maintenance des prompts long-terme, observation que les stacks de règles ad-hoc dégradent rapidement la qualité du raisonnement.
- **Anthropic Prompt Engineering** : best practices sur la cohérence des system prompts, importance de la refonte vs ajout.

Pas de citation détaillée, ces sources informent l'approche, le contenu reste applicable indépendamment.

## Clean slate à l'édition (rappel)

Toute édition produit un fichier qui lit comme s'il avait toujours été ainsi. Bannis sauf mention contraire explicite user :

- « Anciennement X »
- « Avant on faisait Y »
- « Deprecated », « Obsolète »
- Notes changelog inline
- Commentaires HTML historiques

Détail dans le SKILL.md §3. Cette règle vit dans le plugin (invariant universel), pas dans les RULES.md du shared (overlay client).

## Récap au user après refonte

Deux lignes maximum.

> OK, j'ai refondu le ton de SOUL.md pour qu'il soit plus neutre. Le fichier est cohérent maintenant.

Pas de mention du diff, des sections touchées, des passages supprimés. Le user voit le résultat (le fichier final), pas la machinerie de refonte.

Si tech-level haut : recap peut détailler.

> OK, refonte de SOUL.md, sections Voice & Tone et Interaction Style alignées sur le ton neutre. 3 passages familiers supprimés.

## Exception : ajout ponctuel sans refonte

Toutes les modifs ne méritent pas une refonte. Si l'input user est manifestement additif et orthogonal au contenu existant (ex : *« ajoute que je préfère le format ISO pour les dates »* dans un fichier qui n'a aucune autre règle sur les dates), un ajout simple suffit.

Le jugement Claude : si l'ajout produit un fichier toujours cohérent et lisible, ajout possible. Si l'ajout crée du bruit ou de la redondance, refonte nécessaire.

En cas de doute, refonte > ajout. Le coût d'une refonte courte est inférieur au coût accumulé d'une stack de patchs.
