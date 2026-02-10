from pydantic import BaseModel
from typing import Optional


class MusiqueBase(BaseModel):
    titre: str
    artiste: str
    album: Optional[str] = None
    duree_secondes: int
    fichier_audio: str
    fichier_cover: Optional[str] = None


class MusiqueCreate(MusiqueBase):
    pass


class Musique(MusiqueBase):
    id: int

    class Config:
        from_attributes = True


class MusiqueResponse(BaseModel):
    id: int
    titre: str
    artiste: str
    album: Optional[str]
    duree_secondes: int
    fichier_audio: str
    fichier_cover: Optional[str]
