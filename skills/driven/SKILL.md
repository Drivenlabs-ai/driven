---
name: driven
description: >
  Ce skill doit être utilisé quand le workspace courant contient un fichier `.driven`
  à la racine (détecté par remontée d'arborescence depuis le dossier courant). Il
  maintient un workspace collaboratif Claude (espace perso ou espace partagé Drive
  Desktop) : capture mémoire timestampée, cross-author, propagation silencieuse,
  routage de l'information, maintenance holistique des fichiers normatifs. Activer
  quand l'utilisateur dit 'retiens ça', 'note ce truc', 'on a décidé que', 'rdv avec',
  'X m'a dit', 'je veux retenir' ; quand il crée un fichier dans un workspace driven ;
  quand il modifie un RULES.md, CONTRIBUTING.md, CLAUDE.md, SOUL.md, ME.md, VOICE.md
  ou ABOUT.md ; quand il mentionne une entité (personne ou organisation) qui mérite
  un document. Lire RULES local + invariants embarqués. Ne jamais exposer le jargon
  technique au user (memory, frontmatter, factualité, etc.) : parler en langage
  naturel uniquement.
argument-hint: "[intention en langage naturel] | [search | audit | migrate | setup-doc]"
license: Proprietary — Drivenlabs
---

# driven : Maintient un workspace collaboratif Claude

Plugin compagnon pour deux types de workspaces :

- **personal space** : espace privé local, jamais synchronisé, identité user (ME.md, SOUL.md, VOICE/).
- **shared space** : espace partagé via Drive Desktop, frontmatter `authors` par fichier, factualité forcée.

Les deux sont signalés par un fichier `.driven` (zéro octet) à la racine. Le plugin s'active automatiquement dès détection du marker + d'un trigger.

---

## 1. Principe directeur : invisibilité

Le user n'est pas tech. Il fait, il parle, il décide. La structure (mémoires, frontmatter, authors, scope, factualité) se construit sans qu'il ait à y penser. Le plugin pose strictement les questions nécessaires, en langage naturel, sans jargon, et rapporte les actions en deux lignes maximum.

Ne jamais exposer la machinerie. Ne pas dire « je vais créer une memory entry dans le dossier `memory/` avec un frontmatter YAML qui inclut authors, type, topic et keywords ». Dire « OK, j'ai noté ça dans Olenbee. »

---

## 2. Vocabulaire selon tech-level inféré

### Bannis envers user (tous tech-levels)

memory, frontmatter, factualité, cross-author, stub, propagation, scope, fiche, sync, hook, MCP, additionalDirectories, marker, trigger, references, helpers, commit, branch, rebase, merge, diff.

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

## 3. Clean slate à l'édition

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

## 4. Détection workspace driven

Avant tout trigger, vérifier la présence du marker `.driven` à la racine du workspace courant :

1. Depuis le dossier courant (cwd), remonter l'arborescence parent par parent.
2. À chaque niveau, vérifier l'existence d'un fichier `.driven` (zéro octet, persistant).
3. Premier `.driven` rencontré → racine du workspace.
4. Si aucun `.driven` trouvé jusqu'à la racine système → workspace non-driven, plugin silencieux (comportement Claude standard).

Le path de la racine workspace permet de distinguer :

- **personal space** : path local hors Drive Desktop (ex `~/Personal OS/`). RULE de factualité désactivée.
- **shared space** : path sous Drive Desktop (ex `~/Library/CloudStorage/GoogleDrive-.../shared/`). RULE active. `authors` trackés par fichier.

Si workspace ambigu ou multi-folder Cowork actif, vérifier le path du fichier cible avant chaque write, jamais la racine de la session. Détail : `references/scope-check.md`.

---

## 5. Triggers V1

### 3 triggers user

| Trigger | Détection | References à charger |
|---|---|---|
| **Création de fichier** | `Write` sur path inexistant, workspace driven | `scope-check.md`, `frontmatter.md`, `links.md` si mentions entités |
| **Demande de retenir une info** | Phrases NL : « retiens ça », « note ça », « garde une trace », « je veux retenir » | `memory.md`, `factualite.md` si shared, `links.md` si mentions |
| **Modification d'un fichier de règle** | `Edit`/`Write` sur RULES.md, RULES/*.md, CONTRIBUTING.md, CLAUDE.md, SOUL.md, ME.md, VOICE.md, ABOUT.md | `maintenance-fichiers-racines.md` + référence dédiée au type de fichier, `propagation.md` |

### 2 supports automatiques

| Support | Détection | References |
|---|---|---|
| **Cross-author détecté** | Avant `Edit` shared space : email user ∉ frontmatter `authors` | `cross-author.md` (active **avant** préparation du diff) |
| **Mention d'entité sans document** | Pendant rédaction shared, mention personne/organisation sans document existant | `links.md` (seuil de pertinence, pas de stub) |

---

## 6. Routing rules

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
| `audit` | Audit holistique du CLAUDE.md racine et de ses sections | `audit-sections.md` |
| `migrate` | Migration d'une note du personal vers un shared | `cross-author.md`, `factualite.md` |
| `setup-doc` | Création guidée d'un nouveau document structuré | `frontmatter.md`, `routage.md` |

### Intention en langage naturel

Inférer l'action depuis `references/routage.md` (table des 10 types de demande user → cible + garde-fous), charger les références pertinentes, exécuter.

**Ambiguïté** → demande NL à l'user, pas un menu technique : *« Je peux mettre ça comme une note ponctuelle, ou tu veux que ce soit une règle qui s'applique à chaque session ? »*.

---

## 7. Garde-fous critiques

### Avant tout write sur un fichier normatif

Validation explicite en langage naturel. Pour les fichiers à criticité élevée (RULES.md, CONTRIBUTING.md, CLAUDE.md racine d'un shared) : alerte renforcée, *« Ce fichier est réservé aux personnes plus expertes en gestion du système. Tu es sûr ? »*.

Pour les autres normatifs (ME, SOUL, VOICE, sous-CLAUDE) : validation simple.

### Refactor for coherence, not add one more rule

Quand un input user touche un fichier normatif, ne pas se contenter d'ajouter une ligne. Si le pattern est *« tu es trop X »*, *« sois moins Y »*, *« change ta posture sur Z »* → identifier les passages qui produisent le comportement à corriger et refondre. Si plusieurs ajouts antérieurs touchent déjà ce domaine, proposer la refonte même quand l'input courant est additif.

### Anti-micromanagement

Une règle ne s'ajoute que si user le demande explicitement et durablement. Pas de captures préventives qui pourraient biaiser Claude plus tard. **L'absence de règle = état neutre**. Si user dit « finalement on retire X », le fichier final ne mentionne plus X du tout (pas de « anciennement on évitait X »).

Détail complet : `references/maintenance-fichiers-racines.md`.

---

## 8. Bivalence Code / Cowork

| Capacité | Claude Code | Claude Cowork | Notes |
|---|---|---|---|
| Plugins account-level | Auto-loaded | Hérités via account | Update Code propage Cowork au prochain accès |
| Frontmatter `description` SKILL.md | Auto-trigger natif | Partiel | Project Instructions compensent |
| Marker `.driven` | Lu via Read tool | Lu via Read tool | Identique |
| Read / Write / Edit / Grep / Glob | Oui | Oui (approbation user) | Identique |
| Bash tool | Oui (sandbox) | Oui (sandbox Ubuntu 22.04) | `scripts/search_memories.py` tourne dans les deux |
| Python | Oui | Oui via Bash | Pas de fallback à coder |
| Hooks (PreToolUse, etc.) | Oui | Non supportés | **Pas de hooks V1**, préserve bivalence |
| MCP custom local | Oui | Oui via config | Pas utilisé V1 |
| Project Instructions Cowork | N/A | Indispensables | Pointent vers le CLAUDE.md racine du workspace |

Aucune asymétrie majeure à coder. Détail : Spec 5 + `references/lecture-arborescente.md` (orchestration manuelle de la cascade en Cowork).

---

## 9. Setup checks non-bloquants

À la première activation dans un workspace driven, vérifier silencieusement :

| Check | Workspace concerné | Action si manquant |
|---|---|---|
| `.driven` à la racine | Les deux | Workspace non-driven, plugin silencieux |
| `CLAUDE.md` à la racine | Les deux | Mention NL en fin de réponse, propose création |
| `ME.md` ou équivalent | personal | Mention NL, propose création |
| `ABOUT.md` | shared, si CLAUDE.md absent ou maigre | Mention NL, propose création |
| `RULES.md` local | shared | Optionnel, pas d'alerte |

**Non-bloquant** : la session continue normalement. Les checks ne sont pas une wizard, juste un signal qu'il manque quelque chose pour exploiter pleinement le workspace.

---

## 10. References disponibles

Toutes les references vivent dans `${CLAUDE_PLUGIN_ROOT}/skills/driven/references/`. Chargées à la demande via `Read`. Pas de frontmatter.

### Transverses

- `scope-check.md`, Détection workspace + distinction perso / shared.
- `frontmatter.md`, Formats YAML par type de fichier.
- `memory.md`, Création d'une memory entry, naming, append-only, cross-link.
- `links.md`, Liens markdown standards, pas de stub.
- `propagation.md`, Cascades silencieuses + proposées.
- `factualite.md`, 4 heuristiques + reformulation silencieuse.
- `cross-author.md`, Flow 1 question, ajout co-auteur.
- `routage.md`, ⭐ Table de routage de l'information (10 cas).
- `maintenance-fichiers-racines.md`, ⭐ Refactor for coherence, clean slate, anti-micromanagement.

### Découpage progressif

- `claude-md-template.md`, 4 sections du CLAUDE.md racine shared.
- `audit-sections.md`, Audit + détection sections gonflées.
- `decoupage-progressif.md`, Extraction ABOUT/RULES/CONTRIBUTING/RULES/<thème>.md.

### Personal space

- `me-md.md`, Identité user, ME.md + sous-dossier ME/.
- `soul-md.md`, Posture Claude, anti-complaisance.
- `voice-md.md`, Routeur surfaces + registres par contact.

### Cascades Cowork

- `lecture-arborescente.md`, CLAUDE.md + CONTRIBUTING + 5 dernières mémoires.
- `comprehension-contextuelle.md`, Pré-trigger contextuel.

### Compléments

- `interface-cli.md`, Comportement `/driven` (sans arg / argument / NL).
- `verbosity-tech-level.md`, Inférence tech-level + verbosité recap.
- `skill-creator-routing.md`, Quand router vers `/skill-creator`.
- `stop-slop-routing.md`, Invoquer `/stop-slop` avant contenu à partage externe.

---

## Pour finir

Toujours préférer la question NL en langage naturel à l'action présomptueuse. Toujours valider avant de toucher un fichier normatif. Toujours appliquer le clean slate à l'édition. Toujours rapporter en deux lignes maximum.

Le user n'a pas besoin de connaître l'existence de ce plugin. Il a besoin que son workspace tienne dans le temps sans qu'il ait à y penser.
