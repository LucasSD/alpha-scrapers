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


@freeze_time("2024-07-01 12:34:56")
def test_save_raw_response_text_default_timestamp(tmp_path, monkeypatch):
    monkeypatch.setattr(io_mod, "Path", lambda *a, **kw: tmp_path.joinpath(*a))
    content = "hello world"
    path = save_raw_response(content, "test", "file.txt")
    assert "20240701_123456" in str(path)
    assert path.read_text() == content
    assert path.exists()
    assert path.is_file()
    assert path.parent.exists()
    assert path.parent.is_dir()
    assert path.name == "file.txt"
    assert "raw_responses" in str(path)
    assert "test" in str(path)
    assert path.stat().st_size > 0


def test_save_raw_response_text_explicit_timestamp(tmp_path, monkeypatch):
    monkeypatch.setattr(io_mod, "Path", lambda *a, **kw: tmp_path.joinpath(*a))
    content = "hello world"
    path = save_raw_response(content, "test", "file.txt", timestamp="20240101_120000")
    assert "20240101_120000" in str(path)
    assert path.read_text() == content
    assert path.exists()
    assert path.is_file()
    assert path.parent.exists()
    assert path.parent.is_dir()
    assert path.name == "file.txt"
    assert "raw_responses" in str(path)
    assert "test" in str(path)
    assert path.stat().st_size > 0


def test_save_raw_response_binary(tmp_path, monkeypatch):
    monkeypatch.setattr(io_mod, "Path", lambda *a, **kw: tmp_path.joinpath(*a))
    content = b"\x00\x01\x02"
    path = save_raw_response(content, "test", "file.bin", timestamp="20240101_120000")
    assert path.exists()
    assert path.is_file()
    assert path.parent.exists()
    assert path.parent.is_dir()
    assert path.name == "file.bin"
    assert "raw_responses" in str(path)
    assert "test" in str(path)
    assert "20240101_120000" in str(path)
    assert path.read_bytes() == content
    assert path.stat().st_size > 0
