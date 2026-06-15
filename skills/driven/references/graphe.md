# graphe : Index des relations du workspace

Le script `scripts/graph.py` recense les relations déjà écrites dans les fichiers du workspace (liens markdown, références `@`, frontmatter) et répond à une sous-commande. Il ne crée ni n'interprète rien : il indexe ce qui est inscrit. La source de vérité reste les `.md`.

**Optimisation, jamais point de défaillance.** Si le script échoue (Python absent, dépendance manquante), retomber silencieusement sur le comportement historique (grep pour la propagation, BM25 seul pour l'anti-récidive). Ne jamais exposer l'erreur au user.

Chaque invocation reconstruit le graphe avant de répondre — impossible de requêter un graphe périmé. Le cache `.claude/driven/graph.json` n'est qu'un artefact de relecture, jamais une source.

## Invocation

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/graph.py" <commande> [args] --scope "<racine workspace>"
```

`--scope` par défaut = cwd. Toujours passer la racine du workspace courant. Filtrer le préfixe stdout éventuel avant de parser le JSON.

Pour un projet code, `--project <repo>` remplace `--scope` et cible la mémoire native du repo (`memoire-projet-code.md`).

## Sous-commandes et quand les utiliser

| Situation | Commande | Lecture du résultat |
|---|---|---|
| Renommage / suppression d'un fichier ou dossier | `impact <path>` | `incoming` = qui pointe vers la cible. `at-ref` = chargement transitif (impact fort), `link` = lien simple. |
| Proposition stratégique sur une entité avec historique | `explain <entité>` | `linked_memories` triées par date = mémoires connexes à scruter pour l'anti-récidive. |
| Création d'une mémoire (auto cross-link) | `explain <entité>` | `incoming`/`outgoing` = candidats de liens markdown à insérer. |
| « explique-moi <entité> », « qu'est-ce qu'on sait sur X » | `explain <entité>` | Fiche + arêtes + mémoires. |
| « quel est le lien entre A et B » | `path <A> <B>` | `path` = chaîne de nœuds, `hops` = arêtes traversées. |
| Audit de cohérence, vérification des liens | `check` | `broken` = liens cassés (à corriger), `orphans` = fichiers sans entrée. |

## Résolution ambiguë

Si `explain` retourne `resolved: null` avec une liste `candidates`, ou si `path` retourne `ambiguous: true` avec `candidates_a` / `candidates_b`, le script n'a pas tranché. Choisir selon le contexte de la tâche, ou demander en NL au user (« Tu parles du contact Laurent ou de la note du RDV ? »). Ne jamais deviner en silence.

## Restitution NL

Jamais de JSON brut au user. Reformuler comme `interface-cli.md` le fait pour `search` : phrases naturelles, liens markdown vers les fichiers, deux lignes de recap. Exemple après un `impact` au renommage :

> OK, j'ai renommé Olenbee : 2 chargements obligatoires et 12 liens mis à jour.

## Garde-fou bivalence

Le script tourne en Python 3.10+ stdlib + PyYAML, identiquement en Claude Code et en sandbox Cowork. Pas de hook, pas de dépendance lourde : la bivalence est préservée (cf SKILL.md §10).
