# Music Voice - Application Mobile de Musique par Commande Vocale

[![CI Pipeline](https://ci.woodpecker-ci.org/api/badges/hammedikelian/woodpecker/status.svg)](https://ci.woodpecker-ci.org/hammedikelian/woodpecker)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Application mobile Flutter contrôlée par commande vocale avec 2 services backend Python (FastAPI) et PostgreSQL, le tout conteneurisé avec Docker.

## CI/CD Pipeline

Notre pipeline CI/CD professionnel inclut :

| Stage | Outils | Description |
|-------|--------|-------------|
| **Lint** | black, flake8, isort | Formatage et qualité du code |
| **Security** | bandit, safety | Analyse de sécurité |
| **Test** | pytest, coverage | Tests unitaires avec couverture |
| **Build** | Docker | Construction des images |

## Architecture

```
Flutter App ─── HTTP ───> Service Vocal (5001) ─── HTTP ───> Service BDD (5002) ───> PostgreSQL (5432)
                         (Vosk STT + Parser)         (REST API CRUD)
```

## Prérequis

- Docker & Docker Compose
- Flutter SDK (>= 3.0.0)
- Android Studio / Xcode (pour le développement mobile)

## Installation et Démarrage

### 1. Démarrer les services backend

```bash
# Depuis le répertoire racine du projet
docker-compose up -d

# Vérifier que les services sont démarrés
docker-compose ps

# Peupler la base de données avec des musiques de test
docker exec -it music_service_bdd python scripts/seed.py
```

### 2. Vérifier les services

```bash
# Vérifier le service BDD
curl http://localhost:5002/health
curl http://localhost:5002/musiques

# Vérifier le service vocal
curl http://localhost:5001/health
```

### 3. Lancer l'application Flutter

```bash
cd music_voice_app
flutter pub get
flutter run
```

## Services Backend

### Service BDD (port 5002)

API REST pour la gestion des musiques.

**Endpoints:**
- `GET /health` - Vérification de santé
- `GET /musiques` - Liste toutes les musiques
- `GET /musiques/{id}` - Détail d'une musique
- `GET /musiques/search?q=` - Recherche textuelle

### Service Vocal (port 5001)

Service de reconnaissance vocale utilisant Vosk.

**Endpoint principal:**
- `POST /recognize` - Reçoit un fichier audio WAV, retourne l'intention et la musique

**Intentions reconnues:**
| Intention | Déclencheurs |
|-----------|--------------|
| PLAY | "joue", "mets", "lance", "je veux écouter" |
| STOP | "stop", "arrête", "coupe" |
| PAUSE | "pause", "mets en pause" |
| RESUME | "reprends", "continue" |
| NEXT | "suivant", "passe" |
| PREVIOUS | "précédent", "reviens" |

## Application Flutter

### Structure

```
music_voice_app/
├── lib/
│   ├── main.dart                  # Point d'entrée
│   ├── config/
│   │   └── app_config.dart        # Configuration (URLs)
│   ├── models/
│   │   └── musique.dart           # Modèle de données
│   ├── services/
│   │   ├── audio_recorder_service.dart  # Enregistrement micro
│   │   ├── audio_player_service.dart    # Lecture audio
│   │   ├── vocal_api_service.dart       # Client API vocal
│   │   └── tts_service.dart             # Text-to-Speech
│   ├── providers/
│   │   └── music_provider.dart    # État global (Provider)
│   ├── screens/
│   │   └── home_screen.dart       # Écran principal
│   └── widgets/
│       ├── voice_button.dart      # Bouton micro animé
│       ├── audio_visualizer.dart  # Visualiseur barres
│       ├── mini_player.dart       # Lecteur en bas
│       └── loading_overlay.dart   # Overlay chargement
└── assets/
    ├── musiques/                  # Fichiers MP3
    └── covers/                    # Images des pochettes
```

### États de l'application

```
IDLE → LISTENING → PROCESSING → PLAYING/ERROR → IDLE
```

### Configuration réseau

Dans `lib/config/app_config.dart`, l'URL de base est automatiquement configurée:
- **iOS Simulator**: `localhost`
- **Android Emulator**: `10.0.2.2`

## Test de la commande vocale

```bash
# Envoyer un fichier WAV au service vocal
curl -X POST -F "audio=@test.wav" http://localhost:5001/recognize
```

Réponse attendue:
```json
{
  "success": true,
  "transcript": "joue bohemian rhapsody",
  "intent": "PLAY",
  "musique": {
    "id": 1,
    "titre": "Bohemian Rhapsody",
    "artiste": "Queen",
    "album": "A Night at the Opera",
    "duree_secondes": 354,
    "fichier_audio": "bohemian_rhapsody.mp3",
    "fichier_cover": "queen_night_opera.jpg"
  }
}
```

## Points Techniques

1. **Vosk**: Modèle français `vosk-model-small-fr-0.22` (~40MB), téléchargé automatiquement dans le Dockerfile
2. **Format audio**: WAV 16kHz mono requis par Vosk
3. **Fuzzy matching**: Seuil 70% avec `token_set_ratio` de rapidfuzz
4. **Permissions Flutter**:
   - Android: `RECORD_AUDIO`, `INTERNET`
   - iOS: `NSMicrophoneUsageDescription`

## Développement

### Logs des services

```bash
# Voir les logs
docker-compose logs -f service-vocal
docker-compose logs -f service-bdd
```

### Reconstruire les images

```bash
docker-compose build --no-cache
docker-compose up -d
```

### Arrêter les services

```bash
docker-compose down
```

## Ajouter des musiques

1. Placez les fichiers MP3 dans `music_voice_app/assets/musiques/`
2. Placez les images de couverture dans `music_voice_app/assets/covers/`
3. Mettez à jour le script `service-bdd/scripts/seed.py` avec les nouvelles entrées
4. Exécutez le script de seed:
   ```bash
   docker exec -it music_service_bdd python scripts/seed.py
   ```

## Exemples de commandes vocales

- "Joue Bohemian Rhapsody"
- "Mets du Queen"
- "Lance Billie Jean"
- "Je veux écouter Hotel California"
- "Stop"
- "Pause"
- "Reprends"
- "Suivant"
- "Précédent"
