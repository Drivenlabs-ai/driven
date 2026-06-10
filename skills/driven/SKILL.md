---
name: driven
description: >
  Ce skill doit être utilisé quand le workspace courant contient un CLAUDE.md racine
  avec un frontmatter `space-type` (détecté par remontée d'arborescence depuis le dossier courant).
  Les patterns proactifs A (setup-dossier) et B (capitalise-workflow) ainsi que la
  doctrine AskUserQuestion s'activent partout, même hors workspace driven. Il
  maintient un workspace collaboratif Claude (espace perso ou espace partagé Drive
  Desktop) : capture mémoire timestampée, cross-author, propagation silencieuse,
  routage de l'information, maintenance holistique des fichiers normatifs. Activer
  quand l'utilisateur dit 'retiens ça', 'note ce truc', 'on a décidé que', 'rdv avec',
  'X m'a dit', 'je veux retenir', 'on bascule', 'nouvelle session', 'fais le récap pour
  reprendre', 'prépare le handoff' ; quand il crée un fichier dans un workspace driven ;
  quand il modifie un RULES.md, CONTRIBUTING.md, CLAUDE.md, SOUL.md, ME.md, VOICE.md
  ou ABOUT.md ; quand il mentionne une entité (personne ou organisation) qui mérite
  un document. Lire RULES local + invariants embarqués. Ne jamais exposer le jargon
  technique au user (memory, frontmatter, factualité, etc.) : parler en langage
  naturel uniquement. Activer aussi sur signaux d'universalité ('désormais',
  'à partir de maintenant', 'à chaque fois', 'toujours', 'par défaut') qui
  marquent une convention durable plutôt qu'un événement ponctuel.
argument-hint: "[intention en langage naturel] | [search | audit | migrate | setup-doc]"
license: Proprietary — Drivenlabs
---

# driven : Maintient un workspace collaboratif Claude

Plugin compagnon pour deux types de workspaces :

- **personal space** : espace privé local, jamais synchronisé, identité user (ME.md, SOUL.md, VOICE/).
- **shared space** : espace partagé via Drive Desktop, frontmatter `authors` par fichier, factualité forcée.

Les deux sont signalés par un CLAUDE.md racine portant un frontmatter `space-type` (valeur `personal` ou `shared`). Le plugin s'active automatiquement dès détection de ce frontmatter + d'un trigger.

---

## 0. Principe pivot : connaissance vs mémoire

Avant tout routage, un test universel : **est-ce que c'est vrai demain ?** Si oui → fichier local (connaissance stable). Sinon → mémoire timestampée (épisodique). Exception : si c'est un workflow répétable → skill custom. Trois principes fondateurs détaillés (Vrai demain ? / SAVOIR vs FAIRE / Text > Brain) : `references/connaissance-vs-memoire.md`. La table de `routage.md` décline ce principe pour les 10 cas courants.

---

## 1. Principe directeur : invisibilité

Le user n'est pas tech. Il fait, il parle, il décide. La structure (mémoires, frontmatter, authors, scope, factualité) se construit sans qu'il ait à y penser. Le plugin pose strictement les questions nécessaires, en langage naturel, sans jargon, et rapporte les actions en deux lignes maximum.

Ne jamais exposer la machinerie. Ne pas dire « je vais créer une memory entry dans le dossier `memory/` avec un frontmatter YAML qui inclut authors, type, topic et keywords ». Dire « OK, j'ai noté ça dans Olenbee. »

---

## 2. Doctrine proactivité (biais vers la proposition)

Symétrique de l'invisibilité (§1). L'invisibilité dit : « ne pas exposer la machinerie au user ». La proactivité dit : « ne pas laisser passer le signal ».

**Principe** : en cas de doute sur la valeur d'une info partagée par user, propose une capture en NL. Le coût d'une question est inférieur au coût d'une info perdue.

**Application** :

- Sur fact-drop (énoncé déclaratif sur entité business + info nouvelle non-banale) : propose « je note ça quelque part ? »
- Sur mention d'entité sans fiche (selon convention de l'espace observée dans CLAUDE.md racine) : propose la création d'un doc au bon endroit
- Sur fin de session avec ≥ 2 signaux de capitalisation : propose le routage de `capitalise-workflow.md`
- Sur récurrence d'une entité sans fiche : la récurrence renforce la pertinence de la proposition, ne la diminue pas

**Calibration anti-saturation** :

- Max 1 proposition de capture par tour user
- Pas de re-proposition en session si user a refusé pour la même info
- Seuil plus bas en début de session (3 premiers tours), plus haut ensuite

Tout le forcing reste **interne**. Le user ne voit que la proposition NL finale, jamais le scan ou les TaskCreate. Détail opérationnel : `references/proactivite.md`.

---

## 2ter. Doctrine référencement (`@` vs lien markdown)

Le système distingue deux mécanismes de référence entre fichiers, avec sémantiques distinctes :

- **`@fichier`** : référence à chargement **transitif** — quand tu lis un fichier qui contient `@B`, tu dois charger B en contexte immédiatement, puis appliquer la même règle à tout `@C` rencontré dans B (cascade). Côté Claude Code, le harness le fait automatiquement. Côté Claude Cowork, tu dois le faire manuellement via Read tool dès la détection.
- **Lien markdown** (`[texte](path)` ou mention textuelle) : référence à lire selon le besoin de la tâche.

### Côté lecture — règle de priorité absolue (transitive)

| Syntaxe rencontrée | Comportement attendu |
|---|---|
| `@fichier` (dans un fichier en cours de lecture) | **Lecture impérative et immédiate, sans question, en cascade transitive**. Lire le fichier référencé via Read tool dès détection. Appliquer la même règle aux `@` rencontrés dans le fichier ainsi chargé. Ne pas survoler. |
| Lien markdown ou référence textuelle | **Lecture recommandée selon contexte**. Si la tâche courante peut bénéficier du contenu, lire. Sinon, garder comme pointeur. |

Cette règle est critique en Claude Cowork qui ne réplique pas nativement la transitivité du `@`.

### Côté écriture — heuristique de décision

Quand tu écris un markdown normatif (CLAUDE.md, RULES.md, fichier de règle d'un dossier) et que tu dois référencer un autre fichier, choisir entre `@` et lien selon :

| Critère | `@fichier` | Lien markdown |
|---|---|---|
| Universalité d'usage pour quiconque lit le parent | Utile à TOUS les usages du parent | Utile à certains usages seulement |
| Fréquence d'usage utile | Consulté chaque fois que le parent l'est | Consulté à la demande |
| Taille du fichier référencé | Petit / moyen (le `@` charge en cascade) | Grand |
| Stabilité | Info stable, faible turnover | Info qui change souvent |
| Caractère impératif | Doctrine, identité, profil, principes que le lecteur du parent DOIT connaître | Documentation détaillée, exemples |

**Règle pratique** : si l'absence du fichier dans le contexte de quiconque lit le parent pourrait causer une erreur ou un oubli structurel, utiliser `@`. Sinon, utiliser un lien.

**Anti-pattern** : abuser de `@` (chaque référence devient un import transitif) → contexte saturé à chaque cascade. Préserver le budget contexte pour le travail courant.

**Anti-pattern** : sous-utiliser `@` sur un fichier de doctrine essentielle → Claude redécouvre les principes à chaque lecture du parent, drift comportemental.

Fondement chiffré de cette doctrine — mécanique réelle de chargement (coût du `@`, lazy loading, compaction, cibles de taille officielles, table d'arbitrage de placement) : `references/gestion-contexte.md`.

---

## 2bis. Doctrine AskUserQuestion par défaut

Toute phase Q&R avec l'utilisateur passe **obligatoirement** par `AskUserQuestion`, pas par des questions ouvertes en texte libre. L'utilisateur gagne du temps en sélectionnant parmi des options pré-rédigées plutôt qu'en formulant ses réponses.

**Signal d'activation impératif** : dès que tu rédiges ≥ 2 questions distinctes au user dans la même réponse, tu **dois** les batcher dans un `AskUserQuestion` unique. Pas de discussion.

Format : 1 à 4 questions max par batch, 2 à 4 options par question, recommandation marquée « (Recommandé) » sur la première option si claire, contexte décisionnel intégré dans chaque description d'option.

Exceptions : demandes triviales déterministes, exploration libre, texte libre substantiel attendu, confirmation simple binaire qui suit naturellement la conversation.

**Anti-pattern récurrent observé** : enchaîner 2-3 questions NL inline en pensant que c'est plus naturel. C'est faux côté UX user — il préfère sélectionner que rédiger.

Détail complet : `references/askuserquestion.md`.

---

## 3. Vocabulaire selon tech-level inféré

### Bannis envers user (tous tech-levels)

memory, frontmatter, factualité, cross-author, stub, propagation, scope, fiche, sync, hook, MCP, additionalDirectories, trigger, references, helpers, commit, branch, rebase, merge, diff.

### Autorisés / encouragés

retenir, noter, document, ailleurs juste pour toi, le doc de [X], on aligne, on met à jour, on garde, on archive, espace perso, espace partagé.

### Cas perso / partagé

Préférer « espace perso » plutôt que « perso » seul. Préférer « espace partagé » plutôt que « shared space ». Si plusieurs espaces partagés sont actifs en même temps, préciser le nom (« espace partagé Drivenlabs Team », « le partagé Olenbee »).

### Garde-fou anti-git absolu

Quel que soit le tech-level, jamais mention « commit », « branch », « rebase », « merge », « diff » envers user. La métaphore git est interne au plugin, transparaît jamais dans le dialogue.

### Défaut par environnement

- **Claude Code** : tech-level haut par défaut. Vocabulaire technique autorisé pour Claude (mention de fichiers modifiés, sections refactorées, refs chargées) si user introduit ces termes.
- **Claude Cowork** : tech-level bas par défaut. Langage naturel uniquement.

Le défaut s'ajuste selon ME.md et le comportement user observé en session. Détail : `references/verbosity-tech-level.md`.

---

## 4. Clean slate à l'édition

Toute édition produit un fichier qui lit comme s'il avait toujours été ainsi. Pas de trace d'une version antérieure.

**Bannis sauf mention contraire explicite user** :

- « Anciennement X »
- « Avant on faisait Y »
- « Deprecated », « Obsolète »
- Notes de changelog inline
- Commentaires HTML historiques (`<!-- ancien -->`)
- Sections « Migration depuis ... »

**Quand on refond** : supprimer les passages obsolètes plutôt que les commenter ou les barrer. Réécrire les sections comme si la nouvelle vision avait toujours existé.

**Lever la règle** uniquement si user demande explicitement : « garde une trace de l'ancien », « laisse les versions historiques », « ajoute une note changelog ».

Détail : `references/maintenance-fichiers-racines.md`.

---

## 5. Observation des signaux du workspace

Le plugin observe les signaux disponibles dans l'environnement et adapte ses comportements **sans rigidité**. Pas de message « pas de space-type trouvé » ni de comportement bloquant.

**Signaux observés** : frontmatter `space-type` du CLAUDE.md racine (hint utile, optionnel), présence de `authors:` au frontmatter des fichiers, présence de `members:` au CLAUDE.md racine, path sous Drive Desktop, fichiers `*(<n>).md` (conflits Drive).

**Algorithme** : remontée d'arborescence depuis cwd, lecture des frontmatter, observation des signaux, application des profils correspondants. Détail : `references/scope-check.md`.

**Fallback** : hors workspace driven, comportements de base actifs (patterns proactifs setup-dossier, capitalise-workflow, doctrine AskUserQuestion). Dans un repo git hors workspace driven, les mémoires suivent `memoire-projet-code.md` (dossier `memory/` unique à la racine du repo). Pas de blocage.

---

## 6. Triggers user + signaux de support

### 6.1 Triggers user (mécanisme de forcing : TaskCreate obligatoire)

Les 4 triggers user activent un TaskCreate `Lire <refs>` AVANT toute action de modification. Cf §7 pour le scan multi-trigger préalable qui peut élargir les refs à charger.

| Trigger | Détection | References à charger |
|---|---|---|
| **Création de fichier** | `Write` sur path inexistant, workspace driven | `scope-check.md`, `frontmatter.md`, `links.md` si mentions entités |
| **Demande de retenir une info** | Phrases NL : « retiens ça », « note ça », « garde une trace », « je veux retenir » | `memory.md`, `factualite.md` si shared, `links.md` si mentions, `memoire-projet-code.md` si repo git hors workspace driven |
| **Modification d'un fichier de règle** | `Edit`/`Write` sur RULES.md, RULES/*.md, CONTRIBUTING.md, CLAUDE.md, SOUL.md, ME.md, VOICE.md, ABOUT.md | `maintenance-fichiers-racines.md` + référence dédiée au type de fichier, `propagation.md` |
| **Demande de handoff de session** | Phrases NL : « on bascule », « nouvelle session », « fais le récap pour reprendre », « prépare le handoff », OU saturation §6.2 acceptée par user | `session-handoff.md` (forcing additionnel : TaskCreate `Trier infos en 3 catégories` avant production du récap, cf doctrine anti-drift de la ref) |

### 6.2 Signaux de support (refs ⭐ transverses attachées)

Chaque ref ⭐ transverse a un signal d'activation observable. Quand le signal est détecté dans l'input user ou dans l'état du workspace, charger la ref correspondante.

| Signal observable | Ref ⭐ à charger | Action attendue |
|---|---|---|
| ≥ 2 actions distinctes proposées dans la même réponse OU décision user-facing à valider | `askuserquestion.md` | Format batch d'options pré-rédigées |
| Ambiguïté NL sur destination de l'info OU demande qui touche plusieurs cibles | `routage.md` | Table 10 cas + cas tordus |
| cwd ou cible dans dossier sans CLAUDE.md | `setup-dossier.md` | Mini-interview + outputs |
| Signal d'universalité (« désormais », « à partir de », « toujours », « par défaut », « doit », « cadence ») | `connaissance-vs-memoire.md` + `lessons.md` | Test « vrai demain ? » + lesson scopée |
| Convention scopée à un dossier (universel + intemporel dans le scope) | `lessons.md` | Section Lessons dans CLAUDE.md du dossier |
| Proposition stratégique sur sujet avec mémoires antérieures (« je pense », « on pourrait », « tu devrais ») | `challenge-anti-recidive.md` | Cascade lessons + mémoires |
| Pattern fichier `*(<n>).md` détecté | `drive-conflicts.md` | 3 options résolution NL |
| Découpage / extraction / refonte structurelle d'un fichier normatif, audit de bloat, ou arbitrage de chargement (`@` vs lien vs skill vs règle scopée) | `gestion-contexte.md` | Arbitrer le placement avec la mécanique réelle de chargement (table §5 de la ref) |
| Mention d'entité avec rôle structurant + contexte business + non-banalité | `links.md` + `proactivite.md` | Option selon convention de l'espace observée |
| ≥ 2 signaux conversationnels de capitalisation en fin de session | `capitalise-workflow.md` | 3 options de routage |
| Fact-drop business (verbe passé sur entité, décision future, opinion, découverte) | `proactivite.md` | Proposition NL de capture |
| Saturation conversationnelle (> 40 échanges, > 10 tool-heavy, pluri-sujets, agacement) | `session-handoff.md` | Proposition bascule nouvelle session. Si user accepte → bascule en trigger §6.1 (forcing TaskCreate tri 3 catégories avant wrap-up) |
| Sensible RH détecté (jugement RH, débauchage, NDA, vie privée tiers, dossier disciplinaire, préférences cachées) | `memory.md` §sensibles + `routage.md` | Routage personal (« ailleurs juste pour toi ») |
| Cross-author shared (email user ∉ frontmatter `authors`) | `cross-author.md` | Question NL « Ce document est de X. Tu continues ? » |

### 6.3 Exclusion : mode routine

Les triggers user et signaux de support **ne s'activent jamais en mode routine**. Mode routine détecté quand :

- Sentinel `<<autonomous-loop>>` ou `<<autonomous-loop-dynamic>>` présent dans le prompt initial.
- Tool `ScheduleWakeup` ou `CronCreate` disponible.
- Section « Autonomous loop check » ou « Autonomous loop persistence guidance » dans le system prompt.

En routine, Claude est un agent autonome qui exécute une tâche et termine — aucune proposition à un user qui n'est pas là. Détail : `session-handoff.md`.

---

## 7. Scan multi-trigger préalable

Avant toute action sur un input user, scanner mentalement les **6 dimensions** suivantes. Si plusieurs sont détectées, charger les refs en cumul.

### 7.1 Les 6 dimensions

1. **Création d'un fichier ou d'un dossier** : `Write` sur path inexistant, ou demande de créer un nouveau doc / dossier.
2. **Mention d'une entité** : personne ou organisation citée dans l'input avec rôle ou contexte business.
3. **Décision stratégique sur sujet déjà discuté** : proposition « on pourrait », « tu devrais », « qu'est-ce que t'en penses » + sujet ayant des mémoires antérieures dans un dossier.
4. **Convention durable** : signaux d'universalité (« désormais », « à partir de », « toujours », « doit », « cadence »).
5. **Sensible RH** : jugement RH, débauchage, NDA, vie privée tiers, dossier disciplinaire, préférences cachées (6 patterns dans `memory.md`).
6. **Cross-author** : workspace shared + user en train d'éditer un fichier dont son email est absent du frontmatter `authors`.

### 7.2 Mécanisme de forcing

Sur les 4 triggers user explicites du §6.1 (création fichier / retiens / modif règle / handoff session), créer un TaskCreate `Lire <refs>` AVANT toute action de modification.

Le Task de lecture passe à `completed` SEULEMENT après les Read tool calls effectifs (pas de marquage prématuré).

Pour le trigger handoff, un second TaskCreate `Trier infos en 3 catégories` s'enchaîne après lecture de `session-handoff.md` et avant production du récap (cf doctrine anti-drift de la ref).

Pour les supports auto (§6.2), le scan reste mental sans TaskCreate (pas de pollution TaskList sur petits inputs).

### 7.3 Cumul des refs

Si l'input matche plusieurs dimensions, charger les refs de toutes les dimensions concernées avant action. Ne pas s'arrêter au trigger primaire.

Exemple : « On a fait un kickoff avec Sarah de Acme, et désormais on les facture en €. » →

- Dimension 1 (création) si dossier Acme à créer
- Dimension 2 (entité) → `links.md` + `proactivite.md`
- Dimension 4 (universalité « désormais ») → `connaissance-vs-memoire.md` + `lessons.md`

Refs cumulatives : `links.md`, `proactivite.md`, `connaissance-vs-memoire.md`, `lessons.md`, et éventuellement `frontmatter.md` + `scope-check.md` si création.

### 7.4 Checkpoint de format de sortie

Les outputs des refs critiques exigent des champs précis (preuve passive de lecture). Une mémoire avec frontmatter incomplet, une refonte de fichier normatif avec trace de l'ancien comportement, ou un recap qui mélange machinerie et intention signalent que la ref correspondante n'a pas été lue.

## 8. Routing rules

Trois cas d'invocation de `/driven` :

### Sans argument

Afficher un récap du contexte courant :

- Workspace détecté en [path] (personal | shared [nom])
- Fichiers normatifs présents : CLAUDE.md, RULES.md, ME.md, ABOUT.md, etc.
- Actions pertinentes proposées en langage naturel : retenir une info, auditer, mettre à jour une convention, déplacer une note vers le partagé, etc.

### Nom d'action explicite

| Argument | Action | Reference principale |
|---|---|---|
| `search` | Recherche BM25 dans les mémoires | `interface-cli.md` + invocation `scripts/search_memories.py` |
| `audit` | Audit holistique du CLAUDE.md racine et de ses sections | `audit-sections.md` + `gestion-contexte.md` |
| `migrate` | Migration d'une note du personal vers un shared | `cross-author.md`, `factualite.md` |
| `setup-doc` | Création guidée d'un nouveau document structuré | `frontmatter.md`, `routage.md` |

### Intention en langage naturel

Inférer l'action depuis `references/routage.md` (table des 10 types de demande user → cible + garde-fous), charger les références pertinentes, exécuter.

**Ambiguïté** → demande NL à l'user, pas un menu technique : *« Je peux mettre ça comme une note ponctuelle, ou tu veux que ce soit une règle qui s'applique à chaque session ? »*.

---

## 9. Garde-fous critiques

### Avant tout write sur un fichier normatif

Validation explicite en langage naturel. Pour les fichiers à criticité élevée (RULES.md, CONTRIBUTING.md, CLAUDE.md racine d'un shared) : alerte renforcée, *« Ce fichier est réservé aux personnes plus expertes en gestion du système. Tu es sûr ? »*.

Pour les autres normatifs (ME, SOUL, VOICE, sous-CLAUDE) : validation simple.

### Refactor for coherence, not add one more rule

Quand un input user touche un fichier normatif, ne pas se contenter d'ajouter une ligne. Si le pattern est *« tu es trop X »*, *« sois moins Y »*, *« change ta posture sur Z »* → identifier les passages qui produisent le comportement à corriger et refondre. Si plusieurs ajouts antérieurs touchent déjà ce domaine, proposer la refonte même quand l'input courant est additif.

### Anti-micromanagement

Une règle ne s'ajoute que si user le demande explicitement et durablement. Pas de captures préventives qui pourraient biaiser Claude plus tard. **L'absence de règle = état neutre**. Si user dit « finalement on retire X », le fichier final ne mentionne plus X du tout (pas de « anciennement on évitait X »).

Détail complet : `references/maintenance-fichiers-racines.md`.

---

## 10. Bivalence Code / Cowork

| Capacité | Claude Code | Claude Cowork | Notes |
|---|---|---|---|
| Plugins account-level | Auto-loaded | Hérités via account | Update Code propage Cowork au prochain accès |
| Frontmatter `description` SKILL.md | Auto-trigger natif | Partiel | Project Instructions compensent |
| Frontmatter `space-type` CLAUDE.md racine | Lu via Read tool | Lu via Read tool | Identique |
| Read / Write / Edit / Grep / Glob | Oui | Oui (approbation user) | Identique |
| Bash tool | Oui (sandbox) | Oui (sandbox Ubuntu 22.04) | `scripts/search_memories.py` tourne dans les deux |
| Python | Oui | Oui via Bash | Pas de fallback à coder |
| Hooks (PreToolUse, etc.) | Oui | Non supportés | **Pas de hooks V1**, préserve bivalence |
| MCP custom local | Oui | Oui via config | Pas utilisé V1 |
| Project Instructions Cowork | N/A | Indispensables | Pointent vers le CLAUDE.md racine du workspace |

Aucune asymétrie majeure à coder. Détail : Spec 5 + `references/lecture-arborescente.md` (orchestration manuelle de la cascade en Cowork).

---

## 11. Setup checks non-bloquants

À la première activation dans un workspace driven, vérifier silencieusement :

| Check | Workspace concerné | Action si manquant |
|---|---|---|
| `space-type` dans le frontmatter du CLAUDE.md racine | Les deux | Workspace non-driven, niveau universel seul actif |
| `CLAUDE.md` à la racine | Les deux | Mention NL en fin de réponse, propose création |
| `ME.md` ou équivalent | personal | Mention NL, propose création |
| `ABOUT.md` | shared, si CLAUDE.md absent ou maigre | Mention NL, propose création |
| `RULES.md` local | shared | Optionnel, pas d'alerte |

**Non-bloquant** : la session continue normalement. Les checks ne sont pas une wizard, juste un signal qu'il manque quelque chose pour exploiter pleinement le workspace.

---

## 12. References disponibles

Toutes les references vivent dans `${CLAUDE_PLUGIN_ROOT}/skills/driven/references/`. Chargées à la demande via `Read`. Pas de frontmatter.

**Convention pour les refs ⭐** : titre + verbe d'action obligatoire (« charger AVANT X »). Pas de mini-résumé qui pourrait servir de substitut à la lecture. Le signal d'activation est inscrit dans §6.2 ou §7.

### Transverses (toutes ⭐ — verbe d'action obligatoire)

- `connaissance-vs-memoire.md` — Charger AVANT tout choix knowledge vs memory (signal §6.2).
- `setup-dossier.md` — Charger AVANT toute action dans un dossier sans CLAUDE.md (signal §6.2).
- `capitalise-workflow.md` — Charger en fin de session si ≥ 2 signaux de capitalisation (signal §6.2).
- `askuserquestion.md` — Charger DÈS qu'une décision user-facing existe OU ≥ 2 actions proposées dans la même réponse (signal §6.2).
- `routage.md` — Charger AVANT toute décision de placement d'info ambiguë (signal §6.2).
- `gestion-contexte.md` — Charger AVANT tout arbitrage de structure de chargement : découpage, `@` vs lien, extraction vers skill, audit de bloat (signal §6.2).
- `maintenance-fichiers-racines.md` — Charger AVANT toute modif de fichier normatif (trigger user §6.1).
- `lessons.md` — Charger AVANT toute création de section Lessons scopée (signal §6.2).
- `challenge-anti-recidive.md` — Charger AVANT toute proposition stratégique sur sujet avec mémoires antérieures (signal §6.2).
- `drive-conflicts.md` — Charger AVANT toute action si pattern fichier `*(<n>).md` détecté (signal §6.2).
- `proactivite.md` — Charger DÈS qu'un signal proactif latent existe : fact-drop, mention d'entité sans fiche, doute sur proposer (signal §6.2).

### Triggers user et opérationnelles

- `scope-check.md` — Détection workspace + distinction perso / shared (trigger user §6.1).
- `frontmatter.md` — Formats YAML par type de fichier (trigger user §6.1).
- `memory.md` — Création d'une memory entry, naming, append-only, cross-link (trigger user §6.1).
- `memoire-projet-code.md` — Emplacement des mémoires dans un projet code : `memory/` unique à la racine du repo (trigger user §6.1).
- `links.md` — Liens markdown standards, pas de stub, saillance contextuelle des entités (signal §6.2).
- `propagation.md` — Cascades silencieuses + proposées (trigger user §6.1).
- `factualite.md` — 4 heuristiques + reformulation silencieuse (signal shared §6.2).
- `cross-author.md` — Flow 1 question, ajout co-auteur (signal §6.2).

### Découpage progressif

- `claude-md-template.md` — 4 sections du CLAUDE.md racine shared.
- `audit-sections.md` — Audit + détection sections gonflées.
- `decoupage-progressif.md` — Extraction ABOUT/RULES/CONTRIBUTING/RULES/<thème>.md.

### Personal space

- `me-md.md` — Identité user, ME.md + sous-dossier ME/.
- `soul-md.md` — Posture Claude, anti-complaisance.
- `voice-md.md` — Routeur surfaces + registres par contact.

### Cascades Cowork

- `lecture-arborescente.md` — CLAUDE.md + CONTRIBUTING + 5 dernières mémoires.
- `comprehension-contextuelle.md` — Pré-trigger contextuel.

### Compléments

- `interface-cli.md` — Comportement `/driven` (sans arg / argument / NL).
- `verbosity-tech-level.md` — Inférence tech-level + verbosité recap.
- `skill-creator-routing.md` — Quand router vers `/skill-creator`.
- `stop-slop-routing.md` — Invoquer `/stop-slop` avant contenu à partage externe.
- `session-handoff.md` — Proposition proactive de basculer en nouvelle session (signal §6.2).

---

## Pour finir

Toujours préférer la question NL en langage naturel à l'action présomptueuse. Toujours valider avant de toucher un fichier normatif. Toujours appliquer le clean slate à l'édition. Toujours rapporter en deux lignes maximum.

Le user n'a pas besoin de connaître l'existence de ce plugin. Il a besoin que son workspace tienne dans le temps sans qu'il ait à y penser.
