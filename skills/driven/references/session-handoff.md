# session-handoff : Reprendre la conversation dans une nouvelle session quand elle sature

Une conversation trop longue brouille le contexte et dégrade la précision de Claude. Le plugin détecte proactivement les signaux de saturation et propose de reprendre dans une nouvelle session. Le handoff est l'étape de reprise — optionnelle — d'une clôture de session (`cloture-session.md`) : la mémoire de session est créée par la clôture (phase prise de mémoire), le handoff produit le prompt de reprise dense qui la cite. Cette ref couvre la détection de saturation et le format de ce prompt.

Le risque structurel d'un wrap-up de session : la nouvelle instance Claude n'a pas vécu la session précédente. Si le prompt de reprise contient des inférences non vérifiables présentées comme des faits, la nouvelle session hérite d'un **drift silencieux** — elle agit sur la base de déductions qu'elle ne peut pas retracer. La doctrine anti-drift (§Doctrine ci-dessous) impose un tri strict avant toute inscription dans le prompt de reprise.

## Quand cette ref s'active

Trigger 4 — saturation conversationnelle. Quatre signaux possibles, n'importe lequel suffit :

| Signal | Description |
|---|---|
| Volume échanges | Plus de 40 échanges user dans la conversation courante |
| Tool-heavy | Plus de 10 actions tool-intensives cumulées (Read sur gros fichiers, Bash longs, Agent lancés, etc.) |
| Pluri-sujets | La conversation a couvert 3+ sujets structurellement distincts (ex : pricing Acme, puis design Webflow, puis prospection LinkedIn) |
| Agacement user | Phrases : « je m'y perds », « tu te répètes », « c'est bordélique », « fait court », « trop d'infos », « j'ai du mal à suivre », « tu deviens confus » |

Claude n'a pas accès direct au compteur de tokens en Code ni en Cowork. L'estimation est qualitative.

La ref s'active aussi sur demande explicite user : « on bascule », « nouvelle session », « fais le récap pour reprendre », « prépare le handoff ». Dans ce cas, la clôture (`cloture-session.md`) passe d'abord, puis ce handoff produit le prompt de reprise — pas de proposition préalable.

## Doctrine anti-drift : tri en 3 catégories

Toute info candidate à l'inscription dans le prompt de reprise passe par un tri en 3 catégories.

| Catégorie | Définition | Action |
|---|---|---|
| **C1 — Vérifiable** | Existe dans une source primaire localisable : path fichier, Message-ID Gmail, URL, ID document, output tool précis, hash de commit, output Bash daté | Inscrire avec son pointeur source |
| **C2 — Inférée** | Synthèse, déduction ou interprétation produite par Claude pendant la session, non rattachable à une source primaire | Ne PAS inscrire comme fait. Si l'info reste utile, l'inscrire dans la section « NON inscrit volontairement » avec instruction de re-déduction par la nouvelle session |
| **C3 — Incertaine** | Détail partiel, rapporté de mémoire conversationnelle sans pointeur, ou oublié en cours de session | Ne pas inscrire dans les faits. Optionnellement, marquer dans « NON inscrit volontairement » comme à re-vérifier par lecture directe |

**Règle de tri strict** : en cas de doute entre C1 et C2 → traiter comme C2. La sur-inclusion d'inférences est plus coûteuse que l'omission : un fait C1 manquant sera redécouvert par lecture, un fait C2 inscrit comme C1 contamine durablement la nouvelle session.

**Distinction faits vs décisions actées** : un fait C1 décrit un état du monde vérifiable techniquement (version dans plugin.json, contenu d'un fichier, output d'un tool). Une décision actée est un arbitrage explicite tranché par user au cours de la session, qui n'existe pas ailleurs que dans la conversation. Les deux vont dans le prompt de reprise mais dans deux blocs distincts (cf format §Format).

## Forcing : tri avant le prompt de reprise

Dès que le handoff est engagé, Claude crée un TaskCreate `Trier infos en 3 catégories` AVANT toute production du prompt de reprise.

Le Task passe à `completed` seulement après application effective du tri sur chaque info candidate (pas de marquage prématuré). Aligné sur §7.2 du SKILL.md (mécanisme de forcing TaskCreate pour les triggers user §6.1).

Production du prompt **après** complétion du tri uniquement.

## Exclusion : mode routine

Cette ref **ne s'active jamais en mode routine** (Claude lancé en `/loop`, `/schedule` ou comme sub-agent). En routine, Claude est un agent autonome qui exécute une tâche et termine — il n'y a pas d'utilisateur en interaction à qui recommander quoi que ce soit, et proposer briserait l'autonomie.

Mode routine détecté en Code via :

- Sentinel `<<autonomous-loop>>` ou `<<autonomous-loop-dynamic>>` dans le prompt initial de la session.
- Tool `ScheduleWakeup` ou `CronCreate` disponible dans la liste des tools.
- Section « Autonomous loop check » ou « Autonomous loop persistence guidance » dans le system prompt.

Mode routine en Cowork : pas de signal observable documenté — les scheduled tasks Cowork sont indistinguables d'une session normale côté Claude. Cowork est traité comme toujours interactif.

## Workflow

### 1. Détection

Claude observe la conversation en continu et juge selon les 4 signaux ci-dessus. Pas de chiffre précis sur le context window. Si un seul signal est présent, déclencher.

### 2. Proposition NL

Une phrase, naturelle, sans jargon :

> Cette conversation devient longue, je commence à perdre en précision. On la fait basculer dans une nouvelle session ? Je te prépare un récap et un prompt pour reprendre rapidement.

Si signal d'agacement détecté, adapter le phrasing :

> Je sens qu'on s'y perd un peu. On reprend dans une nouvelle session avec un récap propre ?

### 3. Si user accepte (ou demande explicitement le handoff)

a. **TaskCreate forcing du tri** : Claude crée un TaskCreate `Trier infos en 3 catégories` (doctrine anti-drift §Doctrine). Aucune production du prompt avant complétion.

b. **Application du tri** : Claude scanne mentalement chaque info candidate (décisions, faits, locks, pointeurs, actions identifiées) et les classe C1 / C2 / C3 selon la doctrine. Pour chaque C1, identifier le pointeur source exact (path:section, Message-ID, URL, output tool daté).

c. **Mémoire de session** : déjà créée par la clôture (phase prise de mémoire, `memory.md`) dans le `memory/` du dossier projet dominant. Le handoff n'en crée pas de seconde — il la cite comme source pivot du prompt. Le tri C1 / C2 / C3 alimente les blocs du prompt (§Format), pas un fichier séparé.

d. **Multi-projet** : si la session a touché plusieurs projets distincts, le prompt de reprise cible le projet dominant (celui qui a concentré l'essentiel des décisions), cohérent avec le dossier où la clôture a placé la mémoire de session. Si vraiment ambigu, demande NL :

   > On a touché Acme et le plugin driven. Je prépare la reprise sur Acme (dominant) ou un prompt par projet ?

e. **Génération du prompt de reprise** : 6 blocs denses (cf section suivante). Présenté à l'user en fin de message dans un code block, prêt à copier-coller.

### 4. Si user refuse

- Re-proposer tous les 10 échanges suivants. Pas plus serré.
- Si user dit explicitement « stop », « arrête », « pas maintenant définitif », « lâche-moi avec ça » → silencieux jusqu'à environ 90 % estimé de saturation.
- À 90 % estimé : ultime relance, mention transparente :

   > Dernière alerte sur la saturation. On est vraiment proche du seuil où je vais perdre du contexte. Je propose qu'on bascule maintenant.

  Si user refuse encore : silencieux définitif pour la session.

### 5. Cowork : où démarrer la nouvelle session

User démarre une **nouvelle conversation dans le même Cowork Project** (clic « New chat »). Garde la config multi-folder + les Project Instructions standardisées. Colle le prompt de reprise comme premier message.

Pas de nouveau Cowork Project sauf changement de scope (rare).

`/compact` Cowork existe mais perd la scrollable history — non recommandé pour ce workflow.

### 6. Code : où démarrer la nouvelle session

User lance un nouveau `claude` dans le terminal (ou nouveau pane / nouveau terminal) au même path workspace. Colle le prompt de reprise comme premier message.

## Format du prompt de reprise

6 blocs **denses, vérifiables, sans inférence implicite**. Cible : 20-35 lignes selon le volume de C1 disponible. Le user doit pouvoir le lire en 15 secondes ; la nouvelle session doit pouvoir vérifier chaque ligne contre une source.

````markdown
On reprend [Nom du projet].

## Sources à lire en priorité (paths réels)
- [path/mémoire-session.md] — capture de la session précédente
- [path/fichier-touché.md] — [raison concise]
- [autre source vérifiable : Message-ID Gmail, URL, ID document, output tool]

## Faits 100% certains (vérifiés contre sources)
- [Fait C1] (vérifié dans [path:section] ou [Message-ID] ou [tool output daté])
- [Fait C1] (vérifié dans [...])

## Décisions actées (validées par user le DD/MM/YYYY)
- [Arbitrage tranché 1]
- [Arbitrage tranché 2]

## NON inscrit volontairement (à reconstruire / re-vérifier)
- [Inférence C2 utile — instruction : re-déduire par lecture de X]
- [Détail C3 oublié — instruction : re-vérifier par lecture directe de Y]
- [Hypothèse non sourcée — instruction : escalader à user si nécessaire]

## Action immédiate
[1 phrase concrète : par quoi commencer.]

## Instructions pour la nouvelle session
- Lire impérativement les sources listées avant toute proposition
- Re-vérifier directement la cohérence des faits listés ; pas de confiance aveugle au handoff
- Si point flou ou inférence à trancher : demander via AskUserQuestion, ne pas inférer silencieusement
- Le handoff est un raccourci de contexte, pas un onboarding complet — doctrine driven, cascade Personal OS, conventions globales restent à charger via CLAUDE.md / RULES.md / USER.md habituels
````

### Règles d'écriture

- **Identification** : nom court du projet, pas de jargon technique.
- **Sources à lire en priorité** : 2 à 5 paths / IDs concrets, chacun vérifiable directement par la nouvelle session. La mémoire de session est citée en premier — c'est le pivot de la reprise.
- **Faits 100% certains** : exclusivement du C1. Chaque ligne porte son pointeur source entre parenthèses. Pas de fait sans source. Si pas de pointeur listable → le fait bascule en « NON inscrit volontairement ».
- **Décisions actées** : arbitrages explicitement tranchés par user au cours de la session, avec date si possible. Distinct des faits C1 car porte un acte de validation conversationnelle, pas une vérifiabilité technique d'état du monde.
- **NON inscrit volontairement** : explicite ce qui était candidat mais classé C2 / C3. Sans cette section, la nouvelle session ignore qu'elle hérite d'un contexte tronqué et peut prendre les inférences précédentes pour acquises. Chaque ligne porte une instruction d'action concrète (re-déduire, re-vérifier par lecture, escalader).
- **Action immédiate** : une seule chose à faire en premier. Pas de liste à puces, une phrase concrète.
- **Instructions pour la nouvelle session** : bullets méta d'orientation, pas du contenu. Rappelle que le handoff est un raccourci, pas un onboarding.

### Ce que le prompt ne dit PAS

- Ne ré-explique pas ce que le plugin fait (la nouvelle session le détecte via le frontmatter `space-type` du CLAUDE.md racine).
- Ne liste pas les principes invariants (le plugin les charge automatiquement).
- Ne donne pas le ton ou la voix attendus (le plugin + SOUL.md s'en chargent).
- Ne décrit pas la structure du workspace (le plugin la découvre via lecture-arborescente).
- Ne formule pas d'inférence non sourcée comme fait acquis — C2 va dans « NON inscrit volontairement », pas dans « Faits ».

Le prompt est un **raccourci de contexte vérifiable**, pas un onboarding complet.

## Recap user après wrap-up

Une fois la clôture faite et le prompt généré, recap minimal :

> OK, j'ai mis le récap dans [dossier projet]. Voilà ton prompt de reprise :
>
> [le prompt en code block]
>
> Tu peux copier-coller au démarrage de la prochaine session.

Pas plus. Le user voit la mémoire créée, le prompt prêt, et sait quoi faire ensuite.

## Anti-patterns

- **Forcer la décision** : c'est une proposition, pas une obligation. Si user refuse définitivement, respecter.
- **Inventer une saturation** : si aucun des 4 signaux n'est présent, ne pas proposer. Pas de paranoïa préventive.
- **Prompt verbeux** : > 40 lignes = échec. Lisible en 15 secondes max par user.
- **Wrap-up générique** : la mémoire de récap doit capturer ce qui s'est passé en session de manière factuelle et précise, pas un résumé corporate vague.
- **Mélanger C1 et C2 dans « Faits »** : inscrire une inférence comme un fait crée un drift silencieux dans la nouvelle session. Le tri est strict ; en cas de doute → C2.
- **Fait sans pointeur source** : un fait dans « Faits 100% certains » doit pouvoir être vérifié par la nouvelle session. Si pas de path / Message-ID / URL / ID / output tool listable → ce n'est pas un C1, bascule en « NON inscrit volontairement ».
- **Omettre « NON inscrit volontairement »** : sans cette section, la nouvelle session ignore qu'elle hérite d'un contexte tronqué. La section explicite le trou et donne l'instruction de comblement.
- **Pointeur source vague** (« on en a parlé », « tu m'as dit ») : pas un pointeur. Un pointeur est localisable indépendamment de la session courante.

## Bivalence Code / Cowork

| Aspect | Claude Code | Claude Cowork |
|---|---|---|
| Détection mode routine | Sentinels + ScheduleWakeup tool + section system prompt | Toujours interactif (aucun signal observable) |
| Nouvelle session | `claude` relancé ou nouveau pane terminal | « New chat » dans le Cowork Project |
| Multi-folder préservé | Via `additionalDirectories` du `settings.json` | Via le Project actuel |
| Prompt de reprise | Collé en premier message | Collé en premier message |
| `/compact` disponible | Oui | Oui mais perd la scrollable history (non recommandé) |
| TaskCreate forcing du tri | Tool natif | Tool natif via plugin |
