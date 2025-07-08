import pytest
from alpha_scrapers.utils.io import sanitize_filename, save_raw_response
import alpha_scrapers.utils.io as io_mod
from freezegun import freeze_time

@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("abc123", "abc123"),
        ("abc 123", "abc_123"),
        ("abc/123", "abc_123"),
        ("abc:123?", "abc_123_"),
        ("abc-123_foo.bar", "abc-123_foo.bar"),
    ],
    ids=[
        "alphanumeric",
        "space",
        "slash",
        "punctuation",
        "safe-mixed",
    ],
)
def test_sanitize_filename(input_str, expected):
    assert sanitize_filename(input_str) == expected


@pytest.mark.parametrize(
    "content,filename,timestamp,expected_content,read_method,expected_timestamp",
    [
        # Default timestamp (freeze_time)
        ("hello world", "file.txt", None, "hello world", "read_text", "20240701_123456"),
        # Explicit timestamp, text
        ("hello world", "file.txt", "20240101_120000", "hello world", "read_text", "20240101_120000"),
        # Explicit timestamp, binary
        (b"\x00\x01\x02", "file.bin", "20240101_120000", b"\x00\x01\x02", "read_bytes", "20240101_120000"),
    ],
    ids=["text_default_timestamp", "text_explicit_timestamp", "binary_explicit_timestamp"]
)
@freeze_time("2024-07-01 12:34:56")
def test_save_raw_response_parametrized(tmp_path, monkeypatch, content, filename, timestamp, expected_content, read_method, expected_timestamp):
    monkeypatch.setattr(io_mod, "Path", lambda *a, **kw: tmp_path.joinpath(*a))
    kwargs = {"timestamp": timestamp} if timestamp else {}
    path = save_raw_response(content, "test", filename, **kwargs)
    assert expected_timestamp in str(path)
    assert getattr(path, read_method)() == expected_content
    assert path.exists()
    assert path.is_file()
    assert path.parent.exists()
    assert path.parent.is_dir()
    assert path.name == filename
    assert "raw_responses" in str(path)
    assert "test" in str(path)
    assert path.stat().st_size > 0
