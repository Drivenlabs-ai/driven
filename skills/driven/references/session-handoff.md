# session-handoff : Reprendre la conversation dans une nouvelle session quand elle sature

Une conversation trop longue brouille le contexte et dégrade la précision de Claude. Le plugin détecte proactivement les signaux de saturation et propose à l'user de reprendre dans une nouvelle session, avec une mémoire de récap qui préserve le contexte et un prompt de reprise dense pour relancer rapidement.

## Quand cette ref s'active

Trigger 4 — saturation conversationnelle. Quatre signaux possibles, n'importe lequel suffit :

| Signal | Description |
|---|---|
| Volume échanges | Plus de 40 échanges user dans la conversation courante |
| Tool-heavy | Plus de 10 actions tool-intensives cumulées (Read sur gros fichiers, Bash longs, Agent lancés, etc.) |
| Pluri-sujets | La conversation a couvert 3+ sujets structurellement distincts (ex : pricing Olenbee, puis design Webflow, puis prospection LinkedIn) |
| Agacement user | Phrases : « je m'y perds », « tu te répètes », « c'est bordélique », « fait court », « trop d'infos », « j'ai du mal à suivre », « tu deviens confus » |

Claude n'a pas accès direct au compteur de tokens en Code ni en Cowork. L'estimation est qualitative.

## Exclusion : mode routine

Cette ref **ne s'active jamais en mode routine**. En routine, Claude est un agent autonome qui exécute une tâche et termine — il n'y a pas d'utilisateur en interaction à qui recommander quoi que ce soit, et proposer briserait l'autonomie.

Mode routine détecté en Code via :

- Sentinel `<<autonomous-loop>>` ou `<<autonomous-loop-dynamic>>` dans le prompt initial de la session.
- Tool `ScheduleWakeup` ou `CronCreate` disponible dans la liste des tools.
- Section « Autonomous loop check » ou « Autonomous loop persistence guidance » dans le system prompt.

Mode routine en Cowork : pas de signal observable documenté. Cowork est traité comme toujours interactif. Les scheduled tasks Cowork sont indistinguables d'une session normale côté Claude — accepté comme limitation V1.

## Workflow

### 1. Détection

Claude observe la conversation en continu et juge selon les 4 signaux ci-dessus. Pas de chiffre précis sur le context window. Si un seul signal est présent, déclencher.

### 2. Proposition NL

Une phrase, naturelle, sans jargon :

> Cette conversation devient longue, je commence à perdre en précision. On la fait basculer dans une nouvelle session ? Je te prépare un récap et un prompt pour reprendre rapidement.

Si signal d'agacement détecté, adapter le phrasing :

> Je sens qu'on s'y perd un peu. On reprend dans une nouvelle session avec un récap propre ?

### 3. Si user accepte

a. **Création de la mémoire de récap** dans le `memory/` du dossier projet dominant.

   - Mémoire **standard**, suit `memory.md`. Pas de type spécial.
   - Topic descriptif : `recap-pricing-olenbee`, `recap-design-plugin-driven`, etc.
   - `type` adapté : `decision` si arbitrages tranchés en session, `insight` si apprentissages, `memory` par défaut.
   - Préambule `## Contexte` : 2-3 phrases self-contained résumant ce sur quoi on a travaillé.
   - Corps `## Notes` : décisions prises, actions identifiées, fichiers touchés (liens markdown), locks structurants, anything qui mérite d'être préservé pour la reprise.

b. **Multi-projet** : si la session a touché plusieurs projets distincts, Claude infère le projet dominant (celui qui a concentré l'essentiel des décisions). Si vraiment ambigu, demande NL :

   > On a touché Olenbee et le plugin driven. Je mets le récap dans Olenbee (dominant) ou je split ?

c. **Génération du prompt de reprise** : dense et concis (cf section suivante). Présenté à l'user en fin de message dans un code block, prêt à copier-coller.

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

5 blocs **denses et concis**. Cible : 12-18 lignes max. Le user doit pouvoir le lire en 10 secondes.

```markdown
On reprend [Nom du projet].

## État actuel
[1-2 phrases : où on en est exactement.]

## Documents à charger
- [path/mémoire-récap.md] — état détaillé de la session précédente
- [path/autre-fichier.md] — [raison concise]

## Locks structurants
- [décision verrouillée 1]
- [décision verrouillée 2]

## Action immédiate
[1 phrase concrète : par quoi commencer.]
```

### Règles d'écriture

- **Identification** : nom court du projet, pas de jargon technique.
- **État actuel** : factuel, sans émotion. Phrase nominale acceptable.
- **Documents à charger** : 1 à 3 maximum. Chaque ligne = path + raison ultra-courte. La mémoire de récap est citée en premier — c'est le pivot qui contient le détail.
- **Locks structurants** : 2 à 4 bullets max. Décisions verrouillées critiques pour ne pas re-débattre dans la nouvelle session.
- **Action immédiate** : une seule chose à faire en premier. Pas de liste à puces, une phrase concrète.

### Ce que le prompt ne dit PAS

- Ne ré-explique pas ce que le plugin fait (la nouvelle session le détecte via le marker `.driven`).
- Ne liste pas les principes invariants (le plugin les charge automatiquement).
- Ne donne pas le ton ou la voix attendus (le plugin + SOUL.md s'en chargent).
- Ne décrit pas la structure du workspace (le plugin la découvre via lecture-arborescente).

Le prompt est un **raccourci de contexte**, pas un onboarding complet.

## Recap user après wrap-up

Une fois la mémoire de récap écrite et le prompt généré, recap minimal :

> OK, j'ai mis le récap dans [dossier projet]. Voilà ton prompt de reprise :
>
> [le prompt en code block]
>
> Tu peux copier-coller au démarrage de la prochaine session.

Pas plus. Le user voit la mémoire créée, le prompt prêt, et sait quoi faire ensuite.

## Anti-patterns

- **Re-proposer trop souvent** : strictement 10 échanges entre relances, pas plus serré.
- **Forcer la décision** : c'est une proposition, pas une obligation. Si user refuse définitivement, respecter.
- **Inventer une saturation** : si aucun des 4 signaux n'est présent, ne pas proposer. Pas de paranoïa préventive.
- **Prompt verbeux** : > 25 lignes = échec. Le user doit lire en 10 secondes max.
- **Wrap-up générique** : la mémoire de récap doit capturer ce qui s'est passé en session de manière factuelle et précise, pas un résumé corporate vague.
- **Proposer en mode routine** : violation absolue. Si Claude tourne en /loop, /schedule ou comme sub-agent, jamais de proposition.

## Bivalence Code / Cowork

| Aspect | Claude Code | Claude Cowork |
|---|---|---|
| Détection mode routine | Sentinels + ScheduleWakeup tool + section system prompt | Toujours interactif (aucun signal observable) |
| Nouvelle session | `claude` relancé ou nouveau pane terminal | « New chat » dans le Cowork Project |
| Multi-folder préservé | Via `additionalDirectories` du `settings.json` | Via le Project actuel |
| Prompt de reprise | Collé en premier message | Collé en premier message |
| `/compact` disponible | Oui | Oui mais perd la scrollable history (non recommandé) |
