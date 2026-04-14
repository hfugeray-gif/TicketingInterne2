from fastapi import APIRouter, Query

from app.schemas.reference import PageConfigResponse, SiteResponse, SubtypeResponse
from app.services.reference_service import get_pages_config, get_sites, get_subtypes

router = APIRouter()


@router.get("/sites", response_model=list[SiteResponse])
def list_sites():
    return get_sites()


@router.get("/subtypes")
def list_subtypes(type_parent: str | None = Query(default=None)):
    result = get_subtypes(type_parent)
    if type_parent:
        return [SubtypeResponse(**item) for item in result]
    return result


@router.get("/pages", response_model=list[PageConfigResponse])
def list_pages_config():
    return get_pages_config()