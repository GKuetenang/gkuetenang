# AGENTS.md — Règles obligatoires du projet `gkuetenang`

> **Périmètre :** ce dépôt et ses sous-répertoires. Destiné à Codex et aux autres assistants de développement.
> **Statut :** contrat technique et de qualité. À appliquer avant toute analyse, modification, génération de code ou revue.
> **Version du document :** 1.0 — 27 octobre 2026.
> **Langue :** échanges et documentation fonctionnelle en français ; identifiants de code, noms de classes/fonctions, docstrings et messages de commit cohérents avec les conventions existantes du dépôt (anglais par défaut).

## 0. Priorités, certitudes et règles d'arbitrage

- **OBLIGATOIRE (MUST)** : respecter les instructions de sécurité de la plateforme, puis la demande explicite de l'utilisateur, puis ce fichier, puis les conventions observées dans le dépôt. Si une demande met la sécurité ou des données à risque, expliquer le conflit et proposer la solution sûre. Ne jamais inventer une vérification ou masquer un conflit.
- **INTERDIT (MUST NOT)** : supposer qu'une dépendance, une API, un module, une configuration, un modèle ou une route existe sans l'avoir observé dans le dépôt.
- **OBLIGATOIRE** : lire le code et les fichiers pertinents **avant** de le modifier. Ne pas substituer une réécriture complète à un changement ciblé.
- **OBLIGATOIRE** : respecter les versions verrouillées et les API documentées de **ces** versions, pas celles d'une version antérieure, future ou `latest`.
- **OBLIGATOIRE** : séparer explicitement dans toute réponse les éléments **observés**, **vérifiés dans la documentation**, **inférés**, **non vérifiés**.
- Les règles **MUST / MUST NOT / SHOULD / MAY** signifient respectivement : obligation / interdiction / préférence forte à justifier si écart / option.
- **Pas de fausse garantie** : ne jamais prétendre qu'une implémentation est « totalement sécurisée », « conforme à tous les standards », « testée » ou « prête pour production » sans preuves appropriées.

## 1. Inventaire technique et source de vérité

| Couche                  | Choix imposé ou connu                             | Politique de version                                                                   |
| ----------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Projet et module Django | `gkuetenang` ; module `gkuetenang`                | Vérifier `manage.py`, `settings`, `asgi.py`, `urls.py` avant import/commande           |
| Framework               | **Django 6.1.2**                                   | Version exacte issue de `uv.lock`; ne pas migrer vers une autre version sans accord    |
| Python                  | **Python 3.13.x**                                 | Valeur exacte tirée de `.python-version`, `pyproject.toml`, Docker et environnement    |
| Dépendances Python      | **Astral `uv`**                                   | `pyproject.toml` + `uv.lock` font autorité ; `uv add`, `uv sync`, `uv run`             |
| Serveur ASGI            | **Uvicorn**, si confirmé dans le déploiement réel | Exécuter `gkuetenang.asgi:application` ; vérifier config existante                     |
| Frontend                | **Tailwind CSS v4** + templates Django            | Version installée à lire dans `pnpm-lock.yaml`                                         |
| Dépendances JS          | **pnpm**                                          | `package.json` (`packageManager`) + `pnpm-lock.yaml`                                   |
| UI                      | Variables sémantiques du thème Tailwind / shadcn  | `:root`, `.dark`, `@theme inline` : source de vérité                                   |
| Données                 | **PostgreSQL 17** ; **Redis 7**                   | Versions réelles confirmées dans `compose.yaml` / images épinglées                     |
| Tâches                  | **Celery** avec Redis                             | Version réelle lue dans `uv.lock`                                                      |
| Emails                  | **django-post-office** + Celery                   | Version réelle lue dans `uv.lock`; templates gérés via Django Admin si déjà configurés |
| Conteneurs              | Docker multi-stage + Docker Compose               | Images et chemins réels tirés de `Dockerfile`/`compose.yaml`                           |

**Distinction impérative :** `uv` est le gestionnaire de dépendances Python ; **`uvicorn` n'est pas un substitut à `pip`**, mais un serveur ASGI. Ne jamais produire une commande du type `uvicorn add ...`.

**Inconnues intentionnelles :** les numéros micro exacts de Django/Python, les versions de `uv`, Uvicorn, Celery, Post Office, pnpm et Tailwind ne sont **pas attestés ici**. Une IA doit les extraire des manifestes et lockfiles réels, et non les inventer. Si aucun verrouillage n'est présent, signaler le manque et solliciter une décision avant d'ajouter/mettre à niveau un paquet.

### Ordre de consultation avant toute implémentation

1. `AGENTS.md` et éventuels `AGENTS.md` plus proches du fichier ciblé.
2. `README.md`, `pyproject.toml`, `uv.lock`, `.python-version`, `package.json`, `pnpm-lock.yaml`.
3. `manage.py`, `gkuetenang/settings*.py`, `gkuetenang/asgi.py`, `gkuetenang/celery.py`, `core/` et templates concernés.
4. `Dockerfile`, `compose.yaml`/`docker-compose.yml`, `.dockerignore`, `.env.example`, `Makefile` et CI.
5. Tests, migrations, services et conventions en place.
6. Documentation officielle **versionnée**, seulement après identification de la version installée.

## 2. Processus obligatoire pour toute tâche

**AVANT LE CODE**

1. Reformuler le besoin en une phrase et identifier les fichiers, acteurs, entrées/sorties, risques et critères d'acceptation.
2. Chercher les implémentations réutilisables et l'API existante ; vérifier les fichiers et le schéma de données.
3. Identifier les versions, compatibilités, docs officielles et hypothèses non résolues.
4. Pour une tâche multi-fichiers ou sensible, présenter un bref plan et les impacts ; demander accord pour toute rupture de contrat, migration destructive, nouvelle dépendance, modification de production ou changement d'architecture.
5. Ne pas élargir arbitrairement le périmètre. Pas de refactorisation non sollicitée.

**PENDANT LE CODE**

1. Implémenter la plus petite solution maintenable, sûre et conforme au style du dépôt.
2. Ajouter ou adapter des tests qui reproduisent le besoin et les cas d'échec/abus pertinents.
3. Vérifier les impacts sur accessibilité, sécurité, performance, i18n, emails, assets et configurations.
4. Ne pas masquer des erreurs avec des exceptions trop larges, commentaires trompeurs, `# noqa` injustifiés ou tests désactivés.
5. Aucun changement de dépendance ou mise à jour de lockfile non demandé et non motivé.

**APRÈS LE CODE**

1. Exécuter les vérifications possibles du §12 ; ne pas inventer leurs résultats.
2. Inspecter le diff et signaler les changements non prévus.
3. Livrer un résumé bref : fichiers modifiés, choix techniques et sources, tests **exécutés avec résultats**, tests non exécutés avec raison, limites/risques restants.
4. Si un outil, un secret, une base ou un service manque, le déclarer ; ne pas simuler un succès.

## 3. Architecture Django 6.1.2

- Utiliser d'abord les primitives natives et documentées **Django 6.1.2** : formulaires, validators, ORM, `reverse`/`{% url %}`, transactions, services réutilisables et templates.
- Respecter les responsabilités : `forms.py` pour validation, `views.py` pour coordination HTTP, services/mailers pour opérations métier et intégrations, `models.py` pour persistance, `tasks.py` pour travail asynchrone **nécessaire**.
- Ne pas introduire de framework API, service layer, repository pattern, bibliothèque UI ou abstraction « magique » sans besoin clair. Préférer le code explicite, lisible et typé lorsque pertinent.
- Ne pas bloquer des vues async avec des opérations sync ; vérifier les API async/sync réellement disponibles. Ne pas convertir des vues sync en async par effet de mode.
- Conserver les noms de routes, de templates et les contrats des formulaires existants. Les nouveaux chemins doivent suivre l'arborescence **observée**, non une structure imaginaire.
- Les migrations sont versionnées ; **jamais** de modification rétroactive de migrations appliquées ni de suppression/renommage de données sans plan de compatibilité et sauvegarde vérifiée.
- Éviter les N+1 (`select_related`, `prefetch_related` selon besoin), paginer les listes, borner les requêtes coûteuses ; n'ajouter index/optimisations qu'après justification.
- Paramétrer toute requête SQL ; privilégier l'ORM. `RawSQL`/SQL brut seulement si justifié, sécurisé et couvert par tests.
- Éviter la logique métier complexe dans les templates et les signaux implicites non documentés.

## 4. Conventions spécifiques au portfolio

- Finalité : portfolio professionnel **développeur Full-Stack** (front-end et back-end). **Ne pas présenter le propriétaire comme prestataire de design UI/UX**, ni inventer parcours, diplômes, années d'expérience, chiffres de projets ou témoignages.
- Pages principales : **Accueil, À propos, Services, Réalisations, Contact** ; composants réutilisables par `{% include %}`.
- Pour la page À propos, respecter, si ces fichiers existent, les chemins EXACTS demandés :
  - `core/about/hero_section.html`
  - `core/about/carrer_path_section.html` (**orthographe conservée intentionnellement**)
  - `core/about/values_section.html`
- Les chemins `core/services/...`, `core/contact/...` et des emails `core/emails/...` doivent être vérifiés avant usage, sans duplications arbitraires.
- Conserver la présentation éditoriale premium et épurée : grandes typographies, espaces généreux, hiérarchie explicite, responsive ; Hero d'accueil sans image ; pas d'ajout de sections, de CTA ou de champs non demandés.
- Formulaire Contact **exactement** : nom complet, email, sujet, message. Aucun champ budget, choix de prestation ou CTA de bas de page sauf demande explicite.
- Réalisations : n'utiliser que des projets réels validés. Les exemples fictifs doivent être clairement marqués comme maquettes et **jamais** présentés comme références professionnelles.

## 5. Tailwind CSS v4 et thème — discipline stricte

- **MUST** employer Tailwind CSS v4, les utilitaires existants et les **tokens sémantiques** du thème. Ne jamais hardcoder des couleurs dans le HTML ou les composants.
- **MUST NOT** : `bg-[#... ]`, `text-[#...]`, `border-[#...]`, `style="color: ..."`, blocs `<style>` locaux, styles personnalisés dans les templates, CDN Tailwind en production.
- **MUST** : utiliser `bg-background`, `text-foreground`, `bg-card`, `text-card-foreground`, `text-primary`, `bg-primary`, `text-primary-foreground`, `text-muted-foreground`, `border-border`, `text-highlight` selon leur sens. Les noms doivent exister dans le `@theme inline` réel.
- **MUST** : conserver l'architecture `:root` / `.dark` / `@theme inline` et le fonctionnement du changement de thème sans ajouter de couleurs isolées dans les composants.
- Identité : violet de marque `#765CF1`, navy profond `#121726` en sombre, crème `#F7F7F3`, vert `#B7F297` **uniquement en accent ponctuel pour des titres** (via le token `highlight`, adapté au contraste clair/sombre). Les HEX ne sont admis **que dans le fichier de thème central**.
- Les dimensions arbitraires Tailwind (`lg:grid-cols-[...]`, etc.) sont admises si nécessaires au layout, jamais pour contourner les tokens de couleur.
- **MUST** : respecter les styles focus visibles, états hover/disabled, labels, contrastes accessibles, tailles de cibles tactiles, navigation clavier et préférences `prefers-reduced-motion`.
- **SHOULD** : HTML sémantique, SVG accessibles, assets optimisés, images correctement dimensionnées, chargement différé sous la ligne de flottaison, aucun JS inutile ; pas de dépendance supplémentaire sans justification.
- N'utiliser `pnpm` pour installer et compiler les assets ; ne pas ajouter npm, yarn, bun ou de lockfile parallèle.
- **Exception explicite** : les **emails HTML** exigent fréquemment tableaux et styles inline pour la compatibilité des clients de messagerie ; ils ne doivent pas dépendre du CSS du site ou de Tailwind à l'exécution.

## 6. Sécurité applicative — exigences bloquantes

Appliquer une approche adaptée au risque inspirée d'**OWASP ASVS 5.0.0**, en complément du guide officiel Django 6.1 ; ne pas prétendre être certifié ASVS sans audit.

### Entrées, sorties et accès

- **MUST** valider toutes les entrées au niveau serveur (types, tailles, plages, normalisation, encodage). La validation HTML du navigateur n'est jamais suffisante.
- **MUST** conserver auto-escaping Django ; **MUST NOT** utiliser `mark_safe`, `|safe`, `autoescape off`, rendu HTML non fiable, interpolation SQL ou `eval` sur des entrées utilisateur sans revue de sécurité et besoin explicite.
- **MUST** vérifier permissions et propriété des ressources **côté serveur**. Une interface masquée n'est pas une protection.
- **MUST** garder `CsrfViewMiddleware` et `{% csrf_token %}` dans les formulaires POST ; ne pas utiliser `@csrf_exempt` comme contournement.
- **MUST** valider les redirections et URLs externes ; aucune redirection ouverte, exécution de shell ou accès réseau arbitraire sur saisie utilisateur.
- **MUST** éviter l'exposition des traces détaillées, clés, PII, tokens ou identifiants dans les réponses, logs, analytics et messages d'erreur.
- **MUST** refuser par défaut les uploads dangereux et contrôler strictement type, taille, stockage et autorisation si des uploads sont ajoutés.

### Formulaire contact et emails

- **MUST** prévoir anti-spam et limitation de débit **côté serveur** par utilisateur/IP avec respect des proxies fiables ; ne pas exposer un relais SMTP ouvert.
- **MUST** utiliser une adresse expéditrice maîtrisée (`DEFAULT_FROM_EMAIL`) et l'adresse du visiteur en `Reply-To`, jamais un `From` arbitraire fourni par l'utilisateur.
- **MUST** limiter la taille et neutraliser les sauts de ligne/injections d'en-têtes dans les champs email/sujet ; échapper les contenus HTML rendus.
- **MUST** distinguer **message accepté/enregistré** de **message réellement livré par SMTP** ; un affichage de succès ne prouve pas la livraison.
- **MUST** tester l'échec de mise en queue, la double soumission, les erreurs de validation, le rate limiting, et la confidentialité des données.
- **MUST** utiliser le modèle Post Office existant (`contact` = notification interne ; `notification` = accusé de réception au visiteur) s'il est configuré. Ne pas créer en parallèle une seconde chaîne d'envoi ou deux files concurrentes.
- **MUST** préserver les modifications des templates faites dans Django Admin ; ne pas écraser les entrées en base sans demande et sauvegarde explicites.
- **SHOULD** définir une politique de conservation/suppression des coordonnées et messages ; restreindre accès à Django Admin et privilégier les logs non sensibles.

### Secrets, authentification et transport

- **MUST NOT** demander d'imprimer, copier dans un fichier de code, logger, versionner, partager ou inventer des secrets. Utiliser variables d'environnement / gestionnaire de secrets et `.env.example` sans valeurs réelles.
- **MUST** `DEBUG=False` en production ; `SECRET_KEY` fourni de façon sécurisée, `ALLOWED_HOSTS` explicites, `CSRF_TRUSTED_ORIGINS` limité à des origines fiables.
- **MUST** assurer HTTPS de bout en bout et configurer correctement `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS selon le déploiement et le reverse proxy ; ne jamais ajouter `SECURE_PROXY_SSL_HEADER` sans vérifier le proxy de confiance.
- **MUST** considérer CSP native **Django 6.1** (`django.middleware.csp.ContentSecurityPolicyMiddleware`, `SECURE_CSP`/`SECURE_CSP_REPORT_ONLY`) ; élaborer/tester la politique pour les ressources effectivement utilisées. Ne pas autoriser `unsafe-inline`/`unsafe-eval` par facilité.
- **MUST** contrôler les permissions Django Admin et prévoir MFA/protection anti-bruteforce au niveau adapté au contexte.
- **MUST** ne pas utiliser de `ALLOWED_HOSTS=['*']`, ne pas désactiver les protections de cookies/CSRF/CSP pour « réparer » un test.
- **MUST** respecter la minimisation des données personnelles : collecter seulement le nécessaire et ne pas réafficher de messages privés dans les pages publiques.

## 7. Celery, Post Office, Redis et PostgreSQL

- **MUST** conserver Redis comme broker si c'est la configuration du dépôt ; ne pas exposer Redis ou PostgreSQL publiquement.
- **MUST** garantir l'idempotence lorsqu'une tâche peut être rejouée, et expliciter les conséquences de retries/acks tardifs. Tester les doublons et les pannes transitoires.
- **MUST** utiliser `transaction.on_commit(...)` lorsqu'un travail asynchrone dépend de données créées dans une transaction encore ouverte, selon les API compatibles réellement installées.
- **MUST** séparer transactions DB, opérations réseau et tâches longues ; timeouts, retries bornés, backoff quand pertinent. Ne pas mettre des identifiants secrets ou des données sensibles inutiles dans les arguments Celery.
- **MUST** valider les paramètres Post Office et la version **installée** avant d'écrire des réglages spécifiques ou de déduire le nom d'une tâche. Pas d'hypothèse sur l'API de Post Office.
- **MUST** éviter la duplication de jobs périodiques : au plus une instance active du scheduler Celery Beat selon l'architecture établie.
- **MUST** préserver et tester les migrations PostgreSQL, la restauration des sauvegardes, et traiter les changements de schéma comme potentiellement destructifs.

## 8. Installation, commandes et dépendances

- **Python :** utiliser exclusivement `uv add <package>`, `uv remove <package>`, `uv sync`, `uv run ...` pour ce projet. Ne pas proposer `pip install`, `pip freeze`, Poetry ou Pipenv.
- **JS :** utiliser exclusivement `pnpm add`, `pnpm remove`, `pnpm install --frozen-lockfile`, `pnpm run <script>` ; ne jamais créer `package-lock.json` ou `yarn.lock`.
- **MUST** versionner `uv.lock` et `pnpm-lock.yaml` ; interdire les versions flottantes ou mises à jour accidentelles durant une réparation hors périmètre.
- **MUST** lire `package.json` avant de proposer `pnpm run dev`/`pnpm run build` (ces scripts doivent réellement exister).
- **MUST** consulter `.python-version` et `requires-python` avant toute modification de Python ; ne jamais modifier silencieusement le runtime.
- **MUST** vérifier les changelogs et compatibilités pour tout ajout/mise à niveau de dépendance ; proposer la plus petite modification nécessaire avec justification, versions et risques.
- **MUST** signaler toute vulnérabilité connue affectant les versions verrouillées et proposer une correction **sans installer ou upgrader silencieusement**.

### Commandes de référence (si fichiers/outils présents)

```bash
uv lock --check
uv sync --locked
uv run python manage.py check
uv run python manage.py test
uv run python manage.py check --deploy  # avec les settings/env de production, sans secrets exposés
pnpm install --frozen-lockfile
pnpm run build                 # uniquement si le script existe
docker compose config --quiet
```

Les outils `ruff`, `pytest`, `bandit`, `pip-audit`, `mypy`, `django-stubs`, `pre-commit` et linters JS sont **optionnels et conditionnés à leur présence** dans les manifestes ou la CI. Ne pas prétendre qu'ils sont installés.

## 9. Docker et déploiement

- **MUST** utiliser des builds reproductibles (images/version compatibles explicitement épinglées), des étapes multi-stage, un compte non-root et un runtime minimal.
- **MUST NOT** embarquer `.env`, secrets, caches locaux, `.venv`, `node_modules`, bases locales ou clés dans l'image ; tenir `.dockerignore` à jour.
- **MUST** distinguer `static/` (sources versionnées), CSS Tailwind compilé et `STATIC_ROOT` (`collectstatic`), servir les fichiers statiques via une solution **réellement configurée** (reverse proxy, WhiteNoise, CDN, etc.). `collectstatic` seul n'est pas un serveur HTTP.
- **MUST** préserver PostgreSQL data volume et toute politique de sauvegarde ; aucune commande `docker compose down -v`, prune destructif ou purge DB sans confirmation explicite.
- **MUST** séparer migrations, construction des assets et démarrage applicatif selon l'organisation existante ; ne pas exécuter une migration destructive automatiquement sans validation.
- **MUST** contrôler healthchecks, timeouts, redémarrages, logs, arrêt gracieux, connectivité des services, reverse proxy, TLS et exposition des ports avant production.
- **MUST** utiliser la commande ASGI `uv run uvicorn gkuetenang.asgi:application ...` **seulement si Uvicorn est réellement choisi et installé** ; conserver un Gunicorn existant tant que son remplacement n'est pas approuvé. Le couple Gunicorn + `uvicorn-worker` est une option distincte à décider explicitement.
- **MUST NOT** lancer `manage.py runserver` en production.

## 10. Qualité Python, tests et CI

- **MUST** écrire du Python idiomatique 3.13, cohérent avec les conventions existantes ; PEP 8, annotations utiles, nommage descriptif, petites unités testables et suppression du code mort.
- **MUST** traiter `None`, saisies invalides, permissions, exceptions réseau, transactions, concurrence et doublons ; les exceptions doivent rester ciblées et traçables, sans divulgation d'informations privées.
- **MUST** ajouter des tests de comportement réels, et pas seulement des tests superficiels ou conçus pour « rendre vert » un pipeline.
- **MUST** utiliser Django `TestCase` / `TransactionTestCase` ou pytest-django uniquement si configuré ; isoler la DB de test, mocker les dépendances externes et éviter les véritables envois SMTP.
- **MUST** couvrir au minimum, pour toute modification du formulaire : formulaire GET, POST valide, POST invalide, longueur maximale, CSRF, rate limit, doublon, email mis en queue, échec de queue et permissions admin.
- **MUST** respecter les migrations et tester l'absence d'altération accidentelle de données. Aucune migration appliquée à une DB réelle lors d'un simple test.
- **SHOULD** vérifier syntaxe, formatage, typage selon CI existante, couverture des cas critiques, dépendances à risque, accessibilité et performance ; ne pas introduire un nouvel outil de qualité sans accord.

## 11. Accessibilité, SEO, performance et UX

- **MUST** viser WCAG 2.2 **AA** sur le périmètre modifié : navigation clavier, focus visible, labels, messages d'erreur associés, hiérarchie des titres, alt text utile et contrastes vérifiés.
- **MUST** respecter responsive mobile/desktop ; pas de débordement horizontal, texte lisible, formulaires utilisables sans souris et états feedback explicites.
- **MUST** conserver une sémantique HTML correcte : un `h1` principal par page, landmarks, `button` vs `a` selon action/navigation, `aria-*` seulement lorsque pertinent.
- **SHOULD** surveiller LCP (≤ 2,5 s), INP (≤ 200 ms) et CLS (≤ 0,1) au 75e percentile ; ce sont des objectifs, jamais des performances affirmées sans mesures.
- **MUST** optimiser images, fonts, bundling Tailwind et cache des assets ; pas de CDN inutile ni de script bloquant non justifié.
- **SHOULD** gérer titres/descriptions par page, canonicals cohérents, sitemap/robots selon contexte et données structurées seulement véridiques.

## 12. Critères de sortie obligatoires (« Definition of Done »)

Pour conclure une demande de code, l'assistant doit confirmer :

- [ ] Besoin, périmètre et invariants existants respectés.
- [ ] Versions et documentation **exactes** identifiées, ou inconnues explicitement signalées.
- [ ] Aucun nouveau secret, chemin inventé, dépendance fantôme, ni changement non sollicité.
- [ ] Validation des entrées, autorisation, CSRF, XSS, SQLi, abuse/rate limiting revus selon le périmètre.
- [ ] Templates : tokens sémantiques ; responsive ; a11y ; mode sombre ; aucun HEX dans le HTML.
- [ ] Django/DB : contrat HTTP et migrations préservés ; transactions cohérentes ; tests pertinents ajoutés.
- [ ] Emails/Celery : pas de double envoi ou de queue parallèle ; template existant préservé ; erreurs et retries raisonnés.
- [ ] Commandes de vérification pertinentes réellement exécutées, avec résultat **observé** ; échecs signalés.
- [ ] `git diff` relu ; aucun changement hors périmètre ou fichier local accidentel.
- [ ] Rapport de livraison : fichiers touchés, ce qui marche, tests, risques et actions nécessaires.

Une case non validée **ne doit jamais être cochée** par supposition. Si elle bloque la mise en production, annoncer explicitement « non prêt pour production » et expliquer le correctif.

## 13. Actions nécessitant accord explicite

**MUST NOT** faire sans autorisation spécifique :

- Installer, mettre à niveau, remplacer ou supprimer une dépendance.
- Changer Django 6.1.2, Python 3.13, `uv`/`pnpm`, remplacer Uvicorn/Gunicorn ou modifier le broker.
- Changer un contrat public (routes, champs de formulaire, format d'API, emails, noms de templates), ou des migrations destructives.
- Modifier sécurité de production, secrets, DNS, SSL, DNS email/SPF/DKIM/DMARC, infrastructure, volumes ou bases réelles.
- Lancer un déploiement, pousser du code, faire un commit, purger un volume/DB, effacer des données, appeler un service externe réel ou envoyer un email réel.
- Copier du contenu tiers protégé ou reproduire un design tiers à l'identique ; les références de design servent à inspirer des compositions originales.

## 14. Sources documentaires autorisées et versionnées

**Priorité 1** : fichiers et lockfiles du dépôt. **Priorité 2** : documentation officielle correspondant à la version installée. **Priorité 3** : changelog officiel et code source officiel versionné. Forums/blogs ne peuvent pas remplacer une source primaire pour une API ou un contrôle de sécurité.

- Django **6.1** : https://docs.djangoproject.com/en/6.1/
- Django 6.1 sécurité : https://docs.djangoproject.com/en/6.1/topics/security/
- Django 6.1 checklist prod : https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/
- Django 6.1 CSP : https://docs.djangoproject.com/en/6.1/howto/csp/
- Django 6.1 Uvicorn/ASGI : https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/uvicorn/
- Python 3.13 : https://docs.python.org/3.13/
- Astral uv : https://docs.astral.sh/uv/ (vérifier commandes selon version réellement installée)
- Tailwind CSS **v4** : https://tailwindcss.com/docs/theme et https://tailwindcss.com/docs/dark-mode
- shadcn/ui, thème : https://ui.shadcn.com/docs/theming
- pnpm : https://pnpm.io/ (choisir la documentation de la version `packageManager`)
- Uvicorn : https://www.uvicorn.org/ (choisir la version installée)
- Celery : https://docs.celeryq.dev/ (choisir la branche correspondant à `uv.lock`)
- django-post-office : https://django-post-office.readthedocs.io/ (vérifier contre le paquet/version installés et le code source officiel si nécessaire)
- Docker Compose : https://docs.docker.com/compose/
- OWASP ASVS **5.0.0** : https://asvs.owasp.org/
- WCAG 2.2 : https://www.w3.org/TR/WCAG22/

**Règle documentaire obligatoire :** lorsque l'assistant propose une API non triviale, une fonctionnalité de sécurité, une commande d'installation ou de déploiement, indiquer (au minimum dans son compte rendu) le produit, la version ciblée et la documentation officielle consultée. Si l'accès à cette documentation n'a pas été possible, écrire « documentation non vérifiée » et ne pas inventer sa compatibilité.

## 15. Format attendu d'une réponse d'assistant de code

1. **Diagnostic / constats vérifiés** (inclure versions réellement trouvées).
2. **Plan de changement** (uniquement si besoin significatif ou risque).
3. **Implémentation** dans les fichiers ciblés ; diff réduit ; pas de code non demandé.
4. **Vérifications exécutées** (commande, résultat observé, limites).
5. **Risques / décisions à approuver** (si présents), sans cacher les échecs.

> Règle finale : **privilégier la justesse vérifiable, la sécurité, l'accessibilité et la maintenabilité plutôt que la vitesse ou la quantité de code.**
