# soul-md : Posture Claude vis-à-vis du user

`SOUL.md` (en personal space, racine ou `~/.claude/SOUL.md` global) définit comment Claude se comporte avec ce user spécifique : ton, niveau de challenge, garde-fous anti-complaisance, anti-patterns.

## Distinction SOUL ↔ ME ↔ VOICE

| Fichier | Contenu |
|---|---|
| `ME.md` | Qui est le user, son business, son contexte |
| `SOUL.md` | Comment **Claude** se comporte avec ce user |
| `VOICE/` | Comment le **user** écrit (surfaces, registres) |

Trois rôles distincts. Ne pas mélanger.

## Structure typique

Pas de pattern imposé. Sections fréquentes (à composer selon le besoin user) :

```markdown
# SOUL : Posture Claude

## Core Truths
[Principes fondamentaux : exécute ET challenge, pense top 0.1%, signal > bruit, etc.]

## Voice & Tone
[Tonalité attendue : concis, direct, anti-corporate, tutoiement, etc.]

## Anti-patterns avec [user]
[Liste des comportements à éviter : sycophantie, blabla, politesses excessives, etc.]

## Continuity / Boundaries
[Cadres : ce qui reste privé, quand demander, etc.]
```

À adapter au user. La structure n'est pas figée, l'essentiel est qu'elle aide Claude à incarner la posture attendue.

## Divergence assumée vs OpenClaw

Certains systèmes (OpenClaw notamment) mettent le **profil pro** du user dans SOUL.md. Ici, divergence assumée :

- Profil pro et identité user → `ME.md`.
- Posture Claude → `SOUL.md`.

Cohérent avec la séparation des rôles. Évite que SOUL.md devienne un mix identité/posture, deux choses qui évoluent différemment.

## Maintenance holistique critique

SOUL.md est **le** fichier où la maintenance holistique compte le plus. Les inputs user sont souvent de la forme *« tu es trop X »* / *« sois moins Y »* → refonte plutôt qu'ajout. Le risque sans refonte : une accumulation de directives de ton contradictoires (cf `maintenance-fichiers-racines.md`).

Pattern attendu — refonte holistique chaque fois qu'un input modifie le ton :

```
[SOUL.md, refondu]

## Voice & Tone

Ton neutre et précis. Pas familier, pas distant. Direct au point.
Tutoiement par défaut. Pas de politesses superflues.
```

## Garde-fous anti-complaisance

Pattern fréquent dans SOUL.md : forcer Claude à challenger plutôt qu'à acquiescer.

Exemples de directives anti-complaisance :

- *« Quand je propose une idée mauvaise, dis-le. »*
- *« N'ouvre pas tes réponses par "Excellent !" ou similaire. »*
- *« Si tu n'es pas sûr, dis "je sais pas" plutôt que d'inventer. »*
- *« Challenge mes assumptions, ne les valide pas par défaut. »*

Ces directives sont **structurelles**, elles définissent comment Claude raisonne. À traiter comme du ton/voix : refonte holistique aux modifications.

## Garde-fous anti-jargon

SOUL.md peut documenter le vocabulaire à éviter avec ce user. Mais attention : si le bannissement de mots est très spécifique à une surface (LinkedIn, mails, brief), ça va dans `VOICE/surfaces/<surface>.md`, pas dans SOUL.md.

SOUL.md = comportement transverse. VOICE = comportement par surface.

## Validation avant modif

Toute modification de SOUL.md déclenche validation explicite en NL :

> Je mets ça dans SOUL.md. OK ?

Si la modification est une refonte (et pas un ajout), présenter le résumé d'intention :

> Je propose de refondre la section Voice & Tone pour qu'elle dise plutôt [résumé en 2-3 phrases]. OK ?

User valide l'intention, Claude écrit. Détail : `maintenance-fichiers-racines.md`.

## Anti-micromanagement

Une règle ne s'ajoute à SOUL.md que si user le demande explicitement et durablement. Pas d'extrapolation d'une demande ponctuelle en règle générale.

Exemple, user dit pendant une session : *« là, fais court »*. C'est une demande ponctuelle pour cette session. Ne pas l'écrire dans SOUL.md à moins que user dise *« désormais, fais toujours court »*.

L'absence de règle = état neutre. Si user dit *« retire ce que j'avais dit sur les emojis »*, le fichier final ne mentionne plus du tout les emojis.

## SOUL global vs SOUL local

Claude peut avoir un `SOUL.md` global (`~/.claude/SOUL.md`) qui s'applique partout, et un `SOUL.md` local (dans le personal space ou shared) qui spécifie pour ce workspace.

Hiérarchie :
- Global d'abord.
- Local ensuite (override ou complète).

Si conflit explicite entre global et local : local gagne (proximité contextuelle). Si user veut une règle universelle, mettre dans global. Si spécifique à un projet ou un shared, mettre dans local.

Le plugin `driven` raisonne sur le SOUL local du workspace courant en priorité.

## Récap après modif

Deux lignes maximum.

> OK, j'ai refondu le ton de SOUL.md pour être plus neutre.

Pas de description du diff. Si user veut voir les changements, il demande.
