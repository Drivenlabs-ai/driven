---
description: "Maintient un workspace driven, capture, cross-author, propagation, routage, structure. Activé automatiquement dans un workspace contenant `.driven` à la racine."
argument-hint: "[intention en langage naturel] | [search | audit | migrate | setup-doc]"
---

# /driven

Point d'entrée du plugin `driven`.

## Routing

Lire `${CLAUDE_PLUGIN_ROOT}/skills/driven/SKILL.md` (skill principal, détection workspace, routing rules, table des references).

Selon l'argument :

- **Aucun argument** → afficher récap contexte courant + actions pertinentes en langage naturel.
- **Nom d'action explicite** (`search`, `audit`, `migrate`, `setup-doc`) → charger la référence correspondante.
- **Intention en langage naturel** → inférer action depuis `routage.md` + références pertinentes.

Note : `/driven` est rarement tapé explicitement. Le skill s'active automatiquement dès détection du marker `.driven` + trigger.
