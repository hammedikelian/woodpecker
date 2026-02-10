# Woodpecker CI Setup

Configuration CI/CD avec Woodpecker pour ce projet.

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│  Woodpecker Server  │◄────│   Woodpecker Agent  │
│    (Docker)         │     │   (Local macOS)     │
│    Port 8000/9000   │     │                     │
└─────────┬───────────┘     └──────────┬──────────┘
          │                            │
          │                            ▼
          │                    ┌───────────────┐
          │                    │    Docker     │
          │                    │   (Builds)    │
          │                    └───────────────┘
          ▼
   ┌─────────────┐
   │   GitHub    │
   │  (Webhooks) │
   └─────────────┘
```

## Fichiers de configuration

| Fichier | Description |
|---------|-------------|
| `docker-compose.woodpecker.yml` | Serveur Woodpecker |
| `.env.woodpecker` | Variables d'environnement (secrets) |
| `.woodpecker/pipeline.yml` | Pipeline CI |

## Commandes utiles

### Demarrer Woodpecker

```bash
# Lancer le serveur
docker compose -f docker-compose.woodpecker.yml --env-file .env.woodpecker up -d

# Lancer l'agent (local)
WOODPECKER_SERVER="localhost:9000" \
WOODPECKER_AGENT_SECRET="<secret>" \
WOODPECKER_BACKEND="docker" \
~/bin/woodpecker-agent agent
```

### Arreter Woodpecker

```bash
# Arreter le serveur
docker compose -f docker-compose.woodpecker.yml down

# Arreter l'agent
pkill -f woodpecker-agent
```

## Pipeline

Le pipeline se declenche sur :
- `push` sur main/develop
- `pull_request`
- `tag`

Etapes :
1. Affichage des infos (branch, commit)
2. Tests service-bdd
3. Tests service-vocal
4. Build des images Docker (sur main uniquement)
