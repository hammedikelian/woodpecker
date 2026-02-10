#!/usr/bin/env python3
"""Script to seed the database with sample music data."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_cursor, init_db

SAMPLE_MUSIQUES = [
    {
        "titre": "Bohemian Rhapsody",
        "artiste": "Queen",
        "album": "A Night at the Opera",
        "duree_secondes": 354,
        "fichier_audio": "bohemian_rhapsody.mp3",
        "fichier_cover": "queen_night_opera.jpg",
    },
    {
        "titre": "Imagine",
        "artiste": "John Lennon",
        "album": "Imagine",
        "duree_secondes": 183,
        "fichier_audio": "imagine.mp3",
        "fichier_cover": "lennon_imagine.jpg",
    },
    {
        "titre": "Billie Jean",
        "artiste": "Michael Jackson",
        "album": "Thriller",
        "duree_secondes": 294,
        "fichier_audio": "billie_jean.mp3",
        "fichier_cover": "mj_thriller.jpg",
    },
    {
        "titre": "Smells Like Teen Spirit",
        "artiste": "Nirvana",
        "album": "Nevermind",
        "duree_secondes": 301,
        "fichier_audio": "smells_like_teen_spirit.mp3",
        "fichier_cover": "nirvana_nevermind.jpg",
    },
    {
        "titre": "Hotel California",
        "artiste": "Eagles",
        "album": "Hotel California",
        "duree_secondes": 391,
        "fichier_audio": "hotel_california.mp3",
        "fichier_cover": "eagles_hotel.jpg",
    },
    {
        "titre": "Stairway to Heaven",
        "artiste": "Led Zeppelin",
        "album": "Led Zeppelin IV",
        "duree_secondes": 482,
        "fichier_audio": "stairway_to_heaven.mp3",
        "fichier_cover": "led_zeppelin_iv.jpg",
    },
    {
        "titre": "Sweet Child O Mine",
        "artiste": "Guns N Roses",
        "album": "Appetite for Destruction",
        "duree_secondes": 356,
        "fichier_audio": "sweet_child_o_mine.mp3",
        "fichier_cover": "gnr_appetite.jpg",
    },
    {
        "titre": "Like a Rolling Stone",
        "artiste": "Bob Dylan",
        "album": "Highway 61 Revisited",
        "duree_secondes": 373,
        "fichier_audio": "like_a_rolling_stone.mp3",
        "fichier_cover": "dylan_highway.jpg",
    },
    {
        "titre": "Purple Rain",
        "artiste": "Prince",
        "album": "Purple Rain",
        "duree_secondes": 520,
        "fichier_audio": "purple_rain.mp3",
        "fichier_cover": "prince_purple.jpg",
    },
    {
        "titre": "Hey Jude",
        "artiste": "The Beatles",
        "album": "Hey Jude",
        "duree_secondes": 431,
        "fichier_audio": "hey_jude.mp3",
        "fichier_cover": "beatles_hey_jude.jpg",
    },
    {
        "titre": "Wonderwall",
        "artiste": "Oasis",
        "album": "Morning Glory",
        "duree_secondes": 258,
        "fichier_audio": "wonderwall.mp3",
        "fichier_cover": "oasis_morning.jpg",
    },
    {
        "titre": "Back in Black",
        "artiste": "AC DC",
        "album": "Back in Black",
        "duree_secondes": 255,
        "fichier_audio": "back_in_black.mp3",
        "fichier_cover": "acdc_black.jpg",
    },
    {
        "titre": "Lose Yourself",
        "artiste": "Eminem",
        "album": "8 Mile Soundtrack",
        "duree_secondes": 326,
        "fichier_audio": "lose_yourself.mp3",
        "fichier_cover": "eminem_8mile.jpg",
    },
    {
        "titre": "Comfortably Numb",
        "artiste": "Pink Floyd",
        "album": "The Wall",
        "duree_secondes": 382,
        "fichier_audio": "comfortably_numb.mp3",
        "fichier_cover": "pinkfloyd_wall.jpg",
    },
    {
        "titre": "November Rain",
        "artiste": "Guns N Roses",
        "album": "Use Your Illusion I",
        "duree_secondes": 537,
        "fichier_audio": "november_rain.mp3",
        "fichier_cover": "gnr_illusion.jpg",
    },
]


def seed_database():
    """Seed the database with sample music data."""
    print("Initializing database schema...")
    init_db()

    print("Seeding database with sample music...")

    with get_db_cursor() as cursor:
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) as count FROM musiques")
        result = cursor.fetchone()

        if result["count"] > 0:
            print(f"Database already contains {result['count']} musiques. Skipping seed.")
            return

        # Insert sample data
        for musique in SAMPLE_MUSIQUES:
            cursor.execute(
                """
                INSERT INTO musiques (titre, artiste, album, duree_secondes, fichier_audio, fichier_cover)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    musique["titre"],
                    musique["artiste"],
                    musique["album"],
                    musique["duree_secondes"],
                    musique["fichier_audio"],
                    musique["fichier_cover"],
                ),
            )

        print(f"Successfully inserted {len(SAMPLE_MUSIQUES)} musiques.")


if __name__ == "__main__":
    seed_database()
