# Spec — Index de graphe structurel pour driven

**Date** : 2026-06-11
**Statut** : design validé, prêt pour plan d'implémentation
**Version cible** : driven v1.9.0

## Problème

Driven maintient un workspace collaboratif qui ne fait que grossir : les mémoires sont append-only, les fichiers et liens s'accumulent. Plusieurs comportements du plugin reposent aujourd'hui sur un scan au moment T :

- **Propagation** (`propagation.md`) : au renommage ou à la suppression d'un fichier, le plugin fait un `grep` du chemin littéral dans tout le workspace pour trouver les liens entrants. Faillible (faux positifs/négatifs sur les sous-chaînes), lent à mesure que l'espace grossit, et incapable de distinguer un lien markdown d'une référence `@` à chargement transitif.
- **Anti-récidive** (`challenge-anti-recidive.md`) : avant une proposition stratégique, le plugin consulte les Lessons + un BM25 top 5. Il rate les mémoires connexes qui ne partagent pas les mots-clés de la requête mais sont liées par référence directe.
- **Auto cross-link** (`memory.md`) : à la création d'une mémoire, le plugin « scanne le voisinage » du dossier courant pour proposer des liens. Le voisinage se limite au dossier, pas aux relations réelles.

Le risque de fond est le « système menteur » du Principe 3 (RULES.md du Personal OS) : un lien cassé ou une cascade ratée ne se voit que le jour où on tombe dessus. Un workspace driven vendu comme tenant dans le temps doit avoir une garantie structurelle contre ce pourrissement silencieux.

## Objectif

Indexer les **relations déjà écrites** dans le workspace dans un format requêtable, et brancher cet index sur les flux existants de driven. L'index ne crée rien et n'interprète rien : il recense ce qui est inscrit dans les fichiers (liens, références `@`, frontmatter). La source de vérité reste les `.md`.

Principe directeur : **optimisation, jamais point de défaillance**. Si l'index échoue, driven retombe sur ses comportements actuels (grep, BM25) sans bloquer ni exposer l'erreur. Strictement déterministe : zéro appel LLM, zéro extraction d'entités depuis le texte libre.

## Périmètre

### Dans le périmètre (V1)

1. **Socle** : `scripts/graph.py`, script unique à sous-commandes, qui construit le graphe et répond.
2. **Blast radius** : sous-commande `impact` branchée sur `propagation.md`.
3. **Requêtes de graphe** : sous-commandes `explain` et `path`, exposées via `/driven explain` / `/driven path` + routage NL.
4. **Confidence tagging** : champ `confidence` dans le frontmatter des mémoires, exploité par l'anti-récidive.
5. **Détection** : sous-commande `check` (liens cassés, orphelins).

### Hors périmètre (V1, explicite)

- Carte de l'espace / rapport d'audit structurel régénérable (non retenu).
- Staleness automatique (alerte de fraîcheur proactive).
- Cache cross-session avec logique d'invalidation par mtime.
- Extraction d'entités depuis le texte libre (interprétatif — interdit par principe).
- Visualisation (HTML, graphe interactif).
- Hooks (briserait la bivalence Code/Cowork — cf SKILL.md §10).

## Architecture

### Script unique à sous-commandes

`scripts/graph.py`, à côté de `scripts/search_memories.py`, mêmes conventions (PyYAML, sortie JSON sur stdout, erreurs sur stderr, flag `--scope`). Chaque invocation **reconstruit le graphe en interne** avant de répondre : impossible de requêter un graphe périmé.

Dépendance unique : **PyYAML** (déjà requise par `search_memories.py`). Pas de `rank-bm25`. Python 3.10+ stdlib pour le reste, afin de rester compatible avec la sandbox Cowork (Ubuntu 22.04).

### Cache

Le graphe est écrit à `<racine-workspace>/.claude/driven/graph.json`. Ce cache ne sert que d'artefact de relecture dans la même session ; aucune sous-commande ne s'y fie comme source — toutes reconstruisent avant de répondre. Emplacement choisi : `.claude/` est déjà un dossier technique conventionnel, non synchronisé comme contenu de travail, et hors de la vue du user. Pas de logique d'invalidation à maintenir (le rebuild systématique la rend inutile).

La racine du workspace est déterminée par remontée d'arborescence depuis `--scope` jusqu'au CLAUDE.md portant `space-type` (même algorithme que `scope-check.md`). Si aucune racine n'est trouvée, le cache n'est pas écrit (le script répond quand même depuis le graphe en mémoire).

## Modèle de données

### Nœuds

Un nœud par fichier `.md` du workspace. Exclus du parcours : `.claude/`, `.tmp/`, tout dossier `_legacy/`.

Attributs d'un nœud :

| Attribut | Source | Notes |
|---|---|---|
| `path` | chemin relatif à la racine du workspace | identifiant du nœud |
| `kind` | inféré | `memory` (dans un `memory/` avec frontmatter `date`), `normative` (nom en MAJUSCULES : CLAUDE/RULES/SOUL/ME/ABOUT/CONTRIBUTING/VOICE), `content` sinon |
| `frontmatter` | YAML parsé | date, authors, type, topic, keywords, last-updated, confidence |
| `title` | premier H1 du corps | pour la résolution par nom dans `explain` |

### Arêtes typées

Par ordre de force décroissante :

| Type | Source | Force | Notes |
|---|---|---|---|
| `at-ref` | référence `@fichier` dans le corps ou le frontmatter | forte | chargement transitif — un `at-ref` cassé est plus grave qu'un lien cassé |
| `link` | lien markdown `[texte](path.md)` | moyenne | résolu d'abord relatif au fichier source, puis relatif à la racine en fallback (les deux conventions coexistent dans `links.md`) |
| `affinity` | topic identique OU ≥ 2 keywords communs entre deux mémoires | faible | calculée, jamais inscrite dans un fichier ; relie des mémoires d'un même sujet |

Une arête `at-ref` ou `link` vers une cible inexistante **ne crée pas d'arête** : elle alimente la liste `broken` (sert à `check` et détecte les stubs interdits par `links.md`).

Les arêtes `link` et `at-ref` portent le **numéro de ligne** de la source, pour des recaps précis (« lien en ligne 42 »).

## Sous-commandes

| Commande | Entrée | Sortie JSON |
|---|---|---|
| `build` | `--scope` | Stats : nombre de nœuds par `kind`, nombre d'arêtes par type, liste `broken`. Écrit le cache. |
| `impact <path>` | fichier ou dossier | Liens entrants typés, triés (`at-ref` d'abord, puis `link`), chacun avec fichier source + ligne. C'est le blast radius. Pour un dossier : agrège l'impact de tous ses fichiers. |
| `explain <nom\|path>` | nom d'entité ou chemin | Résolution du nœud (match sur basename, H1, ou topic), puis : attributs du nœud, arêtes entrantes et sortantes (tous types), mémoires liées (`affinity` + `link`) triées par date décroissante. |
| `path <A> <B>` | deux nœuds (nom ou path) | Plus court chemin entre A et B (BFS sur le graphe non orienté), avec la séquence d'arêtes traversées et leur type. « non connectés » si aucun chemin. |
| `check` | `--scope` | Liens cassés (cible inexistante, avec source + ligne) + fichiers orphelins (aucune arête entrante, hors fichiers racine attendus comme CLAUDE.md). |

### Résolution de nom ambiguë

Si `explain olenbee` ou `path A B` matche plusieurs nœuds (ex. un dossier `Clients/Olenbee/` et une fiche), le script retourne la **liste des candidats** avec leur path et kind. Il ne devine jamais. Claude tranche selon le contexte ou demande en NL au user.

## Branchements dans les références existantes

### `propagation.md`

Le scan `grep` du chemin littéral (renommage, suppression) est remplacé par `impact <path>`. Les seuils existants restent inchangés :

- ≤ 50 liens entrants : cascade silencieuse, recap minimal.
- > 50 liens : validation NL avant exécution.

Nouveauté dans le recap : distinction des types. Au lieu de « j'ai mis à jour les 14 liens », le plugin sait dire « 2 chargements obligatoires (`@`) et 12 liens mis à jour » — et alerte plus fortement si un `at-ref` est touché (impact transitif).

### `challenge-anti-recidive.md`

La cascade de consultation gagne une troisième source, après les Lessons et le BM25 top 5 :

- **Mémoires liées par arête** au sujet de la proposition, obtenues via `explain` sur l'entité concernée.

La limite anti-cascade-infinie reste (5 mémoires max au total, toutes sources confondues). Le confidence tagging pondère : un signal de rejet dans une mémoire `verbatim` bloque ; un signal dans une mémoire `inferred` se mentionne avec réserve (« il me semble que tu avais écarté ça, à confirmer »).

### `memory.md`

L'auto cross-link (étape « scan du voisinage », §Auto cross-link) utilise `explain` sur les entités mentionnées dans la nouvelle mémoire pour proposer les liens markdown pertinents, au lieu du scan limité au dossier courant. Le reste du workflow de création est inchangé.

### `interface-cli.md`

Documenter `/driven explain <entité>` et `/driven path <A> <B>` à côté de `/driven search`, dans la section « nom d'action explicite ». Mapping vers l'invocation du script. **Pas de mention dans le menu sans argument** (`/driven` seul) — l'invisibilité prime, ces verbes sont pour le power-user.

### Nouvelle référence `references/graphe.md`

Documente : quand invoquer `graph.py`, quelle sous-commande pour quelle situation, format de restitution NL des résultats (jamais de JSON brut au user — toujours reformulé en langage naturel comme `interface-cli.md` le fait pour `search`). Référencée au §12 du SKILL.md, avec signal d'activation ajouté au §6.2 (modification structurelle / renommage / suppression / proposition stratégique).

### `frontmatter.md` — confidence tagging

Évolution officielle du format des memory entries : ajout d'un champ optionnel.

```yaml
confidence: verbatim | inferred | mixed
```

- `verbatim` : reformulation factuelle de ce que l'user a effectivement dit ou décidé.
- `inferred` : déduction de Claude à partir du contexte, non énoncée explicitement par l'user.
- `mixed` : la mémoire contient les deux.

Inféré silencieusement par Claude à la création, jamais demandé au user, jamais inscrit dans le corps (compatible clean slate strict de `factualite.md` et invisibilité du SKILL.md §1). Les mémoires existantes sans le champ sont traitées comme `verbatim` par défaut — pas de migration rétroactive.

## Gestion d'erreurs et dégradation

| Situation | Comportement |
|---|---|
| Python absent / PyYAML manquant | driven retombe sur grep + BM25, sans exposer l'erreur au user |
| Frontmatter corrompu sur un fichier | nœud créé avec les attributs disponibles, fichier signalé dans les stats de `build` |
| Workspace vide / scope inexistant | sortie JSON vide valide, pas d'erreur |
| Racine de workspace introuvable | graphe construit en mémoire, cache non écrit |
| Lien ambigu à résoudre | candidats retournés, jamais de devinette |

Le script ne lève jamais d'exception non gérée vers l'appelant : toute erreur attendue produit une sortie JSON exploitable ou un message stderr clair. Claude lit le code de sortie et le JSON, et décide de la dégradation.

## Tests

Suite `pytest` dans `tests/` du repo. Workspace fixture synthétique : versions miniatures d'un espace perso et d'un espace shared, contenant mémoires avec frontmatter complet, liens markdown valides, références `@`, liens cassés (stubs), fichiers orphelins, mémoires partageant topic et keywords.

Couverture :

- Un test par sous-commande (`build`, `impact`, `explain`, `path`, `check`).
- Cas limites : lien relatif au fichier vs relatif à la racine ; cible ambiguë (candidats multiples) ; frontmatter corrompu ; workspace vide ; scope inexistant ; `path` entre nœuds non connectés ; arête `affinity` déclenchée par topic identique seul, et séparément par ≥ 2 keywords communs seuls (les deux conditions sont alternatives, cf modèle de données).
- Dégradation : comportement sur fichier `.md` sans frontmatter.

Contrainte d'exécution : Python 3.10+ stdlib + PyYAML uniquement, pour garantir l'exécution en sandbox Cowork.

## Versions et fichiers touchés

Bump driven v1.8.1 → v1.9.0 (nouvelle capacité). Fichiers :

- **Nouveau** : `scripts/graph.py`
- **Nouveau** : `skills/driven/references/graphe.md`
- **Nouveau** : `tests/` (fixture + tests pytest)
- **Modifié** : `skills/driven/SKILL.md` (§6.2 signal, §12 référence graphe)
- **Modifié** : `skills/driven/references/propagation.md` (impact remplace grep)
- **Modifié** : `skills/driven/references/challenge-anti-recidive.md` (3ᵉ source)
- **Modifié** : `skills/driven/references/memory.md` (auto cross-link via explain)
- **Modifié** : `skills/driven/references/interface-cli.md` (verbes explain/path)
- **Modifié** : `skills/driven/references/frontmatter.md` (champ confidence)
- **Modifié** : `.claude-plugin/plugin.json` (version)
