from pathlib import Path
import datetime
import re

def sanitize_filename(s):
    """
    Sanitize a string to be safe for use as a filename.

    :param s: The input string to sanitize (e.g., a job ID or URL segment).
    :type s: str
    :returns: A sanitized string safe for use as a filename (alphanumeric, dash, underscore, dot).
    :rtype: str
    """
    return re.sub(r'[^\w\-_\.]+', '_', s)

def save_raw_response(content, scraper_name, filename, timestamp=None):
    """
    Save raw HTTP response content to a timestamped directory.

    :param content: The response body, either as bytes or as a string.
    :type content: bytes or str
    :param scraper_name: Short name of the scraper (e.g. 'qrt', 'cisco').
    :type scraper_name: str
    :param filename: Filename to use when saving (e.g. 'main_response.json').
    :type filename: str
    :param timestamp: Optional timestamp string (YYYYMMDD_HHMMSS). If not provided, use now.
    :type timestamp: str or None
    :returns: Path to the file that was written.
    :rtype: pathlib.Path

    The file will be written to:
        raw_responses/<scraper_name>/<YYYYMMDD_HHMMSS>/<filename>
    """
    base_dir = Path("raw_responses") / scraper_name
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = base_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(content, (bytes, bytearray)) else "w"
    path = run_dir / filename
    with open(path, mode) as f:
        f.write(content)
    return path
