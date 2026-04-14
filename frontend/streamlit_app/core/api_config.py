import pandas as pd

from core.api_client import api_get


def get_sites_config() -> pd.DataFrame:
    data = api_get("/config/sites")
    return pd.DataFrame(data)


def get_subtypes_config(type_parent: str | None = None) -> pd.DataFrame:
    params = {"type_parent": type_parent} if type_parent else None
    data = api_get("/config/subtypes", params=params)

    if isinstance(data, list):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        # Cas 1 : backend renvoie déjà une structure tabulaire
        if all(not isinstance(value, list) for value in data.values()):
            return pd.DataFrame([data])

        # Cas 2 : backend renvoie un mapping type -> liste de sous-types
        rows = []
        for parent, values in data.items():
            if isinstance(values, list):
                for idx, value in enumerate(values, start=1):
                    if isinstance(value, dict):
                        row = dict(value)
                        row.setdefault("type_parent", parent)
                        row.setdefault("display_order", idx)
                        rows.append(row)
                    else:
                        rows.append(
                            {
                                "type_parent": parent,
                                "label": str(value),
                                "is_active": True,
                                "display_order": idx,
                            }
                        )
            else:
                rows.append(
                    {
                        "type_parent": parent,
                        "label": str(values),
                        "is_active": True,
                        "display_order": 1,
                    }
                )

        return pd.DataFrame(rows)

    return pd.DataFrame()


def get_active_subtypes_by_type(type_parent: str) -> list[str]:
    df = get_subtypes_config(type_parent)
    if df.empty:
        return []

    if "is_active" in df.columns:
        df = df[df["is_active"] == True]

    if "display_order" in df.columns:
        df = df.sort_values(["display_order", "label"], kind="stable")

    if "label" not in df.columns:
        return []

    return df["label"].astype(str).tolist()


def get_pages_config() -> pd.DataFrame:
    data = api_get("/config/pages")
    return pd.DataFrame(data)