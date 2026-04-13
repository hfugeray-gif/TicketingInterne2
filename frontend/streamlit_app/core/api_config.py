import pandas as pd

from core.api_client import api_get


def get_sites_config() -> pd.DataFrame:
    data = api_get("/config/sites")
    return pd.DataFrame(data)


def get_subtypes_config(type_parent: str | None = None) -> pd.DataFrame:
    params = {"type_parent": type_parent} if type_parent else None
    data = api_get("/config/subtypes", params=params)
    return pd.DataFrame(data)


def get_active_subtypes_by_type(type_parent: str) -> list[str]:
    df = get_subtypes_config(type_parent)
    if df.empty:
        return []

    if "is_active" in df.columns:
        df = df[df["is_active"] == True]

    if "display_order" in df.columns:
        df = df.sort_values(["display_order", "label"], kind="stable")

    return df["label"].astype(str).tolist()


def get_pages_config() -> pd.DataFrame:
    data = api_get("/config/pages")
    return pd.DataFrame(data)