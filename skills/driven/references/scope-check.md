# scope-check : Observation des signaux du workspace

Avant chaque write, observer les signaux disponibles dans l'environnement et adapter les comportements en conséquence. Pas de rigidité sur un type d'espace figé.

## Doctrine d'optionnalité

Le plugin **observe** les signaux disponibles et adapte ses comportements **sans rigidité**. Pas de message « pas de space-type trouvé » ni de comportement bloquant. Les comportements émergent des signaux, pas d'une déclaration figée.

## Signaux observés

À chaque action dans un dossier, Claude vérifie les signaux suivants et active les comportements correspondants :

| Signal | Détection | Comportements activés |
|---|---|---|
| Frontmatter `space-type: personal` du CLAUDE.md racine (remonté) | Lecture du frontmatter YAML | Hint perso, pas de tracking authors par défaut |
| Frontmatter `space-type: shared` du CLAUDE.md racine | Idem | Hint shared, RULE factualité activée |
| Fichiers portent `authors:` au frontmatter | Scan des fichiers du dossier | Cross-author détecté avant write, ajout authors aux nouveaux fichiers |
| CLAUDE.md racine porte `members:` | Lecture frontmatter | Résolution email → nom (cross-author flow complet) |
| Path sous Drive Desktop (`CloudStorage`, `Google Drive`) | Inspection du path absolu | Support `drive-conflicts.md` actif |
| Fichiers présents `<name> (<n>).md` | Scan du dossier | Conflit Drive détecté (cf `drive-conflicts.md`) |
| CLAUDE.md du dossier contient section « Lessons » | Lecture du fichier | Lessons consultées avant proposition stratégique (cf `challenge-anti-recidive.md`) |

## Algorithme de remontée

Pour identifier le workspace driven racine (si présent) :

1. Depuis le dossier courant (cwd), remonter parent par parent.
2. À chaque niveau, vérifier l'existence d'un `CLAUDE.md` et parser son frontmatter YAML.
3. Si un `CLAUDE.md` porte le champ `space-type` (`personal` ou `shared`) → c'est la racine du workspace driven. **Hint** : applique le profil correspondant directement.
4. Sinon, continuer la remontée. Si aucun match → workspace non-driven, comportements de base (niveau universel) actifs.

Le `space-type` reste un **hint utile** mais pas une condition obligatoire. En absence, le plugin observe les autres signaux et adapte.

## Distinction personal ↔ shared (sans `space-type`)

Si le frontmatter `space-type` n'est pas présent mais d'autres signaux suggèrent un type :

| Indicateurs shared | Indicateurs perso |
|---|---|
| Path sous Drive Desktop | Path local hors Drive Desktop |
| Fichiers portent `authors:` | Pas de `authors:` |
| Présence de `members:` quelque part | Pas de `members:` |
| Multiple users observés via authors | Un seul user |

Claude infère le type le plus probable et adapte. Pas de message d'erreur si l'inférence est incertaine — comportement réduit à ce qui fait sens.

## Cas multi-folder (Cowork ou multi-workspace)

Un user peut avoir plusieurs workspaces ouverts simultanément. Le plugin vérifie le path du fichier cible **avant chaque write individuel** :

1. Path cible identifié.
2. Remontée d'arborescence depuis ce path.
3. Premier `CLAUDE.md` avec signaux pertinents = workspace du fichier.
4. Règles appliquées selon signaux observés.

## Anti-fuite personal → shared

Si user demande une action qui pourrait écrire un contenu sensible dans un dossier shared (signaux observés) :

- Mention RH explicite, jugement, NDA → cf `memory.md` détection sensibles
- Brouillon non-factuel → propose perso ou reformulation factuelle
- Donnée personnelle tierce → demande NL avant écriture

Le mouvement perso → shared est **toujours conscient**. Jamais une action automatique du plugin.

## Fallback hors workspace driven

Si Claude est invoqué dans un dossier sans signaux driven (pas de `CLAUDE.md` avec `space-type`, pas d'`authors:`, pas sous Drive Desktop) :

- Comportements de base (niveau universel) actifs : patterns proactifs setup-dossier, capitalise-workflow, doctrine AskUserQuestion
- Pas de routage connaissance vs mémoire, pas de RULE factualité, pas d'ajout authors
- Si user invoque `/driven` explicitement → propose la création d'un CLAUDE.md racine avec `space-type` au niveau pertinent (optionnel)

## Récap minimal au user

Le scope-check est silencieux par construction. Pas de mention sauf erreur (ex : tentative d'écriture dans un workspace sans permission, ambiguïté de path).

Jamais de jargon (« perso », « shared », « space-type ») envers user. Si scope ambigu malgré l'observation, demande NL :

> Le fichier que tu veux modifier vit dans le partagé Drivenlabs Team. Tu veux que je l'écrive là-bas ou tu préfères une note locale ?
