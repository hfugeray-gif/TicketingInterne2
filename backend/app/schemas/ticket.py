from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    titre: str
    typage: str
    site: Optional[str] = None
    commentaire: Optional[str] = None
    demandeur: str


class TicketUpdate(BaseModel):
    titre: Optional[str] = None
    typage: Optional[str] = None
    site: Optional[str] = None
    sous_type: Optional[str] = None
    commentaire: Optional[str] = None
    statut: Optional[str] = None
    priorite: Optional[str] = None
    assigne_a: Optional[str] = None
    motif_resolution: Optional[str] = None
    ticket_maitre_id: Optional[int] = None


class TicketResponse(BaseModel):
    id: int
    titre: str
    typage: str
    site: Optional[str]
    sous_type: Optional[str]
    commentaire: Optional[str]
    statut: str
    priorite: Optional[str]
    demandeur: str
    dispatcheur: Optional[str]
    assigne_a: Optional[str]
    motif_resolution: Optional[str]
    ticket_maitre_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True