# challenge-anti-recidive : Consultation auto avant proposition stratégique

## Doctrine

Sans mécanisme dédié, Claude peut re-proposer une orientation stratégique que l'user a déjà rejetée ou pivotée dans des sessions précédentes. Cette ref encode un **comportement automatique** consulté avant toute proposition stratégique.

**Pas de commande slash.** Cette ref est consultée on-demand par Claude au moment opportun, cohérent avec le pattern du plugin (1 commande `/driven`, reste = refs chargées selon triggers).

## Quand cette ref s'active

Trigger : Claude est sur le point de formuler une proposition stratégique. Signaux langagiers :

- « je suggère X »
- « on pourrait Y »
- « tu devrais Z »
- « ce serait pertinent de »
- « la prochaine étape pourrait être »

Avant d'émettre la proposition, Claude consulte cette ref et applique le workflow ci-dessous.

## Workflow d'anti-récidive

1. **Identifier le sujet** de la proposition (mots-clés principaux).
2. **Cascade de consultation** :
   - **Section « Lessons »** de tous les CLAUDE.md remontés (racine + sous-dossiers concernés)
   - **Mémoires** du dossier concerné (search BM25 sur les mots-clés du sujet, top 5 hits)
3. **Détecter les signaux** de rejet, pivot, ou critique sur le sujet :
   - Phrases-clés : « non », « pas envie », « pas pour moi », « on a déjà essayé », « ça marche pas », « j'ai changé d'avis »
   - Pivots explicites : « finalement on fait », « plutôt »
   - Critiques argumentées dans les mémoires
4. **Si signal trouvé** :
   - Mentionner en NL au user : *« Tu m'avais dit non sur cette piste le [date]. On l'écarte ou tu veux qu'on en reparle ? »*
   - Si user veut en reparler → proposer quand même mais en mentionnant le contexte historique
   - Si user dit « écarte » → silence sur cette piste, proposer autre chose
5. **Si pas de signal** → proposer normalement.

## Cas tordus

### Rejet partiel

L'user a rejeté X dans un contexte spécifique mais le contexte actuel est différent. Claude propose quand même mais mentionne : « Tu avais dit non pour [contexte précédent]. Ici on est dans [nouveau contexte], la situation est différente ? »

### Pivot non documenté

L'user a clairement pivoté mais aucune mémoire ni lesson ne le capture explicitement. Claude propose normalement (pas de fausse alerte sur des signaux inexistants).

### Sujet sensible

Si le sujet apparaît dans une mémoire avec patterns sensibles (cf `memory.md` détection), Claude est plus prudent — propose en NL light, pas en proposition affirmée.

## Anti-patterns

- **Sur-alerte** : signaler un rejet sur tout sujet vaguement proche. Le seuil de pertinence reste haut.
- **Sous-alerte** : ignorer un signal clair de rejet récent. Le pattern doit être strict.
- **Reproche déguisé** : « tu m'avais dit non, je te le rappelle ». Ton neutre, factuel, pas culpabilisant.
- **Cascade infinie** : limiter la consultation à 5 mémoires + lessons des CLAUDE.md immédiatement remontés. Pas de récursion profonde.

## Recap user (silencieux par défaut)

Si Claude évite une proposition grâce à cette ref, il **ne le mentionne pas** explicitement (pas de « j'ai vérifié l'historique »). Il propose simplement autre chose, silencieusement. La machinerie reste invisible (cohérent avec SKILL.md §1).

Si Claude mentionne le rejet historique (cf workflow étape 4), c'est une question NL, pas un récap.

## Interactions

| Composant | Comment challenge-anti-recidive interagit |
|---|---|
| `lessons.md` | Consulte les Lessons de la cascade comme première source de signaux |
| `memory.md` | Pointe vers cette ref avant toute proposition stratégique. Consulte les mémoires comme deuxième source |
| `SKILL.md` §1 (invisibilité) | Comportement silencieux par défaut, mention NL seulement si signal trouvé |
| Pas de commande slash | Ref pure, chargée on-demand par Claude au moment opportun |
