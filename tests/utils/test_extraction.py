import pytest
from alpha_scrapers.utils.extraction import jmes_get

@pytest.mark.parametrize(
    "pattern,data,default,expected",
    [
        ("foo", {"foo": 1}, None, 1),
        ("foo", {"bar": 2}, None, None),
        ("foo", {"bar": 2}, "missing", "missing"),
        ("foo.bar", {"foo": {"bar": 3}}, None, 3),
        ("foo[0]", {"foo": [10, 20]}, None, 10),
        ("foo[1]", {"foo": [10, 20]}, None, 20),
        ("foo[2]", {"foo": [10, 20]}, "notfound", "notfound"),
        # different behaviour to standard Python get()
        ("foo", {"foo": None}, "default_if_null", "default_if_null"),
        ("foo", None, "default", "default"),
    ],
    ids=[
        "simple_key_present",
        "simple_key_missing",
        "simple_key_missing_with_default",
        "nested_key",
        "list_index_0",
        "list_index_1",
        "list_index_out_of_range_with_default",
        "value_is_null_returns_default",
        "none_data_with_default",
    ],
)
def test_jmes_get(pattern, data, default, expected):
    assert jmes_get(pattern, data, default) == expected
