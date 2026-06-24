# interface-cli : Comportement de `/driven` explicite

La commande slash `/driven` est rarement tapée explicitement, le plugin s'active automatiquement dès détection d'un CLAUDE.md racine avec frontmatter `space-type` + d'un trigger. Mais l'invocation explicite reste utile pour forcer un comportement, faire un audit, ou utiliser la recherche BM25.

## 3 modes d'invocation

### 1. Sans argument

`/driven`

Afficher un récap du contexte courant + actions pertinentes.

Format type :

```
Workspace driven détecté en `~/Personal OS/` (personal).
Fichiers normatifs présents : CLAUDE.md, ME.md, SOUL.md, VOICE/, RULES.md.

Actions possibles :
- Retenir une info ponctuelle
- Auditer un fichier (« audite SOUL.md »)
- Mettre à jour une convention
- Migrer une note vers le partagé (« mets ça dans Drivenlabs Team »)
- Chercher dans les mémoires (« cherche les mémoires sur le pricing »)

Tu veux faire quoi ?
```

Adapté au workspace détecté (perso vs shared, fichiers présents).

### 2. Avec argument : nom d'action explicite

| Argument | Action |
|---|---|
| `/driven context "sujet"` | Récupère le contexte du sujet avant de bosser : normatifs + interne (arborescence, BM25, graphe) + canaux externes pointés. Charge `recuperation-contexte.md`. |
| `/driven search "query"` | Recherche BM25 dans les mémoires du scope courant. Invocation du script Python. |
| `/driven explain "entité"` | Fiche d'une entité : ses liens, arêtes et mémoires connexes. Invocation de `scripts/graph.py explain`. |
| `/driven path "A" "B"` | Plus court chemin entre deux entités du workspace. Invocation de `scripts/graph.py path`. |
| `/driven audit` | Audit holistique du CLAUDE.md racine et de ses sections (cf `audit-sections.md`). |
| `/driven audit [fichier]` | Audit d'un fichier spécifique. |
| `/driven migrate` | Migration d'une note du personal vers un shared (cross-author simplified, factualité proposée). |
| `/driven setup-doc` | Création guidée d'un nouveau document structuré dans le workspace. |

Charger la reference correspondante et exécuter.

### 3. Avec argument : intention en langage naturel

`/driven retiens que John Doe a changé le tarif`
`/driven note ça pour Acme`
`/driven crée un doc pour John Doe`
`/driven le SOUL.md est trop strict, refonds-le`

Inférer l'action depuis `references/routage.md`, charger les références pertinentes, exécuter.

Pas de parsing strict, l'intention est lue en NL et Claude raisonne. Si ambigu, demander une question NL.

## Différence avec activation automatique

| Activation auto | Invocation `/driven` explicite |
|---|---|
| Trigger conversationnel (« retiens ça », mention entité, modif règle) | User tape `/driven` ou `/driven <arg>` |
| Plugin s'active silencieusement, agit selon contexte | Plugin force un mode d'action explicite |
| Pas de récap stratégique du workspace | Récap stratégique (mode sans argument) |

Le user n'a typiquement **pas besoin** de taper `/driven`. C'est un raccourci pour les power users ou pour des cas spécifiques (force un audit, force une recherche).

## `/driven context` : passe de récupération de contexte

```
/driven context "sujet"
```

Charge `recuperation-contexte.md` et exécute la passe : cadre normatif, contexte interne du workspace (arborescence, search BM25, graphe d'entités), canaux externes pointés par l'interne, puis restitution NL de l'état des lieux et amorce de travail. Détail et garde-fous : `recuperation-contexte.md`.

## `/driven search` : invocation du script Python

```
/driven search "query" [--scope=path] [--top=N]
```

Mapping vers :

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/search_memories.py" \
  "query expanded with synonyms" \
  --scope="<scope inferred or default cwd>" \
  --top=<N or 20>
```

Workflow :

1. User invoque `/driven search "pricing acme"`.
2. Claude **expand** la query avec des synonymes (pricing → pricing, tarif, tariff, pricing-pack, sales-pack, offre).
3. Claude détermine le scope (par défaut : cwd workspace racine si user dans le workspace driven, sinon path passé en flag).
4. Invocation du script via Bash tool.
5. Parsing du JSON output (top 20 path + score + préambule).
6. Restitution au user en NL : top 3-5 hits avec préambule lisible, lien vers chaque mémoire pour le détail.

Format type de restitution :

```
J'ai trouvé 5 mémoires pertinentes sur le pricing Acme :

1. [Décision pricing 11/05](Clients/Acme/memory/2026-05-11-1430-jane-decision-pricing.md)
   RDV pricing du 11/05. John Doe propose 8K, alignement validé en réunion.

2. [Révision pricing 14/05](Clients/Acme/memory/2026-05-14-0900-jane-revision-pricing.md)
   Révision à 10K après nouveau brief Acme.

3. [...]

Tu veux que je détaille une mémoire en particulier ?
```

## `/driven explain` et `/driven path` : invocation du script graphe

Mapping vers `scripts/graph.py` (cf `graphe.md` pour le détail des sous-commandes et le format de restitution) :

```
/driven explain "Acme"      → python "${CLAUDE_PLUGIN_ROOT}/scripts/graph.py" explain "Acme" --scope=<racine>
/driven path "Acme" "Acme"  → python "${CLAUDE_PLUGIN_ROOT}/scripts/graph.py" path "Acme" "Acme" --scope=<racine>
```

Restitution en NL (jamais le JSON brut) : fiche lisible avec liens markdown pour `explain`, chaîne de connexions pour `path`. Si le résultat est ambigu (plusieurs candidats), demander en NL lequel.

## Mémoire d'un repo code

`search`, `explain` et `path` acceptent `--project <repo>` à la place de `--scope` pour cibler la mémoire native d'un repo code (`~/.claude/projects/<slug>/memory/`) :

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/search_memories.py" "query" --project <repo>
python "${CLAUDE_PLUGIN_ROOT}/scripts/graph.py" explain "entité" --project <repo>
```

Résolution du chemin et contexte : `memoire-projet-code.md`. Résultat vide si le repo n'a pas encore de mémoire native.

## Comportement quand workspace non-driven

Si `/driven` est tapé dans un dossier sans CLAUDE.md `space-type` ancêtre :

> Ce dossier n'est pas un workspace driven (pas de CLAUDE.md avec space-type à la racine). Tu veux que je transforme ce dossier en workspace driven (création d'un CLAUDE.md racine avec space-type) ?

Si user dit oui : créer un CLAUDE.md minimal avec frontmatter `space-type: personal` ou `space-type: shared` au plus haut niveau pertinent. Si user dit non : abandon.

## Comportement quand argument ambigu

Si l'argument NL ne mappe clairement sur aucun cas de `routage.md`, demande NL :

> Tu veux que je note ça comme une décision ponctuelle, ou comme une règle qui s'applique partout ?

Pas de menu technique. Le user choisit en NL.

## Tab completion / argument-hint

Le frontmatter de `commands/driven.md` déclare :

```
argument-hint: "[intention en langage naturel] | [context | search | explain | path | audit | migrate | setup-doc]"
```

Le user voit cette hint en tapant `/driven`. Suggère les actions principales sans forcer.

## Pas d'options avancées V1

Pas de flags complexes en V1 (`--dry-run`, `--verbose`, `--scope=...`, etc.) sauf pour `/driven search` qui supporte `--scope` et `--top` pour usage power-user.

Le reste se gère en NL. Le plugin est conçu pour la simplicité d'usage, pas pour la richesse d'options.

## Récap au user

Chaque action `/driven` se termine par un recap minimal, 2 lignes max. Pas de description de la mécanique d'inférence ou de routage.
