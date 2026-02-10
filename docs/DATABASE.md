# Database Schema - Music Voice

## Diagramme UML

```
┌─────────────────────────────────────────────────────────────┐
│                         musiques                            │
├─────────────────────────────────────────────────────────────┤
│ «PK» id              : SERIAL          [AUTO INCREMENT]     │
├─────────────────────────────────────────────────────────────┤
│      titre           : VARCHAR(255)    [NOT NULL]           │
│      artiste         : VARCHAR(255)    [NOT NULL]           │
│      album           : VARCHAR(255)    [NULLABLE]           │
│      duree_secondes  : INTEGER         [NOT NULL]           │
│      fichier_audio   : VARCHAR(255)    [NOT NULL]           │
│      fichier_cover   : VARCHAR(255)    [NULLABLE]           │
│      created_at      : TIMESTAMP       [DEFAULT NOW()]      │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Indexes
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  idx_musiques_titre    ON LOWER(titre)                      │
│  idx_musiques_artiste  ON LOWER(artiste)                    │
│  idx_musiques_album    ON LOWER(album)                      │
└─────────────────────────────────────────────────────────────┘
```

## Description des colonnes

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | SERIAL | PK, AUTO INCREMENT | Identifiant unique |
| `titre` | VARCHAR(255) | NOT NULL | Titre de la musique |
| `artiste` | VARCHAR(255) | NOT NULL | Nom de l'artiste |
| `album` | VARCHAR(255) | NULLABLE | Nom de l'album |
| `duree_secondes` | INTEGER | NOT NULL | Durée en secondes |
| `fichier_audio` | VARCHAR(255) | NOT NULL | Chemin du fichier MP3 |
| `fichier_cover` | VARCHAR(255) | NULLABLE | Chemin de la pochette |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date de création |

## SQL de création

```sql
CREATE TABLE IF NOT EXISTS musiques (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    artiste VARCHAR(255) NOT NULL,
    album VARCHAR(255),
    duree_secondes INTEGER NOT NULL,
    fichier_audio VARCHAR(255) NOT NULL,
    fichier_cover VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes pour la recherche
CREATE INDEX IF NOT EXISTS idx_musiques_titre ON musiques(LOWER(titre));
CREATE INDEX IF NOT EXISTS idx_musiques_artiste ON musiques(LOWER(artiste));
CREATE INDEX IF NOT EXISTS idx_musiques_album ON musiques(LOWER(album));
```

## Exemple de données

```sql
INSERT INTO musiques (titre, artiste, album, duree_secondes, fichier_audio, fichier_cover)
VALUES
    ('Bohemian Rhapsody', 'Queen', 'A Night at the Opera', 354, 'bohemian_rhapsody.mp3', 'queen_cover.jpg'),
    ('Billie Jean', 'Michael Jackson', 'Thriller', 294, 'billie_jean.mp3', 'thriller_cover.jpg'),
    ('Hotel California', 'Eagles', 'Hotel California', 390, 'hotel_california.mp3', 'eagles_cover.jpg');
```

## Relations avec l'application

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Flutter App   │────►│  Service Vocal  │────►│   Service BDD   │
│                 │     │   (Port 5001)   │     │   (Port 5002)   │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   PostgreSQL    │
                                                │   (Port 5432)   │
                                                │                 │
                                                │  ┌───────────┐  │
                                                │  │ musiques  │  │
                                                │  └───────────┘  │
                                                └─────────────────┘
```

## Endpoints API (Service BDD)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/musiques` | Liste toutes les musiques |
| GET | `/musiques/{id}` | Détail d'une musique |
| GET | `/musiques/search?q=` | Recherche par titre/artiste |
| GET | `/health` | État du service |

## Fichier PlantUML

Le fichier `database-schema.puml` peut être visualisé avec :
- [PlantUML Online](https://www.plantuml.com/plantuml/uml/)
- Extension VS Code "PlantUML"
- IntelliJ IDEA avec plugin PlantUML
