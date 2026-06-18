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

Le CLAUDE.md à la racine peut porter un champ `space-type` qui détermine le scope du workspace.

- `space-type` (optionnel mais recommandé) : `personal` ou `shared`. Hint pour le plugin sur le profil à appliquer. En son absence, le plugin observe les autres signaux (`authors:`, `members:`, path Drive Desktop) et infre le type. Détail : `scope-check.md`.

`authors:` et `members:` sont **obligatoires uniquement si `space-type: shared`** ou si le contexte est shared inféré depuis les signaux disponibles. En personal ou hors workspace driven, ils n'ont pas lieu d'être.

### Personal space

```yaml
---
space-type: personal              # optionnel mais recommandé
last-updated: 2026-05-12
---
```

- `space-type: personal`, scope mono-user, pas d'`authors` ni de `members` (l'auteur est implicitement le user du `ME.md` racine).
- `last-updated`, date ISO de la dernière modification structurelle. Mise à jour automatique au write.

### Shared space

Un shared space porte en plus `authors` + `members:`, qui mappe chaque email au nom de l'auteur correspondant. Cette table sert au flow cross-author pour résoudre les emails en noms lisibles.

```yaml
---
space-type: shared                # optionnel mais recommandé
authors:                          # obligatoire en shared
  - alex@drivenlabs.ai
members:                          # obligatoire en shared
  - email: alex@drivenlabs.ai
    name: Alexandre Bouchez
  - email: jane@drivenlabs.ai
    name: Jane Doe
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

## Projet avec repo code associé

Un projet dont le travail technique vit dans un repo code déclare ce repo via un champ optionnel `code-repo`, dans le frontmatter du doc du projet (son CLAUDE.md ou le doc qui le porte) :

```yaml
---
code-repo: /Users/alexandrebouchez/Code/acme-app
---
```

- `code-repo`, chemin absolu du repo. Lu pour résoudre et lire la mémoire native du repo quand on travaille sur le projet (`memoire-projet-code.md` §pont).

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
  - jane@drivenlabs.ai
type: decision
topic: rdv-acme
confidence: verbatim
keywords:
  - acme
  - pricing
  - pack-sales
  - john-doe
  - negociation
---
```

- `date`, ISO `YYYY-MM-DD`, jamais en string.
- `time`, string `"HHMM"` (quoted pour préserver les zéros : `"0930"`).
- `authors`, liste, omise en personal space (mono-user implicite).
- `type` ∈ {`memory`, `decision`, `interaction`, `insight`, `other`}.
- `topic`, slug kebab-case court (2-4 mots), résumé du sujet de la mémoire.
- `confidence` (optionnel) ∈ {`verbatim`, `inferred`, `mixed`} : `verbatim` = reformulation factuelle de ce que l'user a dit ou décidé ; `inferred` = déduction de Claude non énoncée explicitement ; `mixed` = les deux. Inféré silencieusement à la création, jamais demandé au user, jamais inscrit dans le corps (clean slate). Les mémoires sans le champ sont traitées comme `verbatim`. Exploité par `challenge-anti-recidive.md` pour pondérer les signaux de rejet.
- `keywords`, liste de 5 à 10 mots-clés, couvrant variantes morphologiques + synonymes implicites. Critique pour la recherche BM25 (pondération ×3). Claude les infère silencieusement, pas un champ user-facing.

## Corps d'une memory entry

Après le frontmatter, deux sections obligatoires en shared, recommandées en perso :

```markdown
# RDV Acme 2026-05-11

## Contexte
[2-3 phrases self-contained : pourquoi cette mémoire existe, quel sujet, qui concerné.]

## Notes
[Contenu factuel, scope projet, RULE factualité en shared. Entités = liens markdown
vers des documents existants.]

## Sources
[Sources externes localisables + scripts utilisés (chemins). Optionnel, présent dès
qu'il y a des sources/outils externes. Détail : `memory.md` §Sources.]
```

Le préambule `## Contexte` est obligatoire en shared parce que les memory entries doivent être lisibles isolément, 6 mois plus tard, par un contributeur qui n'était pas dans la conversation. En personal space il reste recommandé mais peut être omis pour des notes très courtes.

## Contenu métier — statut et portée

Les contenus métier (briefs, plans de livrables, notes, fiches produit, decks…) portent deux propriétés que Claude infère à la production, sans validation de l'user :

```yaml
---
authors:
  - alex@drivenlabs.ai
status: wip
last-updated: 2026-06-18
---
```

- **`status: wip`** — artefact temporaire, étape d'un travail en cours (exploration, plan intermédiaire, itération susceptible d'être remplacée). Il **ne fait pas foi** : une session future ne le traite pas comme une référence établie, ne s'appuie pas dessus comme acquis, ne le généralise pas. Un contenu abouti, qui fait foi dans son périmètre, ne porte pas le champ (défaut). Ce n'est pas un statut de relecture — Claude classe selon la nature de l'info, l'user ne valide rien.
- **Portée contextuelle** — un contenu métier est lié à son contexte (un client, un livrable). Ce qui a été fait pour le client X ne s'applique pas au client Y : jamais une instruction universelle, même quand il fait foi. Seuls les fichiers normatifs portent de l'universel.

Ne s'applique pas aux normatifs (CLAUDE/RULES/ME/SOUL/VOICE/ABOUT/CONTRIBUTING) : leur autorité et leur modification sont déjà encadrées (`maintenance-fichiers-racines.md`).

## Règles d'écriture du frontmatter

- Toujours quoter les valeurs string qui pourraient être parsées comme nombre ou date (`time: "0930"`, jamais `time: 0930`).
- Les listes plates uniquement (pas de nested dicts dans `authors` ou `keywords`).
- L'ordre des champs n'est pas imposé mais reste consistant pour les memory entries (date, time, authors, type, topic, confidence, keywords).
- Pas de champs custom ad-hoc, si un besoin émerge, le proposer comme évolution du format, pas comme exception locale.

## Append-only par construction

Le frontmatter d'une memory entry est fixé à la création. La seule modification courante : ajout d'un email dans `authors` au cross-author (cf `references/cross-author.md`). Le nom du fichier (qui contient l'auteur initial) reste invariant.

Pour les fichiers normatifs (CLAUDE/RULES/CONTRIBUTING/ABOUT) : `last-updated` se met à jour automatiquement au write, `authors` accumule au cross-author. Reste structuré, jamais en plus de 4-5 champs.
