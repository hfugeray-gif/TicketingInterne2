from datetime import datetime

from pydantic import BaseModel


class CommentCreate(BaseModel):
    auteur: str
    contenu: str


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    auteur: str
    contenu: str
    created_at: datetime

    class Config:
        from_attributes = True