# links : Liens markdown standards, jamais de stub

Les liens entre fichiers du workspace sont des liens markdown standards : `[Texte affiché](path/relatif/ou/absolu.md)`. Jamais de wikilinks Obsidian-style `[[Page]]`, jamais de crochets simples `[Page]` sans target.

## Format

```markdown
[Olenbee](Clients/Olenbee/CLAUDE.md)
[la décision pricing](Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md)
[le positioning](Drivenlabs/positioning.md)
```

- Path relatif depuis la racine du workspace par défaut. Path absolu uniquement si cross-workspace (rare).
- L'extension `.md` est explicite, même si elle peut paraître redondante. Mieux supporté par les outils de navigation et les éditeurs.
- Le texte affiché reste naturel : on lit la phrase comme si le lien n'existait pas, et l'underline indique juste la navigation.

## Deux options seulement

Quand une entité est mentionnée dans un document :

### Option A : Pas de lien

Choisi quand la mention est ponctuelle, non-business, ou anecdotique. Exemples :

- « Comme l'a dit John dans son post », John n'a pas de document dans le workspace, le post non plus. Pas de lien.
- « C'était pas mal, à la manière de Tarantino », référence culturelle. Pas de lien.
- « On a regardé l'option Stripe », Stripe a pas de fiche dédiée. Pas de lien.

### Option B : Création réelle du document cible

Choisi quand l'entité est importante et devrait avoir un document propre dans le workspace. Exemples :

- « J'ai rencontré Pierre Martin de chez Acme, prospect intéressant », Pierre Martin et Acme sont des entités business pertinentes. Proposer création de `Contacts/pierre-martin.md` et `Clients/acme/CLAUDE.md` (en langage naturel : *« Je crée des docs pour Pierre Martin et Acme ? »*).
- « Le RDV avec Laurent était sur Olenbee », Olenbee est un client suivi. S'il a déjà un dossier (`Clients/Olenbee/`), lien direct. Sinon, proposer création.

## Anti-pattern absolu : pas de stub

Un stub est un lien vers un fichier qui n'existe pas encore, créé « au cas où ». Exemple à bannir :

```markdown
RDV avec [Pierre Martin](Contacts/pierre-martin.md)
```

…sans que `Contacts/pierre-martin.md` existe. Le lien casse, le fichier n'apparaît pas dans l'index, l'orchestration future fait référence à un fantôme.

**Toujours** : soit créer réellement le document cible, soit ne pas mettre de lien. Si user dit *« je préfère juste mentionner sans créer »*, pas de lien, éventuellement gras pour signaler l'entité (`**Pierre Martin**`).

## Seuil de pertinence

Claude raisonne sur l'importance contextuelle de chaque mention. Quelques heuristiques :

| Signal | Décision |
|---|---|
| Mention d'un client ou prospect actif | Option B si pas déjà documenté |
| Mention d'une personne de l'équipe ou partenaire récurrent | Option B |
| Mention culturelle, anecdotique, référence externe | Option A |
| Mention d'un outil utilisé par Drivenlabs (Lemlist, Dougs, Drive) | Option B uniquement s'il y a déjà un dossier outil dans le workspace |
| Citation d'un post / article / livre externe | Option A (référence textuelle), URL en plain text dans le corps si utile |

En cas de doute, demander en NL :

> Je crée un doc pour Pierre Martin ou je le mentionne juste sans créer ?

## Renommage et propagation

Quand un document lié est renommé, le plugin scanne le workspace pour les liens entrants et les regen automatiquement. Détail : `references/propagation.md`. Le user voit seulement *« j'ai mis à jour les 14 liens vers Olenbee. »*

## Liens vers les mémoires

Liens markdown standards, mêmes règles. Format typique :

```markdown
Voir la [décision pricing du 11/05](Clients/Olenbee/memory/2026-05-11-1430-mael-decision-pricing.md).
```

Texte affiché qui résume + path complet. Lisible dans le corps d'un autre fichier sans lien actif (le résumé textuel donne déjà l'essentiel).

## Liens externes

URLs http(s) en lien standard markdown :

```markdown
[le post LinkedIn de Greg Isenberg](https://www.linkedin.com/posts/...)
```

Pas de raccourci, pas de markdown réflexif (`<url>`). Format identique aux liens internes pour la cohérence visuelle.
