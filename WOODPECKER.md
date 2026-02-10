# Woodpecker CI - Documentation

Configuration CI/CD professionnelle avec Woodpecker pour ce projet.

## Architecture

```
                                    ┌─────────────────┐
                                    │     GitHub      │
                                    │    (Webhooks)   │
                                    └────────┬────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TRAEFIK                                 │
│                    (HTTPS / Let's Encrypt)                      │
└─────────────────────────────────────────────────────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
          ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
          │   Woodpecker    │    │   Woodpecker    │    │   PostgreSQL    │
          │     Server      │◄───│     Agent       │    │    Database     │
          │   (Port 8000)   │    │  (Runs builds)  │    │                 │
          └─────────────────┘    └─────────────────┘    └─────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │      Docker         │
                              │   (Build & Push)    │
                              └─────────────────────┘
```

## Pipeline CI/CD

```
┌─────────┐    ┌──────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│  LINT   │───►│ SECURITY │───►│  TEST   │───►│  BUILD  │───►│  PUSH    │───►│  DEPLOY  │
│         │    │          │    │         │    │         │    │ Registry │    │          │
│ black   │    │ bandit   │    │ pytest  │    │ docker  │    │ ghcr.io  │    │ staging  │
│ flake8  │    │ safety   │    │ coverage│    │ build   │    │          │    │ prod     │
│ isort   │    │          │    │         │    │         │    │          │    │          │
└─────────┘    └──────────┘    └─────────┘    └─────────┘    └──────────┘    └──────────┘
```

## Configuration locale (Développement)

### Prérequis
- Docker Desktop
- ngrok (`brew install ngrok`)
- GitHub OAuth App

### Démarrage rapide
```bash
# 1. Copier le fichier d'environnement
cp .env.woodpecker.example .env.woodpecker

# 2. Éditer .env.woodpecker avec vos credentials GitHub

# 3. Lancer Woodpecker
./scripts/start-local.sh
```

### Commandes manuelles
```bash
# Démarrer le serveur
docker compose -f docker-compose.woodpecker.yml --env-file .env.woodpecker up -d

# Démarrer l'agent local
WOODPECKER_SERVER="localhost:9000" \
WOODPECKER_AGENT_SECRET="<secret>" \
WOODPECKER_BACKEND="docker" \
~/bin/woodpecker-agent agent

# Arrêter
docker compose -f docker-compose.woodpecker.yml down
pkill -f woodpecker-agent
```

## Configuration Production

### Prérequis
- Serveur Linux (Ubuntu 22.04 recommandé)
- Domaine avec accès DNS
- Docker & Docker Compose

### Installation
```bash
# 1. Cloner le projet sur le serveur
git clone https://github.com/hammedikelian/woodpecker.git
cd woodpecker

# 2. Lancer le setup
./scripts/setup-production.sh

# 3. Configurer DNS
# Pointer ci.votredomaine.com vers l'IP du serveur

# 4. Attendre le certificat SSL (quelques minutes)
```

### Gestion avec woodpecker-ctl
```bash
./scripts/woodpecker-ctl.sh start     # Démarrer
./scripts/woodpecker-ctl.sh stop      # Arrêter
./scripts/woodpecker-ctl.sh status    # Statut
./scripts/woodpecker-ctl.sh logs      # Voir les logs
./scripts/woodpecker-ctl.sh backup    # Sauvegarder la BDD
./scripts/woodpecker-ctl.sh update    # Mettre à jour
./scripts/woodpecker-ctl.sh secrets   # Aide pour les secrets
./scripts/woodpecker-ctl.sh health    # Vérifier la santé
```

## Secrets à configurer

Dans Woodpecker UI > Repository > Settings > Secrets :

| Secret | Description | Comment l'obtenir |
|--------|-------------|-------------------|
| `GHCR_TOKEN` | Token GitHub pour push images | GitHub > Settings > Developer settings > Personal access tokens |
| `SSH_KEY` | Clé SSH pour déploiement | `ssh-keygen -t ed25519 -f deploy_key` |
| `STAGING_HOST` | Hostname serveur staging | IP ou domaine du serveur staging |
| `PROD_HOST` | Hostname serveur prod | IP ou domaine du serveur production |
| `WEBHOOK_URL` | URL webhook Discord/Slack | Discord: Server Settings > Integrations > Webhooks |

## Fichiers de configuration

| Fichier | Description |
|---------|-------------|
| `docker-compose.woodpecker.yml` | Config locale (développement) |
| `docker-compose.prod.yml` | Config production avec Traefik |
| `.env.woodpecker.example` | Template variables locales |
| `.env.prod.example` | Template variables production |
| `.woodpecker/pipeline.yml` | Pipeline CI/CD |
| `pyproject.toml` | Config outils Python |
| `.flake8` | Config linting |

## Triggers du pipeline

| Événement | Branches | Actions |
|-----------|----------|---------|
| `push` | main, develop | Lint → Security → Test → Build |
| `pull_request` | toutes | Lint → Security → Test |
| `tag` | - | Lint → Security → Test → Build → Push Registry → Deploy Prod |
| `cron` | - | Nightly security scan |

## Environnements de déploiement

| Environnement | Trigger | Approbation |
|---------------|---------|-------------|
| **Staging** | Push sur main | Automatique |
| **Production** | Tag (v1.0.0) | Automatique |

## Monitoring

### Logs
```bash
# Tous les services
./scripts/woodpecker-ctl.sh logs

# Service spécifique
./scripts/woodpecker-ctl.sh logs woodpecker-server

# Suivre en temps réel
./scripts/woodpecker-ctl.sh logs -f
```

### Backups
Les backups sont automatiques (quotidiens) et gardés :
- 7 derniers jours
- 4 dernières semaines
- 6 derniers mois

Backup manuel :
```bash
./scripts/woodpecker-ctl.sh backup
```

## Troubleshooting

### L'agent ne se connecte pas
```bash
# Vérifier les logs de l'agent
docker logs woodpecker-agent

# Vérifier que le secret est correct
grep WOODPECKER_AGENT_SECRET .env.prod
```

### Pipeline échoue au lint
```bash
# Formatter le code localement
pip install black isort flake8
black service-bdd service-vocal
isort service-bdd service-vocal
```

### Certificat SSL non généré
```bash
# Vérifier les logs Traefik
docker logs traefik

# Vérifier que le DNS pointe vers le serveur
dig ci.votredomaine.com
```
