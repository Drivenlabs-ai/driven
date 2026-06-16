# routage : Table de routage de l'information

## Quand cette ref s'active

- Ambiguïté NL sur destination de l'info partagée par user (« où je note ça ? »).
- Input user qui touche plusieurs cibles potentielles (mémoire + fichier normatif + skill).
- Avant toute décision de placement non-évidente d'une info.
- Demande qui ressemble à une mémoire mais qui est en fait une convention durable (ou inversement).

⭐ Cœur du défi #1 : où mettre quoi ? Cette table guide Claude pour router toute demande user vers la bonne cible (mémoire, fichier de règle, document métier, nouveau skill, etc.) sans demander à chaque fois.

## Principe pivot

Test « vrai demain ? » + 3 principes fondateurs : `connaissance-vs-memoire.md`. La table ci-dessous en est la déclinaison opérationnelle.

## Principe directeur

Claude raisonne sur la **nature** de la demande user (événement ponctuel ? convention durable ? posture Claude ? identité user ? contenu produit ?) et route vers la cible appropriée. Si ambigu : une question NL, jamais un menu technique.

## Table de routage (12 cas)

| # | Nature de la demande | Cible | Exemples | Garde-fous |
|---|---|---|---|---|
| 1 | Événement timestampé (RDV, call, décision ponctuelle) | Memory entry dans `memory/` du dossier thématique | « RDV avec John Doe », « on a décidé de pricer à 8K », « j'ai eu un appel avec Acme » | Factualité active si shared. Naming `YYYY-MM-DD-HHMM-author-topic.md`. Contexte 2-3 phrases obligatoire. En repo code (cwd hors workspace driven) → mémoire native du repo (`memoire-projet-code.md`), pas l'espace perso. |
| 2 | Convention durable du team / dossier | `RULES.md` ou `CONTRIBUTING.md` du dossier shared | « on bosse toujours par sprints de 2 semaines », « pour les briefs client on suit la structure X », « tous les devis passent par Dougs » | Validation explicite. Maintenance holistique (cf `maintenance-fichiers-racines.md`). Critère criticité élevée si RULES racine. |
| 3 | Posture / interaction Claude | `SOUL.md` du personal space | « tu es trop familier », « challenge plus mes idées », « ne me complimente pas » | Refonte holistique du ton, pas ajout d'une ligne. Détail : `soul-md.md`. |
| 4 | Identité user (rôle, contexte business, situation) | `ME.md` (ou sous-dossier `ME/`) | « j'ai un nouveau rôle », « Drivenlabs change de positionnement », « j'ai recruté Jane Doe comme assistant » | Propose mise à jour narrative, propose refonte si changement structurel. |
| 5 | Voix sortante de l'user (comment l'user écrit) | `VOICE/voice-perso.md` ou `VOICE/surfaces/<surface>.md` | « pour LinkedIn préfère du court », « n'utilise plus tel mot dans mes mails », « registre plus direct sur les DMs » | Maintenance holistique de la surface concernée. Détail : `voice-md.md`. |
| 6 | Brand voice du team | `Brand/voice/` ou équivalent du shared | « le ton Drivenlabs sur le site est trop corporate », « notre voix devrait être plus directe » | Maintenance holistique. Validation explicite (touche un fichier normatif du shared). |
| 7 | Workflow répétitif automatisable | Nouveau skill custom (route vers `/skill-creator`) | « je veux automatiser la prospection LinkedIn chaque semaine », « à chaque devis envoyé, j'aimerais que tu fasses X automatiquement » | Rare. Ton pédagogique sans infantiliser. Détail : `skill-creator-routing.md`. |
| 8 | Contenu produit pour le travail (80 % des cas) | Markdown simple dans le dossier thématique | Brief client, positioning, deck, fiche produit, lead magnet, post draft, devis | Scope-check perso vs shared. Authors liste si shared. Pas de RULE factualité (c'est du contenu produit, pas une mémoire). |
| 9 | Mention d'une personne / organisation sans document | (a) Pas de lien si ponctuel ; (b) Création réelle si entité importante | « comme l'a dit John Doe dans son post » → pas de lien ; « j'ai rencontré John Doe, prospect » → propose création doc | Seuil de pertinence. Détail : `links.md`. **Jamais de stub**. |
| 10 | Modif d'un fichier RULES / CONTRIBUTING / CLAUDE racine team | RULES.md / CONTRIBUTING.md / CLAUDE.md du shared | « ajoute cette règle à notre fonctionnement », « le CLAUDE.md du dossier Acme doit aussi mentionner X » | Criticité élevée. Alerte pédagogique avant modif. Validation explicite. Maintenance holistique. |
| 11 | Demande exhaustive sur une entité connue | Vue assemblée via `explain` : fiche + arêtes + mémoires liées, pas une recherche de mots | « qu'est-ce qu'on sait sur Acme », « montre tout sur X », « fais-moi une fiche sur John Doe » → `explain <entité>` | `graphe.md`. Restituer en NL, jamais le JSON. |
| 12 | Demande de lien entre deux entités | Plus court chemin via `path` | « quel est le lien entre Acme et John Doe », « comment A et B sont liés » → `path <A> <B>` | `graphe.md`. Si ambigu, demander lequel. |

## Principes en prose

### Ambiguïté → demande en NL

Quand le routage est ambigu, Claude demande en langage naturel, jamais par catégorie technique. Exemples :

> Je peux mettre ça comme une note ponctuelle, ou tu veux que ce soit une règle qui s'applique à chaque session ?

> Je crée un doc pour ça ou je le mentionne juste sans créer ?

> Tu veux que je note la décision dans Acme, ou que ça remonte dans le RULES de Drivenlabs ?

Le user choisit en deux mots, pas en parcourant un menu.

### Pour tout fichier normatif → toujours valider

Tout routage qui touche un fichier de la catégorie « normatif » (CLAUDE/RULES/CONTRIBUTING/ME/SOUL/VOICE/ABOUT) → validation explicite en NL **avant** modification. Le coût d'une question est inférieur au coût d'une modification non désirée.

Pour les fichiers à criticité élevée (RULES racine, CONTRIBUTING racine, CLAUDE racine d'un shared) → alerte renforcée :

> Ce fichier est réservé aux personnes plus expertes en gestion du système. Tu es sûr ?

Pour les autres (ME, SOUL, VOICE, sous-CLAUDE) → validation simple, pas d'alerte renforcée.

### Workflows répétitifs → /skill-creator

Si user décrit une tâche qu'il va refaire plusieurs fois avec des variations (extraction d'un type de données récurrent, génération d'un livrable templatisé, automatisation d'un workflow), router vers `/skill-creator` avec ton pédagogique :

> Ça ressemble à un truc que tu vas refaire souvent. On en fait un skill dédié pour que ça soit automatique la prochaine fois ?

Pas d'infantilisation. Si user dit non, abandon. Détail : `skill-creator-routing.md`.

### Verbosité du recap dépend du tech-level

Le recap au user après routage suit le tech-level inféré (cf `verbosity-tech-level.md`) :

- **Tech bas** (défaut Cowork, user non-tech) : *« OK, j'ai retenu. »*
- **Tech haut** (défaut Code, user dev) : *« OK, ajouté une décision dans `Clients/Acme/memory/` avec liens vers le pricing et le brief. »*

Pas de description verbeuse de la mécanique de routage dans aucun cas.

## Cas tordus (jugement Claude)

### Demande qui touche plusieurs cibles

Si une demande user touche plusieurs cibles (ex : « on a décidé que désormais tous les devis Acme suivent la structure X » → memory entry pour la décision + update du `CONTRIBUTING.md` Acme pour la convention), faire les deux. Pas de choix forcé.

Recap unifié au user :

> OK, j'ai noté la décision dans Acme et mis à jour la convention dans le doc du dossier.

### Demande qui pourrait être obsolète

Si une convention que l'user veut ajouter contredit une convention existante (ailleurs dans le workspace), signaler en NL avant d'écrire :

> Il y a déjà une convention sur les sprints dans `RULES.md` qui dit X. Tu veux qu'on la remplace par celle-ci ou tu veux qu'elles cohabitent ?

Évite la pollution de règles contradictoires (cf `maintenance-fichiers-racines.md` anti-pattern).

### Demande qui ressemble à une mémoire mais qui est en fait une convention

Pattern fréquent : user dit « note que je veux qu'on fasse toujours X comme ça ». Ce n'est pas une mémoire ponctuelle, c'est une convention durable.

Détecter le signal d'universalité (« toujours », « désormais », « à chaque fois », « par défaut ») → router vers RULES/CONTRIBUTING au lieu de memory.

Si user confond : reformuler en NL la nature de ce qu'on s'apprête à écrire :

> Tu me décris une convention qui s'applique à chaque session. Je mets ça dans le doc des règles plutôt qu'en mémoire ?

## Quand le user introduit explicitement la cible

Si user dit « ajoute ça au CLAUDE.md d'Acme » ou « note dans le SOUL.md que tu dois être plus direct », pas de routage à inférer, exécuter directement, après validation explicite si fichier normatif (cf principes ci-dessus).

L'inférence ne sert qu'en absence de cible explicite.
