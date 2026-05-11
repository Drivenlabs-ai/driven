# me-md : Identité user dans le personal space

`ME.md` est le point d'entrée du personal space. Lu en premier par Claude au démarrage d'une session perso. Doit donner une vue stratégique de qui est le user en 30 secondes, puis pointer vers les détails dans `ME/<thème>.md` si la narrative grossit.

## Structure de base

```yaml
---
primary-email: alex@drivenlabs.ai
emails:
  - alex@drivenlabs.ai
  - contact@alexandre-bouchez.fr
name: Alexandre Bouchez
---
```

```markdown
# Alexandre Bouchez

[Phrase d'identification rapide : « Fondateur de Drivenlabs, agence IA. Dev de
formation. », lisible en 5 secondes.]

## Contexte business
[Activité actuelle, rôle, projets en cours, positionnement.]

## Contexte personnel (optionnel)
[Famille, contexte de vie pertinent pour la collaboration avec Claude.]

## Préférences
[Manière de travailler, communication, outils, rythme.]

## Index ME/
[Pointeurs vers les fichiers thématiques approfondis (si présents).]
```

## Distinction ME.md vs sous-dossier ME/

| ME.md | ME/<thème>.md |
|---|---|
| Vue stratégique 30 secondes | Deep dive sur un thème |
| Lisible par Claude à chaque session | Lu uniquement quand le thème est pertinent à la conversation |
| 30 à 100 lignes max | Pas de limite, peut être substantiel |
| Mis à jour rarement (changements structurels uniquement) | Mis à jour au fil de l'apprentissage |

Le sous-dossier `ME/` émerge quand `ME.md` grossit. Pas créé vide au SETUP.

## Sujets typiques de `ME/<thème>.md`

| Fichier | Contenu |
|---|---|
| `ME/business.md` | Détail du business, projets, partenaires, contexte économique |
| `ME/relations.md` | Personnes importantes (famille, équipe proche, mentors) |
| `ME/preferences.md` | Workflow, outils, rythme, préférences fines |
| `ME/history.md` | Parcours, événements marquants, leçons apprises |
| `ME/sante.md` | Si pertinent et le user veut documenter (rare) |
| `ME/objectifs.md` | Objectifs long terme, vision, principes de vie |

Les noms exacts sont au choix. Claude propose en NL quand un thème mérite extraction.

## Quand mettre à jour ME.md

| Trigger | Action |
|---|---|
| User dit *« retiens que je travaille avec Maël maintenant »* | Update narrative business + members |
| User dit *« j'ai changé de positionnement »* | Refonte de la section business |
| User dit *« je veux que tu saches que je suis plus en mode focus dur en ce moment »* | Update préférences (peut être ponctuel ou durable, Claude infère) |
| Changement structurel (nouveau rôle, nouvelle entreprise, nouveau pays) | Refonte de la section identité + business |

Suivre la doctrine de maintenance holistique (cf `maintenance-fichiers-racines.md`) : refonte > ajout pour les changements structurels.

## Anti-pattern : ME.md ≠ SOUL.md

`ME.md` = qui est le user, son business, son contexte de vie.
`SOUL.md` = comment Claude se comporte vis-à-vis du user.

Ne pas mélanger. Si user dit *« sois plus direct avec moi »*, ça va dans SOUL.md, pas dans ME.md. Si user dit *« j'ai changé de poste »*, ça va dans ME.md, pas dans SOUL.md.

Si confusion, demander en NL :

> Tu me parles de toi (j'updaterais ME.md) ou de comment je devrais réagir (j'updaterais SOUL.md) ?

## Anti-pattern : ME.md ≠ VOICE/

`VOICE/` = comment le user écrit (surfaces, registres, tonalités).
`ME.md` = qui est le user.

Si user dit *« pour LinkedIn préfère du court »*, ça va dans `VOICE/surfaces/linkedin.md`, pas dans ME.md.

## Personal space privé

Le ME.md vit en personal space, jamais en shared. Aucune fuite vers shared sans acte conscient du user. Si user demande de partager son contexte business dans un shared, créer une fiche dédiée dans le shared (`Team/about-alex.md` ou équivalent), pas un lien direct vers le ME.md.

## Format narratif vs structuré

ME.md peut être :

- **Narratif** : paragraphes en prose, plus humain, lisible comme une présentation.
- **Structuré** : sections + bullets, plus rapide à scanner.

Au choix du user. Si pas de préférence, défaut narratif (plus naturel à lire et à maintenir).

## Récap après update

Deux lignes maximum.

> OK, j'ai noté que tu bosses avec Maël maintenant, mis à jour ton ME.md.

Pas de description détaillée. Si user veut voir le diff, il demande.
