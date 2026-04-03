from pydantic import BaseModel


class MeResponse(BaseModel):
    username: str
    email: str
    role: str
    authenticated: bool