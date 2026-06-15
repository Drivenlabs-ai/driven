# links : Liens markdown standards, jamais de stub

## Quand cette ref s'active

- Mention d'une entité (personne, organisation) dans l'input user avec rôle structurant + contexte business + non-banalité.
- Récurrence d'une entité déjà mentionnée dans plusieurs docs du workspace sans fiche existante.
- Avant toute proposition de création de doc / fiche / référence interne à une entité.
- Doute sur le routage selon convention de l'espace (dossier local vs CRM vs autre).

Les liens entre fichiers du workspace sont des liens markdown standards : `[Texte affiché](path/relatif/ou/absolu.md)`. Jamais de wikilinks Obsidian-style `[[Page]]`, jamais de crochets simples `[Page]` sans target.

## Format

```markdown
[Acme](Clients/Acme/CLAUDE.md)
[la décision pricing](Clients/Acme/memory/2026-05-11-1430-jane-decision-pricing.md)
[le positioning](Drivenlabs/positioning.md)
```

- Path relatif depuis la racine du workspace par défaut. Path absolu uniquement si cross-workspace (rare).
- L'extension `.md` est explicite, même si elle peut paraître redondante. Mieux supporté par les outils de navigation et les éditeurs.
- Le texte affiché reste naturel : on lit la phrase comme si le lien n'existait pas, et l'underline indique juste la navigation.

## Deux options seulement

Quand une entité est mentionnée dans un document :

### Option A : Pas de lien

Choisi quand la mention est ponctuelle, non-business, ou anecdotique. Exemples :

- « Comme l'a dit John Doe dans son post », John n'a pas de document dans le workspace, le post non plus. Pas de lien.
- « C'était pas mal, à la manière d'un grand réalisateur », référence culturelle. Pas de lien.
- « On a regardé l'option Stripe », Stripe a pas de fiche dédiée. Pas de lien.

### Option B : Création réelle du document cible

Choisi quand l'entité est importante et devrait avoir un document propre dans le workspace. Exemples :

- « J'ai rencontré John Doe de chez Acme, prospect intéressant », John Doe et Acme sont des entités business pertinentes. Proposer création de `Contacts/john-doe.md` et `Clients/acme/CLAUDE.md` (en langage naturel : *« Je crée des docs pour John Doe et Acme ? »*).
- « Le RDV avec John Doe était sur Acme », Acme est un client suivi. S'il a déjà un dossier (`Clients/Acme/`), lien direct. Sinon, proposer création.

## Saillance contextuelle

**Règle** : la récurrence d'une entité sans fiche **renforce** la pertinence de la proposition, ne la diminue pas.

Une entité mentionnée pour la 1ʳᵉ fois est un candidat fiche. Une entité mentionnée pour la 5ᵉ fois sans fiche reste un candidat fiche — et avec une pertinence renforcée par la récurrence. Ne pas atténuer par la familiarité contextuelle.

**Workflow** :

1. **Lire le CLAUDE.md racine** pour identifier la convention de l'espace pour les entités (si documentée).
2. **Si convention documentée** (ex : « les contacts vivent dans Contacts/ », « les contacts sont gérés dans le CRM externe ») : suivre la convention. Si dossier local prescrit et fiche absente, proposer la création au bon endroit.
3. **Si convention absente** : proposer en NL avec question d'orientation : « Tu veux qu'on documente <entité> quelque part ? Où tu préfères ? »
4. **Si l'entité est ambiante** (déjà mentionnée dans plusieurs docs sans fiche) : la récurrence renforce la pertinence, ne la diminue pas. Proposer.
5. **Memory session des refus** : si user a refusé pour cette entité dans la session courante, ne pas re-proposer.

**Anti-pattern** : ignorer une entité ambiante (« il l'a déjà mentionnée plusieurs fois, c'est connu ») = saillance inversée. À éviter.

**Voir aussi** : `proactivite.md` (calibration anti-saturation, format de proposition NL, grammaire des fact-drops liée à la mention d'entité).

## Anti-pattern absolu : pas de stub

Un stub est un lien vers un fichier qui n'existe pas encore, créé « au cas où ». Exemple à bannir :

```markdown
RDV avec [John Doe](Contacts/john-doe.md)
```

…sans que `Contacts/john-doe.md` existe. Le lien casse, le fichier n'apparaît pas dans l'index, l'orchestration future fait référence à un fantôme.

**Toujours** : soit créer réellement le document cible, soit ne pas mettre de lien. Si user dit *« je préfère juste mentionner sans créer »*, pas de lien, éventuellement gras pour signaler l'entité (`**John Doe**`).

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

> Je crée un doc pour John Doe ou je le mentionne juste sans créer ?

## Renommage et propagation

Quand un document lié est renommé, le plugin scanne le workspace pour les liens entrants et les regen automatiquement. Détail : `references/propagation.md`. Le user voit seulement *« j'ai mis à jour les 14 liens vers Acme. »*

## Liens vers les mémoires

Liens markdown standards, mêmes règles. Format typique :

```markdown
Voir la [décision pricing du 11/05](Clients/Acme/memory/2026-05-11-1430-jane-decision-pricing.md).
```

Texte affiché qui résume + path complet. Lisible dans le corps d'un autre fichier sans lien actif (le résumé textuel donne déjà l'essentiel).

## Liens externes

URLs http(s) en lien standard markdown :

```markdown
[le post LinkedIn de John Doe](https://www.linkedin.com/posts/...)
```

Pas de raccourci, pas de markdown réflexif (`<url>`). Format identique aux liens internes pour la cohérence visuelle.
