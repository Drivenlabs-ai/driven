# frontmatter : Formats YAML par type de fichier

Tout fichier structuré du workspace porte un frontmatter YAML en tête entre deux `---`. Le plugin l'écrit et le maintient automatiquement. Le user ne le tape jamais à la main.

## ME.md (personal space, racine)

```yaml
---
primary-email: alex@drivenlabs.ai
emails:
  - alex@drivenlabs.ai
  - contact@alexandre-bouchez.fr
name: Alexandre Bouchez
---
```

- `primary-email`, email principal du user. Sert d'identifiant dans les `authors` lists des shared spaces.
- `emails`, tous les emails dont le user est titulaire. Permet de matcher contre `authors` quel que soit l'alias.
- `name`, nom complet, utilisé dans les recaps en langage naturel.

## CLAUDE.md racine d'un workspace driven

Le CLAUDE.md à la racine porte un champ `space-type` qui détermine le scope du workspace. C'est le signal d'activation des comportements workspace du plugin (cf `scope-check.md`) : sa présence dans le frontmatter — avec valeur `personal` ou `shared` — fait du dossier la racine d'un workspace driven.

### Personal space

```yaml
---
space-type: personal              # OBLIGATOIRE — détermine le scope du workspace
last-updated: 2026-05-12
---
```

- `space-type: personal`, scope mono-user, pas d'`authors` ni de `members` (l'auteur est implicitement le user du `ME.md` racine).
- `last-updated`, date ISO de la dernière modification structurelle. Mise à jour automatique au write.

### Shared space

Un shared space porte en plus `authors` + `members:`, qui mappe chaque email au nom de l'auteur correspondant. Cette table sert au flow cross-author pour résoudre les emails en noms lisibles.

```yaml
---
space-type: shared                # OBLIGATOIRE — détermine le scope du workspace
authors:                          # OBLIGATOIRE en shared
  - alex@drivenlabs.ai
members:                          # OBLIGATOIRE en shared
  - email: alex@drivenlabs.ai
    name: Alexandre Bouchez
  - email: mael@drivenlabs.ai
    name: Maël Urien
last-updated: 2026-05-12
---
```

- `authors`, liste plate (pas de hiérarchie owner/contributeur), ordre première contribution.
- `members` (CLAUDE.md racine uniquement), liste plate de mappings `email + name`. Maintenue manuellement à chaque onboarding d'un nouveau membre. Le plugin lit cette table en début de session pour résoudre les emails dans les questions cross-author. Le `name:` est libre : prénom (« Alex »), nom complet (« Alexandre Bouchez »), surnom (« AB »), comme le member souhaite être nommé dans les questions.
- `last-updated`, date ISO de la dernière modification structurelle. Mise à jour automatique au write.

## CLAUDE.md de sous-dossier (shared space)

Pas de `members:` dans les sous-dossiers (pas dupliqué, la table racine fait foi).

```yaml
---
authors:
  - alex@drivenlabs.ai
last-updated: 2026-05-12
---
```

## CONTRIBUTING.md (sous-dossier sélectif, shared)

Même frontmatter que `CLAUDE.md` shared :

```yaml
---
authors:
  - alex@drivenlabs.ai
last-updated: 2026-05-11
---
```

`CONTRIBUTING.md` documente les conventions locales d'un sous-dossier quand elles divergent de la racine. Optionnel.

## RULES.md / RULES/<thème>.md (shared)

Mêmes champs `authors` + `last-updated`. Pas de hiérarchie de criticité dans le frontmatter, c'est le nom du fichier qui signale la nature normative.

## ABOUT.md (shared)

Mêmes champs `authors` + `last-updated`. Sert quand la section « À propos » du CLAUDE.md racine grossit et mérite extraction (cf `decoupage-progressif.md`).

## Memory entry (perso ou shared)

```yaml
---
date: 2026-05-11
time: "1430"
authors:
  - mael@drivenlabs.ai
type: decision
topic: rdv-olenbee
keywords:
  - olenbee
  - pricing
  - pack-sales
  - laurent-urien
  - negociation
---
```

- `date`, ISO `YYYY-MM-DD`, jamais en string.
- `time`, string `"HHMM"` (quoted pour préserver les zéros : `"0930"`).
- `authors`, liste, omise en personal space (mono-user implicite).
- `type` ∈ {`memory`, `decision`, `interaction`, `insight`, `other`}.
- `topic`, slug kebab-case court (2-4 mots), résumé du sujet de la mémoire.
- `keywords`, liste de 5 à 10 mots-clés, couvrant variantes morphologiques + synonymes implicites. Critique pour la recherche BM25 (pondération ×3). Claude les infère silencieusement, pas un champ user-facing.

## Corps d'une memory entry

Après le frontmatter, deux sections obligatoires en shared, recommandées en perso :

```markdown
# RDV Olenbee 2026-05-11

## Contexte
[2-3 phrases self-contained : pourquoi cette mémoire existe, quel sujet, qui concerné.]

## Notes
[Contenu factuel, scope projet, RULE factualité en shared. Entités = liens markdown
vers des documents existants.]
```

Le préambule `## Contexte` est obligatoire en shared parce que les memory entries doivent être lisibles isolément, 6 mois plus tard, par un contributeur qui n'était pas dans la conversation. En personal space il reste recommandé mais peut être omis pour des notes très courtes.

## Règles d'écriture du frontmatter

- Toujours quoter les valeurs string qui pourraient être parsées comme nombre ou date (`time: "0930"`, jamais `time: 0930`).
- Les listes plates uniquement (pas de nested dicts dans `authors` ou `keywords`).
- L'ordre des champs n'est pas imposé mais reste consistant pour les memory entries (date, time, authors, type, topic, keywords).
- Pas de champs custom ad-hoc, si un besoin émerge, le proposer comme évolution du format, pas comme exception locale.

## Append-only par construction

Le frontmatter d'une memory entry est fixé à la création. La seule modification courante : ajout d'un email dans `authors` au cross-author (cf `references/cross-author.md`). Le nom du fichier (qui contient l'auteur initial) reste invariant.

Pour les fichiers normatifs (CLAUDE/RULES/CONTRIBUTING/ABOUT) : `last-updated` se met à jour automatiquement au write, `authors` accumule au cross-author. Reste structuré, jamais en plus de 4-5 champs.
