import json
from pathlib import Path


def dump_to_json(data: list[dict], filepath: str) -> None:
    """
    Write `data` (a list of dicts) out as JSON to `filepath`, overwriting if exists.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
