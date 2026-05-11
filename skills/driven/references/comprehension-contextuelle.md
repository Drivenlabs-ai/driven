# comprehension-contextuelle : Pré-trigger contextuel avant action

Avant de proposer une action ou un contenu, Claude charge le contexte pertinent : mémoires connexes, fichiers thématiques, fiches contact, etc. Cette pré-trigger contextuel évite que Claude propose ce qu'on a déjà rejeté ou contredise des décisions passées.

## Pourquoi ce pattern

Sans pré-trigger contextuel, Claude raisonne à partir du seul message courant. Conséquences :

- Propose des solutions qu'on a déjà étudiées et écartées.
- Contredit une décision documentée dans une mémoire récente.
- Ignore le contexte business (qui est le destinataire, où en est le projet).
- Refait à zéro un travail déjà bien avancé.

La pré-trigger contextuelle charge l'historique avant d'agir.

## Cas d'usage typiques

### 1. Mention d'un contact

User dit *« j'ai un RDV avec Laurent demain »*. Avant de répondre :

1. Chercher la fiche contact Laurent (dans `Contacts/contacts.jsonl` ou équivalent).
2. Chercher les memory entries où Laurent apparaît (search BM25 ou scan du `memory/` des dossiers business concernés).
3. Charger le contexte projet récent (`Clients/Olenbee/` si Laurent = Olenbee).

Puis répondre avec ce contexte chargé, *« RDV avec Laurent demain, c'est le 4ème sur Olenbee, dernière décision pricing à 8K du 11/05, brief en attente de validation. »*

### 2. Mention d'un sujet stratégique

User dit *« je veux refondre le positioning Drivenlabs »*. Avant de proposer :

1. Lire `Drivenlabs/positioning.md` actuel.
2. Search BM25 sur les memory entries Drivenlabs avec keywords « positioning ».
3. Lire les memory entries pertinentes.
4. Identifier les décisions passées, les itérations, ce qui a été rejeté.

Puis répondre avec ce contexte, pas en partant de zéro.

### 3. Question rétrospective

User dit *« on en était où sur le pack sales ? »*. Trigger direct pour search BM25 :

1. Invoquer `scripts/search_memories.py` avec query `pack sales` + synonymes (sales-pack, offre commerciale, pricing pack, etc.).
2. Lire les préambules des top hits.
3. Restituer l'état actuel à partir des mémoires les plus récentes.

### 4. Suggestion implicite d'un projet existant

User dit *« je veux faire un truc pour aider les PME à choisir leurs outils IA »*. Avant de proposer :

1. Vérifier si un projet équivalent existe déjà (search BM25 keywords « PME outils IA »).
2. Si projet existant trouvé : signaler en NL *« tu avais commencé un truc là-dessus en mars, [lien]. On reprend ou on part autre chose ? »*.
3. Si rien trouvé : proposer la création.

Évite de relancer un travail déjà entamé sans le savoir.

### 5. Avant proposition stratégique

Toute proposition stratégique (positioning, pricing, structure, etc.) sur un sujet déjà abordé → search BM25 d'abord, puis proposition informée par l'historique.

## Workflow du pré-trigger

Étapes types :

1. **Détecter l'élément de contexte**, mention d'un contact, sujet, projet, décision.
2. **Choisir la stratégie de chargement** :
   - Mention de contact → fiche contact + mémoires sur ce contact
   - Mention de sujet stratégique → search BM25 + lecture mémoires + fichiers thématiques
   - Question rétrospective → search BM25 directe
   - Sujet déjà abordé en session → contexte session suffit, pas de re-chargement disque
3. **Charger**, Read + Bash (script search) selon stratégie.
4. **Restituer en synthèse**, pas dump brut du contenu chargé, mais synthèse pertinente.
5. **Agir**, proposer / écrire / décider, informé du contexte.

## Quand ne pas pré-trigger

- Tâche orthogonale à tout contexte existant (« écris-moi un poème »).
- Demande triviale sans enjeu de cohérence (« corrige ce typo »).
- Suite directe d'une conversation en cours où le contexte est déjà chargé.

Le pré-trigger a un coût (temps + tokens). Le déclencher quand la valeur ajoutée est réelle.

## Différence avec `lecture-arborescente.md`

| Pattern | Quand | Volume |
|---|---|---|
| `lecture-arborescente.md` | Exploration d'un dossier nouveau ou rarement visité | CLAUDE.md + 5 mémoires récentes + fichiers pertinents |
| `comprehension-contextuelle.md` | Avant action spécifique (proposition, RDV, refonte) | Ciblé : mémoires + fiches + docs liés au sujet précis |

Ils s'enchaînent souvent : exploration arborescente d'abord pour avoir la vue, puis compréhension contextuelle pour la tâche.

## Restitution en NL

La compréhension contextuelle se rend visible au user dans la synthèse, pas dans la mécanique. Format type :

> RDV avec Laurent demain, 4ème sur Olenbee. Dernière décision : pricing à 8K le 11/05 (cf [mémoire](Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md)). Brief en attente de validation depuis le 9/05. Tu veux qu'on prépare quelque chose ?

Synthétique, factuel, avec liens pour accéder au détail. Pas de description de la machinerie *« j'ai lu 3 mémoires et la fiche contact »*.

## Anti-pattern : sur-charger le contexte

Ne pas charger plus que nécessaire. Une fiche contact + 2-3 mémoires récentes suffit dans la plupart des cas. Pas besoin de lire 20 fichiers pour un sujet ponctuel.

Si la tâche est vraiment ouverte et que beaucoup de contexte est utile : déléguer à un sub-agent (Code uniquement) plutôt que de surcharger la session principale.

## Récap au user

Synthèse contextuelle = le récap implicite. Pas de mention de la mécanique de chargement.

Si user demande *« qu'est-ce que tu as regardé pour me dire ça »*, restituer explicitement :

> J'ai lu la fiche Laurent, les 3 dernières mémoires d'Olenbee, et le brief actuel.

Sinon, silencieux.
