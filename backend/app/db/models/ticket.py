from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    titre: Mapped[str] = mapped_column(String, nullable=False)
    typage: Mapped[str] = mapped_column(String, nullable=False)
    site: Mapped[str | None] = mapped_column(String, nullable=True)
    sous_type: Mapped[str | None] = mapped_column(String, nullable=True)

    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)

    statut: Mapped[str] = mapped_column(String, default="Ouvert", nullable=False)
    priorite: Mapped[str | None] = mapped_column(String, nullable=True)

    demandeur: Mapped[str] = mapped_column(String, nullable=False)
    dispatcheur: Mapped[str | None] = mapped_column(String, nullable=True)
    assigne_a: Mapped[str | None] = mapped_column(String, nullable=True)

    motif_resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    ticket_maitre_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)