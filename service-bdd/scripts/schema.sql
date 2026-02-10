-- Schema for music database

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

-- Create indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_musiques_titre ON musiques(LOWER(titre));
CREATE INDEX IF NOT EXISTS idx_musiques_artiste ON musiques(LOWER(artiste));
CREATE INDEX IF NOT EXISTS idx_musiques_album ON musiques(LOWER(album));
