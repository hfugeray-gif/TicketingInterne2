from datetime import datetime

from pydantic import BaseModel


class JournalResponse(BaseModel):
    id: int
    ticket_id: int
    action: str
    details: str | None
    auteur: str
    created_at: datetime

    class Config:
        from_attributes = True