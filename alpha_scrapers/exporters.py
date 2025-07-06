"""
exporters module
Provides utilities for exporting scraped data to various formats.
"""

import json
from pathlib import Path


def dump_to_json(data: list[dict], filepath: str) -> None:
    """
    Write a list of dictionaries out as JSON to the specified file path, creating
    parent directories if necessary and overwriting any existing file.

    :param data: The data to serialize to JSON.
    :type data: list[dict]
    :param filepath: Filesystem path where the JSON file will be written.
    :type filepath: str
    :returns: None
    :rtype: None
    :raises OSError: If the target directory cannot be created or file cannot be opened.
    :raises TypeError: If `data` is not serializable to JSON.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
