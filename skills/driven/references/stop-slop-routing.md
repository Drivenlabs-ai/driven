# stop-slop-routing : Invoquer `/stop-slop` avant contenu à partage externe

`/stop-slop` est un skill global qui filtre les patterns d'écriture IA et corporate avant un contenu destiné à un audience externe. Le plugin `driven` route vers lui automatiquement quand Claude détecte qu'on produit du contenu de ce type.

## Quand router

Invoquer `/stop-slop` **avant la finalisation** d'un contenu à partage externe :

| Type de contenu | Router ? |
|---|---|
| Post LinkedIn / X (public) | Oui |
| Email commercial / proposition à un prospect | Oui |
| Brief client (livrable Drivenlabs) | Oui |
| Lead magnet PDF | Oui |
| Article Substack / blog | Oui |
| Brochure / one-pager commercial | Oui |
| Slide de pitch deck | Oui (relecture texte) |
| Texte de page web Drivenlabs | Oui |

**Pas router** pour :

| Type de contenu | Pourquoi pas |
|---|---|
| Fichiers normatifs Claude (CLAUDE.md, RULES.md, SOUL.md, etc.) | Pas du contenu à partage externe |
| Memory entries | Internes au workspace |
| Notes personnelles (perso) | Privées |
| Conversations avec Claude | Pas un livrable |
| Code (commentaires, README technique) | Différent registre, `/stop-slop` pas adapté |

## Workflow

1. Claude détecte la production d'un contenu à partage externe (post LinkedIn en rédaction, email commercial draft, etc.).
2. **Avant** la finalisation (avant le « voici la version finale » au user), Claude invoque mentalement `/stop-slop` sur le contenu.
3. `/stop-slop` détecte les patterns slop : phrases creuses, jargon corporate, formulations IA-générique, structure prévisible.
4. Claude reformule les passages problématiques.
5. Présenter au user la version filtrée.

L'invocation peut être :

- **Silencieuse** : Claude applique les principes `/stop-slop` à sa rédaction sans le mentionner. Le user voit juste un contenu propre.
- **Explicite** : Claude dit *« j'ai passé ça au filtre slop »* si tech-level haut et que la mention est utile.

## Slop patterns à filtrer (résumé non exhaustif)

Le détail vit dans le skill `/stop-slop` lui-même. Quelques patterns récurrents :

- « En tant que [rôle] »
- « Dans le paysage actuel »
- « Il est important de noter que »
- « C'est révolutionnaire »
- « Game-changer »
- Structures prévisibles (« 1. Introduction, 2. Développement, 3. Conclusion »)
- Adjectifs vides (« incroyable », « extraordinaire » sans démonstration)
- Phrases qui ne portent aucune information

Le but : que le contenu ressemble à de l'écriture humaine, pas à du « LinkedIn AI bullshit ».

## Voice + stop-slop

L'écriture user passe par deux filtres complémentaires :

1. **VOICE**, incarne la voix du user (caractère, ton, registre). Vit dans `VOICE/`.
2. **stop-slop**, élimine les patterns IA-générique et corporate.

Les deux s'enchaînent : Claude écrit selon VOICE, puis filtre avec stop-slop avant de présenter.

## Différence avec RULE de factualité

| Filtre | Cible |
|---|---|
| `factualite.md` | Contenu **interne** du workspace shared (mémoires, docs internes), élimine jugements, émotions, hors-scope, spéculation |
| `stop-slop` | Contenu **externe** à partager (post, mail, brief client), élimine patterns slop IA-générique |

Les deux peuvent s'appliquer à un même contenu si pertinent (ex : un brief client = à la fois contenu à partage externe et contenu interne du workspace shared). Dans ce cas, les deux filtres s'appliquent.

## Cas hybride

Si user produit un contenu qui sera **à la fois** mémorisé dans le shared et envoyé à un destinataire (ex : email à un client + memory entry de l'échange) :

- Email externe → stop-slop.
- Memory entry → factualité.

Deux passes, deux filtres, deux contenus distincts. Pas de fusion.

## Récap au user

Si invocation silencieuse : aucun recap sur le filtre slop. Le user voit la version finale, propre, sans mention de la mécanique.

Si invocation explicite (rare) : mention en 1 ligne.

> J'ai passé ton post au filtre slop avant de te le rendre.

Pas de description détaillée des changements. Si user veut voir avant/après, il demande explicitement.

## Si `/stop-slop` n'est pas installé

Si le skill global `/stop-slop` n'est pas présent dans l'environnement Claude courant : le plugin `driven` applique mentalement les principes de stop-slop (le skill standard est documenté + simple à intégrer) sans erreur. Pas de blocage par dépendance.

Si user n'a pas `/stop-slop` installé et que Claude le détecte (besoin de filtrage répété) : mention en NL *« tu pourrais installer le skill `stop-slop` pour automatiser ce filtrage »*. Non bloquant.
