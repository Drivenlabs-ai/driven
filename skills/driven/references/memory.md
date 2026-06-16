# memory : Création d'une memory entry

Une memory entry est une note timestampée dans un dossier `memory/` à la racine d'un dossier thématique. C'est la mémoire long terme du workspace : décisions, RDV, interactions, insights, contexte projet.

Avant d'écrire une mémoire, le test pivot doit avoir été passé : l'information est un événement révolu ou une décision contextuelle, pas une convention durable. Si c'est vrai demain, c'est un fichier, pas une mémoire (cf `connaissance-vs-memoire.md`).

## Trigger

Activé quand user dit :

- *« retiens ça »*, *« note ça »*, *« garde une trace »*, *« je veux retenir »*
- *« RDV avec X »*, *« j'ai eu un appel »*, *« on a décidé que »*
- Mention spontanée d'un événement business (sans demande explicite de retenir) si le contexte fait sens

## Workflow de création (100 % piloté par Claude)

Le user ne tape jamais le frontmatter. Claude infère silencieusement :

1. **Scope, ancré sur le dossier courant** (`scope-check.md`). Si le dossier courant est un repo git hors workspace driven (projet code), la mémoire va dans sa mémoire native (`memoire-projet-code.md`), même si un espace perso ou partagé est ouvert en parallèle. Sinon, perso vs shared et lequel.
2. **Dossier cible** (workspace driven). Chercher le `memory/` du dossier thématique pertinent (ex `Clients/Acme/memory/`). Si absent → créer le dossier. Si le sujet est transverse → choisir le dossier qui colle le mieux ou demander en NL.
3. **Lecture proactive des dernières mémoires du dossier cible**, par souci de cohérence. Claude juge le volume selon l'activité du dossier :
   - Dossier neuf (< 5 mémoires) → toutes lues.
   - Dossier modéré (5-30 mémoires) → 5 plus récentes (tri lexico = tri chrono).
   - Dossier dense (> 30 mémoires) → 5 plus récentes + search BM25 sur le topic inféré (top 5 hits).
   - Préambule `## Contexte` suffit en général. Lecture du corps si une mémoire semble directement pertinente au sujet.
   - Permet d'enrichir une mémoire existante plutôt que créer un doublon, et de croiser proprement les liens.
4. **`topic`**, kebab-case court (ex `rdv-acme`, `decision-pricing`, `update-positioning`).
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

Exemple : `2026-05-11-1430-jane-rdv-acme.md`.

Tri lexicographique = tri chronologique. Grep par auteur trivial.

**Le nom du fichier est invariant après création**, même quand le doc évolue via cross-author. Seul `authors` dans le frontmatter accumule.

## Append-only

Une memory entry représente un état figé à un instant T. Si l'information évolue, **créer une nouvelle mémoire** qui linke la précédente, pas éditer l'ancienne.

Exemple :

- `2026-05-11-1430-jane-decision-pricing.md`, décision initiale 8K.
- `2026-05-14-0900-jane-revision-pricing.md`, révision à 10K, mémoire avec lien vers la précédente : « Révision de la [décision initiale](2026-05-11-1430-jane-decision-pricing.md). »

L'historique reste lisible. Pas de réécriture qui efface le passé.

## Auto cross-link

Au moment de la création, Claude scanne le voisinage pour les mémoires connexes :

1. Pour chaque entité mentionnée dans la nouvelle mémoire, invoquer `scripts/graph.py explain <entité>` (cf `graphe.md`) : les arêtes entrantes/sortantes donnent les candidats de liens markdown pertinents. À défaut (script indisponible), scan du `memory/` courant pour les mémoires de même `topic` ou mots-clés communs.
2. Insertion de liens markdown standards inline dans le corps `## Notes`.

Pas de section « Liens » dédiée, les liens vivent dans le texte au moment naturel de la mention. Format `[Texte](path/relatif)`. Détail : `references/links.md`.

## Trace des actions de la session

Une mémoire fige un événement et ce qui en a découlé concrètement. Six mois plus tard, le lecteur doit savoir ce qui a été produit, supprimé et envoyé sans rouvrir la session. Une mémoire consigne donc, sans en omettre, les actions conséquentes de la session qu'elle documente :

- **Fichiers du workspace créés ou modifiés pendant la session** (positioning.md, brief.md, devis.xlsx, etc.) → liens markdown inline dans le corps ; format et placement cf `Auto cross-link`.
- **Fichiers supprimés, déplacés ou renommés** → mention factuelle dans le corps : un fichier disparu ne se linke pas, on nomme quoi, et la cible si déplacé.
- **Éléments envoyés ou partagés vers l'extérieur** — mail, message, document partagé, invitation, ou tout autre élément sortant → ligne factuelle dans le corps : l'élément, le destinataire, la date, et un lien vers l'élément s'il a une référence stable (URL Drive, thread). Le contenu envoyé n'est pas recopié verbatim ; seuls l'élément, le destinataire et la référence sont consignés.

Les lectures et recherches sans effet ne sont pas tracées : seules les mutations et les actions sortantes le sont.

En shared space, ces lignes passent le filtre de `factualite.md` comme le reste du corps ; une action sortante y est par nature factuelle (« devis envoyé à john@acme.com le 11/05 »).

## Détection sensibles → routage perso

Avant d'écrire une mémoire dans un dossier shared, Claude vérifie 6 patterns sensibles. Si un pattern est détecté, propose en NL : *« Ce sujet semble sensible (RH, NDA, vie privée). On le met dans ton espace perso plutôt qu'en partagé ? »*

| Pattern | Exemples |
|---|---|
| Jugement RH | « X est sous-performant », « pas la bonne personne au bon endroit », « problème d'attitude » |
| Débauchage | « on pourrait recruter Y de chez Z », « approcher en off » |
| NDA explicite | « entre nous », « off the record », « sous NDA », « confidentiel » |
| Vie privée tiers | mentions de santé, situation familiale, divorce, finances perso d'un tiers |
| Dossier disciplinaire | « avertissement », « licenciement », « procédure » |
| Préférences cachées | salaire, primes individuelles, conditions négociées |

Si user **insiste** pour écrire en shared malgré le pattern, Claude reformule avec **factualité maximale** (« décision prise », pas « X est nul »).

Si user accepte le routage perso : créer la mémoire dans le personal space miroir (path parallèle, ex `~/Personal OS/Clients/Acme/memory/...`).

Cas hybride (info en partie sensible) : extraire la part factuelle vers shared, le reste vers perso, avec lien réciproque.

Couvre le risque légal RGPD pour les déploiements client.

## Avant toute proposition stratégique

Avant que Claude formule une proposition stratégique (« je suggère X », « on pourrait Y »), il consulte `challenge-anti-recidive.md` qui scrute les lessons et mémoires pour détecter si l'user a déjà rejeté ou pivoté sur le sujet. Évite les récidives silencieuses.

## Recap minimal au user

Après écriture, deux lignes maximum :

> OK, j'ai noté ça dans Acme.

Pas de chemin complet, pas de mention du frontmatter, pas de description de la mémoire elle-même. Le user ne doit pas avoir l'impression que la machinerie est lourde, elle ne l'est pas pour lui.

En tech-level haut (cf `verbosity-tech-level.md`), recap peut être un peu plus détaillé :

> OK, ajouté une décision dans `Clients/Acme/memory/` avec liens vers le pricing et le brief.

## Suppression

Pas de cleanup automatique. Une mémoire ne disparaît jamais d'elle-même.

Si user demande explicitement *« supprime cette mémoire »* : confirmer avant suppression (mention du fichier en NL). Si user dit *« corrige le typo dans cette mémoire »* : édition ponctuelle autorisée pour erreur factuelle évidente (date erronée, faute de frappe). Pas de réécriture de fond, utiliser une nouvelle mémoire (append-only).

## Volume et longévité

Une memory entry typique : 5 à 30 lignes (frontmatter compris). Préambule 2-3 phrases. Corps 3 à 8 paragraphes courts. Pas de « tartines », la concision force la factualité.

Si une mémoire dépasse 50 lignes, c'est probablement un document à part entière qui mérite son propre fichier dans le dossier thématique, avec une mémoire courte qui le référence.
