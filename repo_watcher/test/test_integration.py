import os
import shutil

import pytest
from git import Repo

import repo_watcher.repo_watcher
from repo_watcher.run_watcher import tag


@pytest.fixture
def repo_for_testing() -> Repo:
    repo_path = os.path.join(os.getcwd(), "integration-test-repo")
    repo = Repo.init(repo_path)

    files = []
    for i in range(4):
        file_path = os.path.join(repo.working_tree_dir, f"file{i}.txt")
        open(file_path, "wb").close()
        files.append(file_path)

    repo.index.add([os.path.join(repo.working_tree_dir, "file0.txt")])
    repo.index.commit("Committing first file")
    repo.create_tag("1.0.0")
    yield repo

    shutil.rmtree(repo_path)


def test_run_tag_watcher(monkeypatch, repo_for_testing):
    monkeypatch.setattr(
        repo_watcher.repo_watcher.TagRepoWatcher, "_fetch_remote", lambda x: None
    )
    # We start with a master branch, one commit and a 1.0.0 tag

    # Check if the repo is currently on the master branch
    assert not repo_for_testing.head.is_detached
    assert repo_for_testing.head.reference.name == "master"

    # Run the run-watcher tag function once:
    tag.callback(repo_for_testing.working_tree_dir, "*", "DEBUG", 0.01, True)
    assert repo_for_testing.head.is_detached
    assert (
        repo_for_testing.head.commit
        == [ref.commit for ref in repo_for_testing.references if ref.name == "1.0.0"][0]
    )

    # Add a commit and a new minor release tag
    repo_for_testing.index.add(
        [os.path.join(repo_for_testing.working_tree_dir, "file1.txt")]
    )
    repo_for_testing.index.commit("Committing second file")
    repo_for_testing.create_tag("1.1.0")

    # Run the run-watcher tag function once:
    tag.callback(repo_for_testing.working_tree_dir, "*", "DEBUG", 0.01, True)
    assert repo_for_testing.head.is_detached
    assert (
        repo_for_testing.head.commit
        == [ref.commit for ref in repo_for_testing.references if ref.name == "1.1.0"][0]
    )

    # Add a commit and a new major release tag
    repo_for_testing.index.add(
        [os.path.join(repo_for_testing.working_tree_dir, "file2.txt")]
    )
    repo_for_testing.index.commit("Committing third file")
    repo_for_testing.create_tag("2.0.0")

    # Run the run-watcher tag function once:
    tag.callback(repo_for_testing.working_tree_dir, "*", "DEBUG", 0.01, True)
    assert repo_for_testing.head.is_detached
    assert (
        repo_for_testing.head.commit
        == [ref.commit for ref in repo_for_testing.references if ref.name == "2.0.0"][0]
    )

    # Add a commit and a new major release tag
    repo_for_testing.index.add(
        [os.path.join(repo_for_testing.working_tree_dir, "file3.txt")]
    )
    repo_for_testing.index.commit("Committing fourth file")
    repo_for_testing.create_tag("3.0.0")

    # Run the run-watcher tag function once but with a fixed major version pattern
    tag.callback(repo_for_testing.working_tree_dir, "2.*", "DEBUG", 0.01, True)
    assert repo_for_testing.head.is_detached
    assert (
        repo_for_testing.head.commit
        == [ref.commit for ref in repo_for_testing.references if ref.name == "2.0.0"][0]
    )
