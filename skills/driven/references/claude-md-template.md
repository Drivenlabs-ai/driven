# claude-md-template : Structure du CLAUDE.md racine d'un shared space

Le `CLAUDE.md` racine est le point d'entrée du shared space. Il est lu en premier par Claude au démarrage de session. Sa structure doit permettre à un contributeur (humain ou Claude) d'avoir une vue stratégique en 30 secondes, puis de naviguer vers les détails.

## Structure universelle : 4 sections

Le template commence avec un **meta header** qui pointe vers le plugin, puis 4 sections au choix selon les besoins du shared.

Le frontmatter du CLAUDE.md **racine** porte `authors`, `last-updated`, et la table `members:` (résolution email → nom utilisée par le flow cross-author) :

```yaml
---
authors:
  - alex@drivenlabs.ai
last-updated: 2026-05-12
members:
  - email: alex@drivenlabs.ai
    name: Alexandre Bouchez
  - email: mael@drivenlabs.ai
    name: Maël Urien
---
```

```markdown
# <Nom du shared space>

[Header optionnel : 1 phrase qui résume la mission du shared space, lisible
en 5 secondes par un contributeur qui découvre le dossier.]

## À propos

[Identité, mission, scope, members, objectifs.]

## Conventions (optionnel)

[Workflows, règles locales, glossaire, rituels.]

## Environnement (optionnel)

[Outils, stakeholders, zones rouges, connections externes.]

## Index

[Arborescence hiérarchique des fichiers et sous-dossiers du shared.]
```

## Section 1 : À propos (obligatoire)

Définit l'identité du shared space pour un nouveau contributeur.

Contenu typique :
- **Mission** : pourquoi ce shared space existe (ex : « Drivenlabs Team, espace partagé pour piloter l'agence IA »).
- **Scope** : ce qui est inclus, ce qui est exclu.
- **Members** : liste des emails de l'équipe, avec une phrase sur le rôle de chacun.
- **Objectifs** : direction stratégique, jalons en cours (rare, optionnel).

À conserver concis : 5 à 15 lignes. Si la section gonfle (> 30 lignes), extraire dans `ABOUT.md` à la racine et garder un résumé 3 lignes ici qui pointe le détail.

## Section 2 : Conventions (optionnelle)

Workflows et règles internes au shared. Différent des invariants du plugin : ici on documente ce qui est **spécifique au shared** (vs ce que `driven` impose partout).

Contenu typique :
- **Workflows** : ex « tous les briefs client passent par la structure X », « les retros se font le vendredi ».
- **Glossaire** : termes métier ou acronymes propres au shared.
- **Rituels** : réunions récurrentes, format des updates, etc.

Quand cette section dépasse 30-50 lignes, la décomposer en `RULES.md` + éventuellement `RULES/<thème>.md`. Détail : `references/decoupage-progressif.md`.

## Section 3 : Environnement (optionnelle)

Contexte externe du shared : outils, partenaires, contraintes.

Contenu typique :
- **Outils** : ex « facturation via Dougs », « prospection via Lemlist », « stockage Drive ».
- **Stakeholders externes** : clients, partenaires récurrents, prescripteurs.
- **Zones rouges** : sujets sensibles, NDA en cours, infos à ne jamais sortir du shared.
- **Connections** : comptes liés, accès partagés, etc.

Optionnel parce que beaucoup de shared spaces n'en ont pas besoin (petite équipe focalisée, projet isolé). Si présent, garder concis et factuel.

## Section 4 : Index (obligatoire, auto-regen)

Arborescence hiérarchique du shared space, mise à jour automatiquement par le plugin à chaque création/suppression/renommage de fichier.

Format :

```markdown
## Index

- `Clients/`, clients suivis (un sous-dossier par client)
- `Drivenlabs/`, business core (positioning, brochure, prospection)
- `Content/`, production de contenu (LinkedIn, Substack, X)
- `Partenaires/`, partenaires stratégiques
- `Admin/`, administratif (devis, factures, contrats)
```

Le plugin maintient cet index. Le user n'y touche pas à la main. Pour les sous-dossiers profonds, l'index racine reste de niveau 1-2 (vue stratégique), et chaque sous-dossier maintient son propre index dans son CLAUDE.md local.

## Découpage progressif

À mesure que le shared grossit, les sections sont extraites vers des fichiers dédiés :

| Section qui gonfle | Extraction vers |
|---|---|
| À propos > 30 lignes | `ABOUT.md` à la racine, résumé 3 lignes dans CLAUDE.md |
| Conventions > 30-50 lignes | `RULES.md` à la racine |
| Workflows particuliers | `CONTRIBUTING.md` à la racine ou par sous-dossier |
| Règles thématiques (ex politique de naming, sécurité, voix) | `RULES/<thème>.md` |

Pas de seuil chiffré strict, Claude raisonne au cas par cas selon la densité et la pertinence audience. Détail : `references/decoupage-progressif.md`.

## Personal space : variation

Le `CLAUDE.md` du personal space suit la même structure de base, avec des sections adaptées :

- **À propos** : projet personnel, état d'esprit du moment, contexte de vie.
- **Conventions** : préférences personnelles (organisation, naming).
- **Environnement** : outils, contacts récurrents, projets parallèles.
- **Index** : arborescence du personal space.

Pas de frontmatter `authors` (mono-user implicite). `last-updated` reste utile.

## Pas de pattern imposé pour le CLAUDE.md d'un sous-dossier business

Les sous-dossiers (`Clients/Olenbee/CLAUDE.md`, `Drivenlabs/Driven-Sales/CLAUDE.md`) suivent une structure plus libre, adaptée au domaine. Le pattern 4-sections est la **valeur par défaut** pour la racine d'un shared/personal space, pas une obligation universelle.

Claude juge la structure contextuelle selon les principes (SSOT, progressive disclosure). Chaque domaine a ses contraintes et son audience naturelle.

## Création initiale (au SETUP du shared)

Quand un nouveau shared space est instancié depuis le template, le `CLAUDE.md` initial est minimaliste :

```markdown
---
authors:
  - alex@drivenlabs.ai
last-updated: 2026-05-11
---

# Drivenlabs Team

Espace partagé pour piloter l'agence Drivenlabs.

## À propos

Drivenlabs est une agence IA qui aide les PME à tirer parti de l'IA. Cet espace
partagé regroupe le pilotage de l'agence : business, clients, contenu, prospection.

Members :
- alex@drivenlabs.ai, fondateur
- mael@drivenlabs.ai, assistant LinkedIn et prospection

## Index

(auto-regen)
```

Les sections Conventions et Environnement émergent organiquement au fil de l'usage, pas créées vides.
