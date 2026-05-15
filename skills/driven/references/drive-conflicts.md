# drive-conflicts : Détection et résolution des conflits Drive Desktop

## Doctrine

Quand 2 members écrivent simultanément sur le même fichier d'un Shared Drive Google, Drive Desktop génère un fichier en double type `notes (1).md`. Sans gestion explicite, le plugin peut :
- **Ignorer** les doublons → perte silencieuse de contenu
- **Les lire comme 2 fichiers indépendants** → confusion sur la source de vérité

Cette ref encode un comportement de détection + résolution proposée en langage naturel.

## Quand cette ref s'active

Support automatique du plugin (niveau workspace driven). Trigger : Claude détecte un fichier avec pattern `*(<n>).md` (où `<n>` est un entier) proche d'un fichier sans numéro, dans un workspace sous Drive Desktop.

## Pré-conditions

- Workspace driven (signaux `space-type`, `authors:`, ou path Drive Desktop)
- Path racine sous Drive Desktop (`~/Library/CloudStorage/GoogleDrive-*` sur macOS, équivalent Windows/Linux)
- Présence d'un fichier `<name> (<n>).md` ET d'un fichier `<name>.md` dans le même dossier

## Algorithme de détection

1. À chaque action de lecture/écriture dans un workspace driven, scanner le dossier cible pour des fichiers avec pattern `*(<n>).md`.
2. Pour chaque match, vérifier l'existence du fichier sans numéro (`<name>.md`).
3. Si les deux existent → conflit Drive détecté.
4. Vérifier les `last-updated` ou `mtime` pour identifier le plus récent.

## Workflow de résolution

1. **Alerte NL au user** : *« Il y a un conflit Drive sur `<fichier>`. [member A] et [member B] ont écrit en simultané. Comment on résout ? »*

2. **AskUserQuestion avec 3 options** :
   - **Fusion** : Claude lit les 2 versions, propose un merge en NL au user pour validation
   - **Récent gagne** : on garde le plus récent (mtime), l'ancien est archivé dans `_archive/<date>-<name>.md`
   - **L'user choisit** : Claude montre les 2 versions side-by-side, l'user décide laquelle garder

3. **Exécution** selon choix.

4. **Recap au user** : *« OK, j'ai gardé la version de [member]. L'autre est dans `_archive/`. »* (ou recap adapté au choix)

## Cas particuliers

### Conflit multi-versions

Si plusieurs `*(1).md`, `*(2).md`, etc. existent, Claude liste tous les conflits et propose la résolution un par un.

### Conflit sur fichier normatif racine (CLAUDE.md, RULES.md, etc.)

Criticité élevée. Claude refuse la résolution automatique sans validation explicite renforcée :

> *« Conflit sur un fichier de règle. Ce sont des choix structurants. Tu veux qu'on regarde les 2 versions ensemble avant de décider ? »*

### Conflit récurrent sur le même fichier

Si Claude voit que le même fichier génère des conflits Drive régulièrement (3+ fois), il propose en NL :

> *« Ce fichier semble écrit souvent en simultané. Vous voulez qu'on convienne d'un workflow (un member le maintient, ou on le split en 2 ?) »*

## Anti-patterns

- **Résolution silencieuse** : jamais. Toute résolution passe par validation user.
- **Suppression du fichier sans numéro** : jamais. Le fichier sans numéro est généralement le « principal », l'autre est la copie générée par Drive.
- **Archivage par défaut sans options** : pas de choix forcé. L'user choisit.

## Interactions

| Composant | Comment drive-conflicts interagit |
|---|---|
| `scope-check.md` | Détecte le path Drive Desktop, condition d'activation de cette ref |
| `memory.md` | Si le conflit concerne une mémoire, Claude peut proposer de créer 2 mémoires distinctes plutôt que de fusionner (append-only) |
| `maintenance-fichiers-racines.md` | Si le conflit concerne un fichier normatif, alerte renforcée |

## Recap user après résolution

Selon le choix :

- Fusion : *« OK, j'ai fusionné les 2 versions, voilà ce qu'on garde. »*
- Récent : *« OK, j'ai gardé la version de [member, date]. L'autre est dans `_archive/`. »*
- Choix manuel : *« OK, j'ai gardé celle que tu m'as indiquée. »*

Pas de jargon Drive Desktop. Le user voit le résultat.
