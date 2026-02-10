from typing import List, Optional

from database import get_db_cursor
from fastapi import APIRouter, HTTPException, Query
from models.musique import MusiqueResponse

router = APIRouter(prefix="/musiques", tags=["musiques"])


@router.get("", response_model=List[MusiqueResponse])
def get_all_musiques():
    """Récupère toutes les musiques."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, titre, artiste, album, duree_secondes, fichier_audio, fichier_cover
            FROM musiques
            ORDER BY artiste, titre
        """)
        results = cursor.fetchall()
    return [MusiqueResponse(**row) for row in results]


@router.get("/search", response_model=List[MusiqueResponse])
def search_musiques(q: str = Query(..., min_length=1, description="Terme de recherche")):
    """Recherche des musiques par titre ou artiste."""
    with get_db_cursor() as cursor:
        search_term = f"%{q.lower()}%"
        cursor.execute(
            """
            SELECT id, titre, artiste, album, duree_secondes, fichier_audio, fichier_cover
            FROM musiques
            WHERE LOWER(titre) LIKE %s OR LOWER(artiste) LIKE %s OR LOWER(album) LIKE %s
            ORDER BY
                CASE
                    WHEN LOWER(titre) LIKE %s THEN 1
                    WHEN LOWER(artiste) LIKE %s THEN 2
                    ELSE 3
                END,
                titre
        """,
            (search_term, search_term, search_term, search_term, search_term),
        )
        results = cursor.fetchall()
    return [MusiqueResponse(**row) for row in results]


@router.get("/{musique_id}", response_model=MusiqueResponse)
def get_musique(musique_id: int):
    """Récupère une musique par son ID."""
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, titre, artiste, album, duree_secondes, fichier_audio, fichier_cover
            FROM musiques
            WHERE id = %s
        """,
            (musique_id,),
        )
        result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Musique non trouvée")

    return MusiqueResponse(**result)
