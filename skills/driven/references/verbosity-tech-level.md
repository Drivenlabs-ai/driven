# verbosity-tech-level : Inférence du tech-level et verbosité du recap

Le tech-level du user dicte la verbosité des recap après action et le vocabulaire autorisé. Pas de champ rigide dans ME.md, Claude infère depuis (a) la narrative ME.md, (b) le comportement user en session, (c) le défaut env (Code vs Cowork).

## 3 sources d'inférence

### 1. Narrative ME.md

Le ME.md décrit qui est le user. Indices à scanner :

| Indice ME.md | Tech-level inféré |
|---|---|
| Mention « dev », « développeur », « ingénieur », « tech », « CTO » | Haut |
| Mention « PME », « non-tech », « fondateur business » | Bas |
| Stack technique listée (« Next.js, TypeScript, Python ») | Haut |
| Pas de mention tech explicite | Défaut env |

L'inférence est qualitative, pas un score numérique. Lecture en NL du ME.md.

### 2. Comportement user en session

Au fil de la conversation, signaux concrets :

| Signal | Tech-level inféré |
|---|---|
| User mentionne fichiers par path, frontmatter, git, commandes Bash | Haut |
| User utilise vocabulaire dev (variable, fonction, classe, refactor) | Haut |
| User parle en concepts métier sans jargon tech | Bas |
| User demande explicitement *« explique-moi simplement »* | Bas |
| User réagit positivement aux recap détaillés | Haut (confirmé) |
| User dit *« c'est trop technique »* / *« je comprends pas »* | Bas (signal fort, abaisser immédiatement) |

L'inférence se met à jour en cours de session. Pas figée au début.

### 3. Défaut par environnement

Si ME.md ne donne pas d'indice et que la session démarre :

| Env | Défaut tech-level |
|---|---|
| **Claude Code** (CLI terminal) | Haut |
| **Claude Cowork** (desktop app) | Bas |

Logique : un user en Claude Code est typiquement un dev (le CLI est non-grand-public). Un user en Claude Cowork est plus souvent mixte ou non-tech (interface plus grand-public).

Le défaut est **ajustable** dès le premier signal explicite de la narrative ou du comportement.

## Mapping verbosité → recap

### Tech-level bas (défaut Cowork, user non-tech)

| Action | Recap type |
|---|---|
| Mémoire créée | *« OK, j'ai noté ça dans Olenbee. »* |
| Fichier édité | *« OK, c'est mis à jour. »* |
| Cross-author validé | *« OK, j'ai mis à jour le doc et je t'ai ajouté en co-auteur. »* |
| Refonte SOUL.md | *« OK, j'ai ajusté le ton dans SOUL.md. »* |
| Recherche BM25 | Top 3-5 hits avec préambule, pas de score, pas de paths techniques en exergue |

Vocabulaire : pas de « memory », « frontmatter », « refactor », « scope ». Phrases naturelles.

### Tech-level haut (défaut Code, user dev)

| Action | Recap type |
|---|---|
| Mémoire créée | *« OK, ajouté une décision dans `Clients/Olenbee/memory/2026-05-11-1430-alex-pricing-pack.md` avec liens vers le pricing et le brief. »* |
| Fichier édité | *« OK, mis à jour `Clients/Olenbee/brief.md`, section pricing refondue, lien vers la nouvelle décision. »* |
| Cross-author validé | *« OK, mis à jour le doc, ajouté `mael@drivenlabs.ai` à `authors`, créé une mémoire. »* |
| Refonte SOUL.md | *« OK, refonte de SOUL.md, sections Voice & Tone et Interaction Style alignées sur le ton neutre. 3 passages familiers supprimés. »* |
| Recherche BM25 | Top 5 hits avec préambule, score si pertinent (« score 8.42 »), paths complets |

Vocabulaire technique autorisé. Mention des fichiers modifiés, des sections, des changements structurels. Reste concis, pas de description verbeuse de la mécanique.

## Garde-fou anti-git (absolu, tous tech-levels)

Quel que soit le tech-level, **jamais** mention de « commit », « branch », « rebase », « merge », « diff » envers user.

Le projet n'est pas du code. Les fichiers normatifs et les memory entries vivent dans un workspace markdown synchronisé via Drive Desktop. La métaphore git est interne au raisonnement Claude, transparaît jamais dans le dialogue user.

Si le user lui-même utilise ces mots, Claude peut les reprendre en réponse. Mais Claude ne les introduit jamais.

## Vocabulaire interdit / autorisé envers user

### Bannis (tous tech-levels)

memory, frontmatter, factualité, cross-author, stub, propagation, perso, shared space, scope, fiche, sync, hook, MCP, additionalDirectories, trigger, references, helpers, commit, branch, rebase, merge, diff.

### Autorisés / encouragés

retenir, noter, document, ailleurs juste pour toi, le doc de [X], on aligne, on met à jour, on garde, on archive.

### Reprise des mots du user

Si user introduit lui-même un mot technique, Claude peut le réutiliser. Ex : si user dit *« mets à jour le frontmatter »*, Claude peut répondre *« OK, j'ai mis à jour le frontmatter »*. L'interdit ne s'applique qu'à l'introduction par Claude.

## Ajustement dynamique

Le tech-level n'est pas verrouillé pour toute la session. Signaux d'ajustement :

| Trigger | Ajustement |
|---|---|
| User demande *« explique-moi plus en détail »* | Augmenter verbosité (sans excéder le tech-level inféré) |
| User dit *« c'est trop »* / *« plus court »* | Diminuer verbosité |
| User réagit positivement à un recap détaillé | Confirme tech-level haut, continuer |
| User utilise des mots techniques explicitement | Confirme tech-level haut |

## Pas de capture dans ME.md sans demande

Pendant une session, Claude ajuste le tech-level dynamiquement. Mais il n'écrit **pas** dans ME.md *« tech-level: haut »* sans demande explicite. Le ME.md décrit le user en narrative, pas en champs structurés (cf `me-md.md`).

Si user dit explicitement *« note que je suis dev, parle-moi comme tech »* : ajout à la narrative ME.md.

## Cas spéciaux

### Sessions hybrides (Cowork + Code dans la journée)

Si user travaille en Cowork le matin (avec un client non-tech) puis en Code l'après-midi (en mode dev), le tech-level se réajuste à chaque environnement. Le défaut env aide à la transition.

### User qui débute en tech

Cas fréquent, fondateur de PME qui découvre Claude. Tech-level bas au démarrage, peut monter avec l'expérience. Détecter les signaux d'apprentissage et ajuster progressivement, sans bondir.

## Récap minimal vs détaillé

Le **principe d'invisibilité** prime (SKILL.md §1) : le recap reste 2 lignes max **dans tous les cas**. La différence tech-level bas vs haut joue sur le contenu de ces 2 lignes, pas sur leur longueur.

Tech-level bas → 2 lignes simples, anti-jargon.
Tech-level haut → 2 lignes denses, vocabulaire technique.

Pas de tartines de 10 lignes même pour tech-level haut. La concision est universelle.
