from pydantic import BaseModel


class SiteResponse(BaseModel):
    code: str
    label: str
    display_order: int
    is_active: bool


class SubtypeResponse(BaseModel):
    label: str
    display_order: int
    is_active: bool


class PageConfigResponse(BaseModel):
    page_key: str
    label: str
    icon: str | None
    display_order: int
    is_visible: bool