# scope-check : Détection du workspace courant

Avant chaque write, vérifier le scope cible et appliquer les règles correspondantes. Sans cette vérification, une note privée peut atterrir dans un espace partagé et vice-versa.

## Détection du workspace driven

Algorithme de remontée d'arborescence depuis le cwd :

1. Lister le contenu du dossier courant.
2. Si `.driven` présent (fichier zéro octet, persistant) → c'est la racine du workspace.
3. Sinon, remonter au parent.
4. Répéter jusqu'à la racine système (`/`) ou jusqu'à trouver un `.driven`.
5. Si aucun `.driven` trouvé → workspace non-driven, plugin silencieux (comportement Claude standard).

Implémentation : `pathlib.Path(cwd).resolve()` puis boucle `.parent` jusqu'à `.parent == path` (racine).

## Distinction personal space ↔ shared space

Une fois la racine du workspace identifiée, classer par path :

| Type | Signal | Règles applicables |
|---|---|---|
| **personal space** | Path local hors Drive Desktop (ex `~/Personal OS/`, `~/Documents/perso/`) | RULE de factualité **désactivée**. Pas de tracking `authors`. Anti-fuite vers shared. |
| **shared space** | Path sous Drive Desktop (ex `~/Library/CloudStorage/GoogleDrive-*/`, `~/Google Drive/`, équivalent Windows/Linux) | RULE de factualité **active**. `authors` trackés par fichier. Cross-author détecté avant write. |

Vérifier la présence de `CloudStorage` ou `Google Drive` dans le path absolu pour détecter shared. En cas de doute (path symlink, mount custom) : lire `~/Library/Application Support/Google/DriveFS/...` pour la liste des dossiers syncés, ou demander à l'user en langage naturel.

## Cas multi-folder (Cowork ou multi-workspace)

Un user peut avoir plusieurs workspaces ouverts simultanément (personal + plusieurs shared spaces). Le plugin ne se fie pas à la racine de session, il vérifie le path du fichier cible **avant chaque write individuel** :

1. Path cible identifié (ex `~/Drive/Drivenlabs Team/Clients/Olenbee/notes.md`).
2. Remontée d'arborescence depuis ce path.
3. Premier `.driven` rencontré = workspace du fichier.
4. Règles appliquées selon perso/shared de ce workspace, pas de la session.

## Anti-fuite personal → shared

Si user demande une action qui pourrait écrire un contenu sensible dans le shared :

- Mention RH explicite, jugement sur une personne, NDA → propose perso (cf `references/memory.md` détection sensibles).
- Brouillon en cours, contenu non-factuel → propose perso ou reformulation factuelle.
- Donnée personnelle tierce → demande NL avant écriture.

Le mouvement perso → shared est **toujours conscient** : jamais une action automatique du plugin. Le mouvement shared → perso (extraire un brouillon personnel d'une mémoire collective) suit le même principe.

## Fallback hors workspace driven

Si Claude est invoqué dans un dossier sans `.driven` ancêtre :

- Le plugin reste silencieux. Pas de trigger, pas de check, pas de mention au user.
- Claude opère en mode standard (comportement par défaut hors plugin).
- Si user invoque explicitement `/driven` dans ce contexte → indiquer en NL que ce dossier n'est pas un workspace driven, proposer (optionnel) de transformer le dossier courant en workspace driven (création d'un `.driven` + d'un `CLAUDE.md` minimal).

## Récap minimal au user

Le scope-check est silencieux par construction. Pas de mention sauf erreur (ex : tentative d'écriture dans un workspace sans permission, marker corrompu). Si le scope est ambigu malgré l'algo, demander en NL :

> Le fichier que tu veux modifier vit dans le partagé Drivenlabs Team. Tu veux que je l'écrive là-bas ou tu préfères une note locale ?

Jamais de jargon (« perso », « shared », « scope »). Le user voit « le partagé Drivenlabs Team » et « une note locale ».
