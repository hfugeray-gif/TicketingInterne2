from pydantic import BaseModel


class MergeRequest(BaseModel):
    child_ticket_ids: list[int]
    auteur: str


class UnmergeRequest(BaseModel):
    auteur: str