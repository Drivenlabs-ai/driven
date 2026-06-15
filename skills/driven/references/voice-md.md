# voice-md : Routeur des surfaces et registres d'écriture

`VOICE/` est le système qui gouverne la voix sortante du user (comment il écrit). Vit en personal space. Compose un `VOICE.md` racine qui pointe vers des sous-fichiers thématiques.

## Structure

```
VOICE/
├── VOICE.md                  # Point d'entrée, décrit qui est le user, qui définit la voix
├── voice-perso.md            # Voix générique du user (transverse aux surfaces)
├── surfaces/
│   ├── linkedin.md           # Voix sur LinkedIn (posts publics)
│   ├── site-web.md           # Voix sur le site Drivenlabs / pages produit
│   ├── audit-rapport.md      # Voix pour audits / rapports / restitutions
│   ├── formation-support.md  # Voix pour slides, guides, doc client
│   ├── proposition-commerciale.md  # Voix commerciale (one-pager, brochure, deck)
│   └── guide.md              # Voix pour Substack long, lead magnets
└── registres/
    └── par-contact.md        # Comment le user écrit à chaque contact spécifique
```

Les surfaces sont au choix du user. Pas de liste imposée.

## VOICE.md racine

Point d'entrée. Décrit :

- Qui est le user (1-2 paragraphes, différent de ME.md, ici on parle de la **voix**, pas du contexte business).
- Comment la voix s'incarne (« nous » sur les surfaces marque, « je » sur les surfaces personnelles, etc.).
- Principes invariants (pensée par la pratique, anti-bullshit, loyauté envers le lecteur, etc.).
- Index des surfaces (table avec liens vers `surfaces/<surface>.md`).
- Workflow d'utilisation (« comment l'utiliser », 1. identifier la surface, 2. lire le fichier, 3. lire la fiche contact si destinataire, 4. écrire).

## Fichier surface : pattern

```markdown
# Surface : [Nom]

## Quand l'utiliser
[Conditions d'application : type de contenu, destinataire, contexte.]

## Caractère
[Phrase clé sur le ton attendu, ex « cabinet conseil neutre », « ami compétent
qui partage », « prof posé qui parle à ses élèves ».]

## Principes
[Règles spécifiques à cette surface, ce qu'on fait, ce qu'on évite.]

## Exemples
[Phrases courtes qui incarnent la voix attendue, ou anti-exemples avec correction.]
```

Format au choix. L'essentiel : un lecteur (humain ou Claude) doit pouvoir écrire dans cette surface après lecture du fichier.

## Registres par contact

`VOICE/registres/par-contact.md` documente comment le user écrit à des contacts spécifiques quand ça mérite d'être noté.

Format typique :

```markdown
# Registres par contact

## John Doe (Dentalsoft / Acme)
[Comment Alex écrit à John Doe, registre, niveau de familiarité, sujets sensibles.]

## Jane Doe Mathiot
[Idem.]
```

Mise à jour quand user dit *« avec John Doe, plus direct »* ou similaire. Détail : `maintenance-fichiers-racines.md`.

## Workflow d'utilisation par Claude

Quand Claude doit écrire pour le user :

1. **Identifier la surface**, Claude infère depuis le contexte (post LinkedIn, email, brief client, etc.). Si ambigu, demande NL : *« C'est pour LinkedIn ou un mail ? »*.
2. **Lire `VOICE/surfaces/<surface>.md`**, récupère le caractère, les principes, les exemples.
3. **Lire la fiche contact** si le contenu est destiné à une personne spécifique (via `Contacts/contacts.jsonl` ou équivalent). Détail : `registres/par-contact.md` pour les règles d'arbitrage.
4. **Écrire en exerçant le jugement**, pas une application mécanique des règles, mais une incarnation de la voix.

## Maintenance des surfaces

Quand user dit *« sur LinkedIn préfère du court »*, *« n'utilise plus tel mot dans mes mails »*, etc. :

- Identifier la surface concernée (LinkedIn, mail, etc.).
- Mettre à jour le fichier surface correspondant.
- Maintenance holistique, refonte si la modification touche au caractère global, ajout si c'est un détail compatible avec l'existant. Détail : `maintenance-fichiers-racines.md`.

Validation NL avant modif :

> Je mets ça dans `VOICE/surfaces/linkedin.md`. OK ?

## Override ponctuel

Quand user demande une déviation explicite pendant une session (ex *« là tu tutoie pas, fais sec et factuel »*), appliquer **sans archiver**. La voix par défaut reste la référence.

Si user veut que la déviation devienne permanente, il dit explicitement *« désormais »*, *« toujours »*, *« par défaut »*, alors modifier le fichier surface.

## Mise à jour du voice

Quand user dit *« ajoute ça au voice »* ou *« le voice doit dire ça maintenant »* :

1. Identifier le fichier concerné (surface, voice-perso, ou VOICE.md racine).
2. Proposer un diff en NL (résumé d'intention, pas brut).
3. Attendre approbation explicite.
4. Écrire.

Pas d'écriture directe sans approbation. Le voice est sensible, c'est la voix sortante du user, qui le représente publiquement.

## Anti-pattern : pas de capture sans demande

Pendant une session, Claude n'archive **pas** automatiquement les ajustements ponctuels de voix. *« là, plus court »* = ponctuel, pas une règle. User doit le dire explicitement pour que ça devienne une règle.

## Anti-pattern : voice ≠ SOUL

`VOICE/` = comment le user écrit (contenu sortant).
`SOUL.md` = comment Claude se comporte (interaction).

Si user dit *« sois plus direct avec moi »*, ça va dans SOUL.md. Si user dit *« mes mails commerciaux doivent être plus directs »*, ça va dans `VOICE/surfaces/proposition-commerciale.md`.

Si confusion, demander en NL :

> Tu me dis comment réagir avec toi (j'updaterais SOUL.md) ou comment écrire pour toi (j'updaterais VOICE) ?

## Récap après modif

Deux lignes maximum.

> OK, mis à jour `VOICE/surfaces/linkedin.md` avec la directive sur le court.

Pas de description détaillée. Si user veut voir le diff, il demande.
