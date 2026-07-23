"""parse_keywords 함수에 대한 pytest 테스트."""

from logviewer.keyword_parser import parse_keywords


def test_basic_split():
    assert parse_keywords("ERROR, WARN, INFO") == ["ERROR", "WARN", "INFO"]


def test_excludes_empty_items():
    assert parse_keywords("ERROR, , INFO") == ["ERROR", "INFO"]


def test_empty_string_returns_empty_list():
    assert parse_keywords("") == []
