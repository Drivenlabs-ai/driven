# gestion-contexte : Mécanique réelle de chargement et arbitrages d'économie

La fenêtre de contexte est la ressource la plus précieuse d'une session. Chaque arbitrage de structure (découpage, `@` vs lien, extraction vers skill, placement d'une règle) doit se prendre en connaissance de la mécanique réelle de chargement — pas à l'intuition. Cette ref la documente et en tire les règles de décision.

Mécanique vérifiée sur la doc officielle Claude Code (code.claude.com/docs, juin 2026). Les comportements décrits sont ceux de Claude Code ; les écarts Cowork sont signalés en fin de ref.

## 1. Ce qui charge, et quand

| Mécanisme | Quand ça charge | Coût |
|---|---|---|
| CLAUDE.md ancêtres du cwd (+ `CLAUDE.local.md`) | Au démarrage, **en entier**, concaténés | À chaque tour, toute la session |
| Imports `@fichier` (récursif, max 4 niveaux) | Au démarrage, expansés avec leur parent | Identique à du contenu inline |
| CLAUDE.md d'un **sous-dossier** sous le cwd | À la première lecture d'un fichier de ce sous-dossier (lazy) | Zéro tant qu'on n'y travaille pas |
| Règles `.claude/rules/*.md` sans frontmatter `paths:` | Au démarrage | À chaque tour |
| Règles `.claude/rules/*.md` **avec `paths:`** (globs) | À la lecture d'un fichier qui matche le pattern | Zéro hors du périmètre |
| Descriptions de skills | Au démarrage, budget global = 1 % de la fenêtre | Permanent ; au-delà du budget, les moins utilisés sont réduits au nom seul |
| Corps d'un skill invoqué | À l'invocation, **reste en contexte toute la session** | Récurrent après invocation |
| `references/` d'un skill | Au Read explicite seulement | Ponctuel |
| Subagent | Fenêtre séparée ; seul le résumé final revient | Isolé du contexte principal |
| Hooks | Jamais (code externe), sauf output retourné | Zéro par défaut |
| CLAUDE.md des répertoires `additionalDirectories` / `--add-dir` | **Jamais par défaut** | — |

Conséquence centrale : **tout ce qui est au niveau racine ou `@`-importé est payé à chaque tour, que la tâche en ait besoin ou non**. L'économie de contexte ne se joue pas dans la rédaction, elle se joue dans le placement.

## 2. Le coût réel du `@` — complément à la doctrine §2ter

Un `@fichier` ne fait **aucune** économie par rapport au contenu inline : il est expansé au démarrage et pèse pareil. Splitter un gros fichier en imports `@` améliore l'organisation et la maintenance, pas le contexte.

Les deux seuls leviers d'économie réels :

- **Lien markdown / référence textuelle** → lu à la demande, selon le besoin de la tâche.
- **Skill** → description seule en permanence (~100 tokens), corps à l'invocation.

L'heuristique `@` vs lien de la doctrine de référencement (§2ter du SKILL.md) reste la grille de décision ; cette mécanique en est le fondement chiffré.

## 3. Cibles de taille (recommandations officielles)

| Fichier | Cible | Au-delà |
|---|---|---|
| CLAUDE.md (chaque niveau) | **< 200 lignes** | Charge quand même en entier, mais l'adhérence aux instructions baisse |
| Corps de SKILL.md | < 500 lignes / < 5 000 tokens | Déporter le détail en `references/` |
| Description de skill | Cas d'usage clé en premier ; cap dur 1 536 caractères | Tronquée dans le listing |
| Fichier `references/` > 100 lignes | Table des matières en tête | — |

Quand un fichier normatif dépasse sa cible, c'est un signal d'extraction (workflow : `decoupage-progressif.md`) — en privilégiant les cibles qui sortent du chargement permanent : skill pour une procédure répétable, CLAUDE.md de sous-dossier pour une convention de domaine, lien textuel pour un référentiel volumineux.

## 4. Compaction : ce qui survit, ce qui se perd

Quand la fenêtre approche la saturation (~95 %), Claude Code purge d'abord les vieux résultats d'outils, puis résume la conversation. Après compaction :

| Contenu | Sort |
|---|---|
| CLAUDE.md racine, règles non scopées, mémoire auto | **Ré-injectés depuis le disque** |
| CLAUDE.md de sous-dossiers, règles `paths:` | **Perdus** jusqu'à relecture d'un fichier du périmètre |
| Corps des skills invoqués | Ré-injectés tronqués : 5 000 tokens max par skill, 25 000 au total, les plus anciens éjectés d'abord ; la troncature **garde le début** du fichier |

Règles d'écriture qui en découlent :

- **Une règle vitale pour toute la session vit au niveau racine**, jamais uniquement dans un sous-dossier ou une règle scopée — sinon elle peut disparaître en cours de session longue.
- **Dans un SKILL.md, les instructions critiques vont en haut** : c'est ce que la troncature préserve.
- Un CLAUDE.md peut porter une section d'instructions de compaction (ce que le résumé doit impérativement préserver : décisions en cours, chemins des fichiers ouverts). À proposer pour les workspaces à sessions longues.
- Un édit de fichier normatif en cours de session ne prend effet qu'à la prochaine session (ou compaction) : la session courante continue sur la version chargée au démarrage. Le signaler au user quand il s'attend à un effet immédiat.

## 5. Arbitrage de placement — table de décision

Avant d'écrire ou de déplacer une information normative, choisir le mécanisme par nature de l'info :

| Nature de l'info | Mécanisme | Pourquoi |
|---|---|---|
| Doctrine universelle, nécessaire à chaque session | Fichier racine ou `@`-import | Le coût permanent est justifié |
| Convention propre à un domaine / dossier | CLAUDE.md du sous-dossier | Lazy : payée seulement en y travaillant |
| Règle qui ne vaut que pour certains fichiers (extensions, chemins) | `.claude/rules/<règle>.md` avec `paths:` | Conditionnelle par chemin, zéro coût hors périmètre |
| Procédure répétable, workflow outillé | Skill | ~100 tokens en permanence, le reste à l'invocation |
| Référentiel volumineux, consultation occasionnelle | Fichier dédié + lien textuel | Lu à la demande |
| Pré-traitement mécanique (filtrer un log, valider un format) | Hook ou script | Zéro contexte, seul le résultat utile entre |

Anti-pattern : promouvoir une info au niveau racine « pour être sûr que Claude la voie ». Chaque promotion injustifiée dégrade l'attention portée à tout le reste. Le test : *est-ce qu'une session qui ne touche pas à ce sujet a besoin de cette ligne ?* Non → niveau plus profond ou chargement à la demande.

## 6. Travail verbeux : isoler plutôt que subir

Les opérations à gros volume de sortie (exploration large, scraping, gros logs, suites de tests) se délèguent à un subagent : il consomme sa propre fenêtre et ne rend qu'un résumé. La conversation principale reste pour les décisions, les aller-retours et le travail qui partage du contexte.

En session : une question annexe se traite hors historique quand l'outil le permet (`/btw` en Claude Code) plutôt qu'en polluant le fil.

## 7. Hygiène de session — articulation avec session-handoff

La doctrine officielle rejoint le signal de saturation de `session-handoff.md` : une session propre avec un meilleur prompt bat presque toujours une session longue chargée de corrections accumulées. Repères :

- Plus de deux corrections du user sur le même problème = contexte pollué → proposer la bascule (en NL, jamais en jargon : « on repart sur une page blanche avec ce qu'on a appris ? »).
- Entre deux tâches sans rapport, un contexte vierge est préférable à la continuité.
- La proposition de bascule s'appuie sur `session-handoff.md` (tri 3 catégories, récap de reprise).

## 8. Diagnostic (tech-level haut uniquement)

Quand le user est outillé Claude Code et que la question du contexte se pose concrètement : `/context` (répartition live par catégorie), `/usage` (consommation par skill / subagent / plugin / serveur MCP), `/memory` (fichiers d'instructions chargés), `/doctor` (débordement du budget de descriptions de skills), `claude plugin details <nom>` (coût tokens d'un plugin, always-on vs à l'invocation). Ne jamais exposer ces commandes à un user non-tech — formuler le diagnostic en langage naturel.

## 9. Écarts Cowork

- La transitivité du `@` n'est pas native : cascade manuelle via Read (doctrine §2ter, `lecture-arborescente.md`).
- Les mécanismes Claude Code (`.claude/rules/` scopées, compaction documentée, commandes de diagnostic) ne sont pas garantis : en Cowork, ne compter que sur les leviers universels — placement de l'info (racine vs sous-dossier vs lien) et densité des fichiers.
- Les règles de placement du §5 restent valables partout : elles reposent sur la structure du workspace, pas sur le harness.
