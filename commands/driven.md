---
description: "Maintient un workspace driven, capture, cross-author, propagation, routage, structure. Activé automatiquement dans un workspace dont le CLAUDE.md racine porte space-type dans son frontmatter."
argument-hint: "[intention en langage naturel] | [context | search | explain | path | audit | migrate | setup-doc | setup-dossier | workflow]"
---

# /driven

Point d'entrée du plugin `driven`.

## Routing

Lire `${CLAUDE_PLUGIN_ROOT}/skills/driven/SKILL.md` (skill principal, détection workspace, routing rules, table des references).

Selon l'argument :

- **Aucun argument** → afficher récap contexte courant + actions pertinentes en langage naturel.
- **Nom d'action explicite** → charger la référence correspondante :
  - `context` → récupère le contexte d'un sujet avant de bosser dessus (charge `recuperation-contexte.md`)
  - `search` → recherche mémoire
  - `explain` → fiche d'une entité (liens + mémoires connexes ; charge `graphe.md`)
  - `path` → plus court chemin entre deux entités (charge `graphe.md`)
  - `audit` → audit du workspace
  - `migrate` → migration de structure
  - `setup-doc` → mise en place d'un document normatif
  - `setup-dossier` → mise en place proactive d'un dossier (charge `setup-dossier.md`)
  - `workflow` → sauvegarde le workflow de la session courante (charge `capitalise-workflow.md`)
- **Intention en langage naturel** → inférer action depuis `routage.md` + références pertinentes.

Note : `/driven` est rarement tapé explicitement. Le skill s'active automatiquement dès détection d'un CLAUDE.md racine avec space-type + trigger. Les patterns proactifs setup-dossier et capitalise-workflow s'activent partout, même hors workspace driven.
