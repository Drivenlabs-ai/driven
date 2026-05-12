# memory : Création d'une memory entry

Une memory entry est une note timestampée dans un dossier `memory/` à la racine d'un dossier thématique. C'est la mémoire long terme du workspace : décisions, RDV, interactions, insights, contexte projet.

## Trigger

Activé quand user dit :

- *« retiens ça »*, *« note ça »*, *« garde une trace »*, *« je veux retenir »*
- *« RDV avec X »*, *« j'ai eu un appel »*, *« on a décidé que »*
- Mention spontanée d'un événement business (sans demande explicite de retenir) si le contexte fait sens

## Workflow de création (100 % piloté par Claude)

Le user ne tape jamais le frontmatter. Claude infère silencieusement :

1. **Scope**, perso vs shared, et lequel. Voir `scope-check.md`.
2. **Dossier cible**, chercher le `memory/` du dossier thématique pertinent (ex `Clients/Olenbee/memory/`). Si absent → créer le dossier. Si le sujet est transverse → choisir le dossier qui colle le mieux ou demander en NL.
3. **Lecture proactive des dernières mémoires du dossier cible**, par souci de cohérence. Claude juge le volume selon l'activité du dossier :
   - Dossier neuf (< 5 mémoires) → toutes lues.
   - Dossier modéré (5-30 mémoires) → 5 plus récentes (tri lexico = tri chrono).
   - Dossier dense (> 30 mémoires) → 5 plus récentes + search BM25 sur le topic inféré (top 5 hits).
   - Préambule `## Contexte` suffit en général. Lecture du corps si une mémoire semble directement pertinente au sujet.
   - Permet d'enrichir une mémoire existante plutôt que créer un doublon, et de croiser proprement les liens.
4. **`topic`**, kebab-case court (ex `rdv-olenbee`, `decision-pricing`, `update-positioning`).
5. **`type`**, `decision` si arbitrage tranché, `interaction` si RDV/call/échange, `insight` si apprentissage ou observation, `memory` par défaut, `other` exceptionnel.
6. **`keywords`**, 5 à 10 mots-clés couvrant variantes + synonymes implicites. Critique pour la recherche BM25 (pondération ×3). Inférés depuis le contenu, pas demandés au user.
7. **Préambule `## Contexte`**, 2 à 3 phrases self-contained. Doit pouvoir être lu isolément 6 mois plus tard.
8. **Corps `## Notes`**, contenu factuel (RULE active en shared, cf `factualite.md`). Brut en perso.

## Naming du fichier

`YYYY-MM-DD-HHMM-author-topic.md`

- `YYYY-MM-DD`, date ISO, ancrée programmatiquement (`date` shell ou équivalent Python).
- `HHMM`, heure compacte 24h, zéro-prefixé (ex `0930`, `1430`).
- `author`, préfixe email primaire du créateur initial (ex `alex` pour `alex@drivenlabs.ai`).
- `topic`, slug kebab-case identique au champ `topic` du frontmatter.

Exemple : `2026-05-11-1430-mael-rdv-olenbee.md`.

Tri lexicographique = tri chronologique. Grep par auteur trivial.

**Le nom du fichier est invariant après création**, même quand le doc évolue via cross-author. Seul `authors` dans le frontmatter accumule.

## Append-only

Une memory entry représente un état figé à un instant T. Si l'information évolue, **créer une nouvelle mémoire** qui linke la précédente, pas éditer l'ancienne.

Exemple :

- `2026-05-11-1430-mael-decision-pricing.md`, décision initiale 8K.
- `2026-05-14-0900-mael-revision-pricing.md`, révision à 10K, mémoire avec lien vers la précédente : « Révision de la [décision initiale](2026-05-11-1430-mael-decision-pricing.md). »

L'historique reste lisible. Pas de réécriture qui efface le passé.

## Auto cross-link

Au moment de la création, Claude scanne le voisinage pour les mémoires connexes :

1. Scan du `memory/` courant pour mémoires sur le même `topic` ou avec mots-clés en commun.
2. Scan du contexte conversationnel pour les fichiers Write/Edit récents pertinents (positioning.md, brief.md, devis.xlsx, etc.).
3. Insertion de liens markdown standards inline dans le corps `## Notes`.

Pas de section « Liens » dédiée, les liens vivent dans le texte au moment naturel de la mention. Format `[Texte](path/relatif)`. Détail : `references/links.md`.

## Détection de sensibles → routage perso

Avant d'écrire une memory entry en shared, vérifier la présence de patterns sensibles :

| Pattern | Exemples |
|---|---|
| Jugement RH / débauchage / compétence d'un décideur | « X est moins compétent que », « on pourrait débaucher Y », « Z est sur le départ » |
| NDA / confidentialité explicite | « entre nous », « off the record », « ne pas partager », « sous embargo », « NDA en cours » |

Si détecté, ne pas écrire en shared sans demander. Proposer en NL :

> Ce sujet semble délicat, on garde ça dans l'espace perso ?

Si user accepte : créer la mémoire dans le personal space miroir (path parallèle, ex `~/Personal OS/Clients/Olenbee/memory/...`). Si user refuse : écrire en shared avec rigueur factuelle maximale (cf `factualite.md`).

Cas hybride (info en partie sensible) : extraire la part factuelle vers shared, le reste vers perso, avec lien réciproque.

## Recap minimal au user

Après écriture, deux lignes maximum :

> OK, j'ai noté ça dans Olenbee.

Pas de chemin complet, pas de mention du frontmatter, pas de description de la mémoire elle-même. Le user ne doit pas avoir l'impression que la machinerie est lourde, elle ne l'est pas pour lui.

En tech-level haut (cf `verbosity-tech-level.md`), recap peut être un peu plus détaillé :

> OK, ajouté une décision dans `Clients/Olenbee/memory/` avec liens vers le pricing et le brief.

## Suppression

Pas de cleanup automatique. Une mémoire ne disparaît jamais d'elle-même.

Si user demande explicitement *« supprime cette mémoire »* : confirmer avant suppression (mention du fichier en NL). Si user dit *« corrige le typo dans cette mémoire »* : édition ponctuelle autorisée pour erreur factuelle évidente (date erronée, faute de frappe). Pas de réécriture de fond, utiliser une nouvelle mémoire (append-only).

## Mémoires liées à des fichiers session (Code spécifique)

Quand une mémoire référence des fichiers édités dans la même session (ex `Drivenlabs/positioning.md` mis à jour pendant le RDV documenté), les inclure dans les liens markdown du corps. La traçabilité avant-après reste lisible plus tard.

## Volume et longévité

Une memory entry typique : 5 à 30 lignes (frontmatter compris). Préambule 2-3 phrases. Corps 3 à 8 paragraphes courts. Pas de « tartines », la concision force la factualité.

Si une mémoire dépasse 50 lignes, c'est probablement un document à part entière qui mérite son propre fichier dans le dossier thématique, avec une mémoire courte qui le référence.
