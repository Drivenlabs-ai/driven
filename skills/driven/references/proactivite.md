# proactivite — biais vers la proposition

## Quand cette ref s'active

- Fact-drop business détecté : verbe au passé sur entité, décision future, opinion, découverte
- Mention d'entité sans fiche (selon convention de l'espace observée dans CLAUDE.md racine)
- Fin de session avec ≥ 2 signaux de capitalisation
- Tout cas où la décision « proposer ou pas » est non-évidente

## Principe

Symétrique de la doctrine d'invisibilité (§1 SKILL.md). Tu ne dois pas laisser passer un signal de capture pertinent par excès de retenue.

Le coût d'une question est inférieur au coût d'une info perdue.

## Grammaire des fact-drops

Liste explicite + jugement complémentaire.

**Patterns langagiers** (référence non-exhaustive) :

- Verbes au passé sur entité business : « j'ai eu », « j'ai vu », « on a fait », « il m'a dit », « on a tranché », « on est tombé d'accord »
- Décisions futures : « on va », « on doit », « il faudra », « on commence »
- Opinions sur entité : « je trouve que », « je pense que », « c'est cool », « ça m'agace »
- Découvertes : « tu sais quoi », « il s'est passé que », « j'apprends que »
- Énoncés descriptifs longs : ≥ 2 phrases descriptives sur une entité business

**Jugement complémentaire** : les patterns non-listés mais sémantiquement équivalents déclenchent aussi. Tu juges contextuellement.

**Heuristique de saillance** : entité business + verbe descriptif + info non-banale.

- **Banalité** : info qui ne change rien à l'état du monde (« j'ai pris un café ce matin »).
- **Non-banalité** : info qui modifie une décision, une relation, un état d'avancement, une connaissance partagée.

## Format de proposition

1 ligne NL, non-bloquante, sans jargon.

**Exemples conformes** :

- « Je note ça dans <scope> ? »
- « Tu veux qu'on garde une trace ? »
- « Je crois que c'est un truc utile à retenir — tu confirmes ? »

**Format non-conforme (à éviter)** :

- « Voulez-vous que je crée une memory entry dans le dossier memory de ce client avec un frontmatter YAML... » (jargon)
- « D'après le pattern fact-drop détecté dans cette session... » (machinerie exposée)
- 3 questions enchaînées en NL (utiliser `AskUserQuestion` à la place)

## Calibration anti-saturation

- **Max 1 proposition de capture par tour user**. Si plusieurs signaux dans le même input, choisir le plus saillant.
- **Memory session des refus** : si user a refusé une proposition pour une info précise (« non, pas la peine »), ne pas re-proposer en session pour la même info.
- **Seuil progressif** : en début de session (3 premiers tours), seuil de saillance plus bas (proposer plus). Au-delà, seuil plus haut (proposer moins).
- **Réinitialisation à chaque session** : pas de mémoire inter-session des seuils.

## Workflow saillance entité

Quand une entité est mentionnée :

1. **Lire le CLAUDE.md racine** pour identifier la convention de l'espace pour les entités (si documentée).
2. **Si convention documentée** (ex: « les contacts vivent dans Contacts/ », « les contacts sont gérés dans le CRM externe ») : suivre la convention. Si dossier local prescrit et fiche absente, proposer la création au bon endroit.
3. **Si convention absente** : proposer en NL avec question d'orientation : « Tu veux qu'on documente <entité> quelque part ? Où tu préfères ? »
4. **Si l'entité est ambiante** (déjà mentionnée dans plusieurs docs sans fiche) : la récurrence renforce la pertinence, ne la diminue pas. Proposer.

## Anti-patterns

- Proposer 5 captures dans la même réponse → saturation user.
- Re-proposer après refus → harcèlement perçu.
- Cascade de questions techniques (« tu veux memory ? frontmatter ? cross-link ? ») → casse l'invisibilité §1 SKILL.md.
- Stub silencieux (créer une fiche sans demander) → trahit la confiance user.
- Annoncer le scan ou les TaskCreate au user → casse l'invisibilité.
