from copy import copy
from unittest.mock import MagicMock

import pytest

from repo_watcher.enums import PatternType
from repo_watcher.repo_watcher import TagRepoWatcher


@pytest.mark.parametrize(
    ("pattern", "result"),
    [
        ("*", (True, PatternType.ALL)),
        ("1.*", (True, PatternType.MAJOR)),
        ("1.1.*", (True, PatternType.MINOR)),
        ("A", (False, PatternType.INVALID)),
        ("1.*.*", (False, PatternType.INVALID)),
    ],
)
def test_valid_pattern(pattern, result):
    watcher = TagRepoWatcher("/path/to/repo", "*")
    assert watcher._validated_pattern(pattern) == result


@pytest.mark.parametrize(
    ("in_tags", "exp_tags"),
    [
        (["1.1.0", "1.0.0"], ["1.0.0", "1.1.0"]),
        (["0.0.1", "2.0.0", "1.0.0", "1.1.0"], ["0.0.1", "1.0.0", "1.1.0", "2.0.0"]),
    ],
)
def test_get_sorted_tags(in_tags, exp_tags):
    watcher = TagRepoWatcher("/path/to/repo", "*")

    in_tag_refs = [MagicMock() for i in range(len(in_tags))]
    for i, tag in enumerate(in_tags):
        in_tag_refs[i].name = copy(tag)

    watcher.repo = MagicMock()
    watcher.repo.tags = in_tag_refs

    assert watcher.get_sorted_tags() == exp_tags


@pytest.mark.parametrize(
    ("pattern", "sorted_tags", "exp_tag"),
    [
        ("*", ["0.0.1", "1.0.0", "1.1.0", "1.1.1", "1.2.0", "2.0.0"], "2.0.0"),
        ("*", ["9.0.0", "10.0.0"], "10.0.0"),
        ("1.*", ["0.0.1", "1.0.0", "1.1.0", "1.1.1", "1.2.0", "2.0.0"], "1.2.0"),
        ("1.1.*", ["0.0.1", "1.0.0", "1.1.0", "1.1.1", "1.2.0", "2.0.0"], "1.1.1"),
    ],
)
def test_get_newest_tag(pattern, sorted_tags, exp_tag):
    watcher = TagRepoWatcher("/path/to/repo", pattern)
    sorted_tags_mock = MagicMock()
    sorted_tags_mock.return_value = sorted_tags
    watcher.get_sorted_tags = sorted_tags_mock

    latest_tag = watcher.get_newest_tag()

    assert latest_tag == exp_tag
