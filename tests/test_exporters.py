import json

from alpha_scrapers.exporters import dump_to_json


def test_dump_to_json_creates_and_writes_file(tmp_path):
    data = [{"job_id": "1", "title": "Foo"}, {"job_id": "2", "title": "Bar"}]
    out = tmp_path / "snapshot.json"
    dump_to_json(data, str(out))
    assert out.exists()
    contents = json.loads(out.read_text(encoding="utf-8"))
    assert contents == data


def test_dump_empty_list(tmp_path):
    data = []
    out = tmp_path / "empty.json"
    dump_to_json(data, str(out))
    assert out.exists()
    assert json.loads(out.read_text(encoding="utf-8")) == []


def test_overwrites_existing_file(tmp_path):
    data1 = [{"job_id": "X"}]
    out = tmp_path / "out.json"
    out.write_text("not json")
    dump_to_json(data1, str(out))
    # should now be valid JSON matching data1
    assert json.loads(out.read_text(encoding="utf-8")) == data1


def test_creates_parent_dir(tmp_path):
    data = [{"a": 1}]
    nested = tmp_path / "sub" / "dir" / "file.json"
    dump_to_json(data, str(nested))
    assert nested.exists()
    assert json.loads(nested.read_text(encoding="utf-8")) == data
