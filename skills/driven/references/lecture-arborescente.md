# lecture-arborescente : Pattern de lecture pour exploration d'un dossier

Quand Claude entre dans un dossier (personal ou shared) ou commence à travailler sur un sujet, il a besoin de charger le contexte avant d'agir. Ce pattern documente l'ordre de lecture pour récupérer rapidement l'essentiel.

## Pourquoi ce pattern

En Claude Code, les `@imports` dans CLAUDE.md chargent automatiquement les fichiers liés. En Claude Cowork, les `@imports` ne sont **pas suivis**, c'est Claude qui doit orchestrer la lecture manuellement.

Le pattern documenté ici est utile partout, mais critique en Cowork pour reproduire la cascade automatique du Code.

## Ordre de lecture

Pour explorer un dossier nouveau ou commencer une tâche sur un sujet :

1. **`CLAUDE.md` du dossier courant**, vue stratégique, structure, conventions.
2. **`CONTRIBUTING.md` du dossier si présent**, workflows et règles locales.
3. **5 dernières memory entries du `memory/` local**, contexte récent.
4. **Fichiers thématiques pertinents** (si tâche le justifie), positioning, brief, etc.
5. **Sous-dossiers concernés**, `Clients/Olenbee/` si on bosse sur Olenbee.

Le tri lexicographique des memory entries (naming `YYYY-MM-DD-HHMM-...`) = tri chronologique. Les 5 plus récentes par ordre alphabétique inversé.

## Quand appliquer ce pattern

| Trigger | Action |
|---|---|
| User demande une action sur un dossier rarement visité | Lecture arborescente complète avant d'agir |
| User mentionne un client / projet / thème spécifique | Lecture arborescente du dossier correspondant |
| Début de session sans contexte explicite | Lecture du CLAUDE.md racine + dernières mémoires globales |
| User référence une décision passée (« on avait dit que ») | Lecture des memory entries du dossier concerné |

## Pas systématique

La lecture arborescente n'est pas un rituel imposé à chaque message. Elle se déclenche quand le contexte mérite chargement. Pour des actions simples dans un contexte déjà chargé (édition d'un fichier juste lu, suite d'une conversation en cours), pas de re-chargement.

## Cascade vers les memory entries

Pour les 5 dernières memory entries du dossier :

1. Lister les fichiers `.md` dans `memory/` du dossier courant.
2. Trier par nom (= tri chrono inversé).
3. Lire les 5 plus récents, préambule `## Contexte` suffit en général. Le corps `## Notes` se lit si la mémoire est directement pertinente.

Si le dossier a beaucoup de memory entries et que la tâche est ciblée (ex « cherche les mémoires sur le pricing »), invoquer le script `scripts/search_memories.py` (BM25) plutôt que lire les dernières chronologiques. Détail : `references/interface-cli.md` + `scripts/search_memories.py`.

## Cascade vers la mémoire native d'un repo associé

Quand le CLAUDE.md ou le doc d'un projet porte un champ `code-repo` (`frontmatter.md`), lire aussi la mémoire native de ce repo : le contexte technique rejoint le contexte business. Résolution du dossier et lecture : `memoire-projet-code.md`.

## Cascade vers les fichiers normatifs racine

Quand on travaille dans un sous-dossier d'un shared, on suit la chaîne :

1. CLAUDE.md du sous-dossier.
2. Si CLAUDE.md pointe vers le CLAUDE.md racine → le lire.
3. CLAUDE.md racine + ABOUT.md / RULES.md / CONTRIBUTING.md de la racine si présents et pertinents.

Le plugin ne charge pas tout par défaut. Lecture **à la demande** selon la pertinence pour la tâche.

## Différence avec `comprehension-contextuelle.md`

`lecture-arborescente.md` = pattern d'**exploration** (charge le contexte d'un dossier).

`comprehension-contextuelle.md` = pattern de **pré-trigger** (charge le contexte pertinent avant une action spécifique, ex chercher les mémoires sur un sujet).

Les deux peuvent s'enchaîner : exploration arborescente d'abord, puis compréhension contextuelle pour une tâche précise.

## Cowork : Project Instructions standardisées

En Cowork, les Project Instructions du Project Cowork de l'user disent typiquement :

> Au démarrage de chaque session, lis le `CLAUDE.md` à la racine du workspace ouvert dans ce Project.

Le plugin `driven` complète cette amorce avec la lecture arborescente quand la tâche le justifie. Détail Cowork : Spec 5.

## Multi-folder Cowork

Quand un Cowork Project a plusieurs dossiers (personal space + N shared spaces), Claude doit déterminer quel workspace est concerné par la tâche courante :

1. User mentionne un path explicite → lire le CLAUDE.md de ce workspace.
2. User mentionne un sujet associé à un workspace connu (Drivenlabs Team → shared, journal perso → personal) → lire le CLAUDE.md de ce workspace.
3. Ambigu → demande NL : *« Tu parles du partagé Drivenlabs ou de tes notes dans l'espace perso ? »*

Pas de logique automatique sur le « workspace courant ». Chaque action vérifie son scope (cf `references/scope-check.md`).

## Récap au user

La lecture arborescente est silencieuse par construction. Pas de mention au user *« je lis le CLAUDE.md »*. Le user voit le résultat, Claude qui répond avec le contexte chargé.

Si user demande explicitement *« regarde dans le dossier Olenbee »*, alors mention en NL :

> J'ai lu les conventions et les dernières mémoires d'Olenbee. Voilà ce que je vois...

Sinon, silence. La machinerie de lecture ne se commente pas.
