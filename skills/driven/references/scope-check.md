# scope-check : Détection du workspace courant

Avant chaque write, vérifier le scope cible et appliquer les règles correspondantes. Sans cette vérification, une note privée peut atterrir dans un espace partagé et vice-versa.

## Détection du workspace driven

Algorithme de remontée d'arborescence depuis le cwd :

1. Lister le contenu du dossier courant.
2. Si un `CLAUDE.md` est présent et contient un frontmatter YAML avec le champ `space-type` (valeur `personal` ou `shared`) → c'est la racine du workspace driven.
3. Sinon, remonter au parent.
4. Répéter jusqu'à la racine système (`/`) ou jusqu'à trouver un tel `CLAUDE.md`.
5. Si aucun `CLAUDE.md` avec `space-type` n'est trouvé → workspace non-driven. Seul le niveau universel s'applique (patterns proactifs A et B, doctrine AskUserQuestion).

Implémentation : `pathlib.Path(cwd).resolve()` puis boucle `.parent`. À chaque niveau, vérifier la présence d'un `CLAUDE.md`, lire ses premières lignes pour parser le frontmatter YAML, et chercher le champ `space-type`.

## Distinction personal space ↔ shared space

Une fois la racine identifiée, lire la valeur du champ `space-type` :

| Valeur | Type | Règles applicables |
|---|---|---|
| `personal` | personal space | RULE de factualité **désactivée**. Pas de tracking `authors`. Anti-fuite vers shared. |
| `shared` | shared space | RULE de factualité **active**. `authors` trackés par fichier. Cross-author détecté avant write. |

## Cas multi-folder (Cowork ou multi-workspace)

Un user peut avoir plusieurs workspaces ouverts simultanément (personal + plusieurs shared spaces). Le plugin ne se fie pas à la racine de session, il vérifie le path du fichier cible **avant chaque write individuel** :

1. Path cible identifié (ex `~/Drive/Drivenlabs Team/Clients/Olenbee/notes.md`).
2. Remontée d'arborescence depuis ce path.
3. Premier `CLAUDE.md` avec `space-type` rencontré = workspace du fichier.
4. Règles appliquées selon `space-type` de ce workspace, pas de la session.

## Anti-fuite personal → shared

Si user demande une action qui pourrait écrire un contenu sensible dans le shared :

- Mention RH explicite, jugement sur une personne, NDA → propose perso (cf `references/memory.md` détection sensibles).
- Brouillon en cours, contenu non-factuel → propose perso ou reformulation factuelle.
- Donnée personnelle tierce → demande NL avant écriture.

Le mouvement perso → shared est **toujours conscient** : jamais une action automatique du plugin. Le mouvement shared → perso (extraire un brouillon personnel d'une mémoire collective) suit le même principe.

## Fallback hors workspace driven

Si Claude est invoqué dans un dossier sans `CLAUDE.md` `space-type` ancêtre :

- Niveau 1 universel actif : patterns A (setup-dossier), B (capitalise-workflow), doctrine AskUserQuestion.
- Niveaux 2 et 3 inactifs : pas de routage connaissance vs mémoire, pas de RULE de factualité, pas d'ajout `authors`.
- Si user invoque explicitement `/driven` dans ce contexte → proposer la création d'un `CLAUDE.md` racine avec frontmatter `space-type` au plus haut niveau pertinent, pour activer les comportements workspace.

## Récap minimal au user

Le scope-check est silencieux par construction. Pas de mention sauf erreur (tentative d'écriture dans un workspace sans permission, ambiguïté de path). Si le scope est ambigu malgré l'algorithme, demander en NL :

> Le fichier que tu veux modifier vit dans le partagé Drivenlabs Team. Tu veux que je l'écrive là-bas ou tu préfères une note locale ?

Jamais de jargon (« perso », « shared », « space-type »). Le user voit « le partagé Drivenlabs Team » et « une note locale ».
