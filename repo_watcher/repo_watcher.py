import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from git import Reference, Repo, TagReference

from repo_watcher.enums import PatternType
from repo_watcher.exceptions import (
    InvalidTagException,
    NoTagsFoundException,
    RepoAlreadyInitializedException,
    RepoNotInitializedException,
    RepoWatcherException,
)

logger = logging.getLogger(__name__)


class RepoWatcher(ABC):
    def __init__(self, repo: str, delay: int = 0):
        self.repo_path = repo
        self.delay = timedelta(minutes=delay)

        self.repo: Optional[Repo] = None
        self.repo_initialized: Optional[datetime] = None

        self.branch: Optional[str] = None
        self.commit: Optional[str] = None

    def initialize_git(self):
        if self.repo is not None:
            raise RepoAlreadyInitializedException("Repo already initialized")

        self.repo = Repo(self.repo_path)
        self.repo_initialized = datetime.now()

        if self.repo.head.is_detached:
            logger.debug("Currently in detached head state")
        else:
            self.branch = self.repo.head.ref.name
            logger.debug("Currently on branch %s", self.branch)

        self.commit = self.repo.head.commit.hexsha
        logger.debug("Currently on commit %s", self.commit)

    def get_reference_for_commit(self, commit_sha: str) -> List[Reference]:
        if self.repo is None:
            raise RepoNotInitializedException("Repo not initialized")

        refs = []
        for ref in self.repo.references:
            if ref.commit.hexsha == commit_sha:
                refs.append(ref)

        return refs

    def _fetch_remote(self):
        logger.info(
            "Fetching repo %s from remote %s", self.repo_path, self.repo.remote().name
        )
        logger.debug("Remote url: %s", self.repo.remote().url)
        self.repo.remote().fetch()

    @abstractmethod
    def observe(self) -> bool:
        """
        Main method that will be executed in while the RepoWatcher is running to decide
        if the local repository needs to be updated.
        :return: A boolean flag that is True if the repo should be updated
        """

    @abstractmethod
    def update_head(self):
        """
        Main method handling the updating of the current repository
        """


class BranchRepoWatcher(RepoWatcher):
    """
    RepoWatcher that will watch updates to a branch and follow new updates when an
    updated is observed. For this on initialization, a new branch will be created from
    the watched branch. According to the delay, the watched branch will be merged into
    to the "watcher" branch.

    Args:
        repo: Local path to the repository
        branch: Name of the branch
        delay: Time delay in minutes
    """

    def __init__(self, repo: str, branch: str, delay: int = 0):
        super().__init__(repo, delay)

        self.branch = branch


class TagRepoWatcher(RepoWatcher):
    """
    RepoWatcher that will watch tags and updates the repo is a new tag is observed that
    follows some predefined criteria

    Args:
        repo: Local path to the repository
        tag_pattern: Tag pattern. Supported are * (every release), X.* (every minor re-
                     lease with the major version X.) and X.Y.* (every patch release
                     of the versions X.Y)
        delay: Time delay in minutes
    """

    def __init__(self, repo: str, tag_pattern: str, delay: int = 0):
        logger.info("Initializing tag watcher")
        logger.debug("     repo: %s", repo)
        logger.debug("  pattern: %s", tag_pattern)
        logger.debug("    delay: %s", delay)
        super().__init__(repo, delay)

        self.pattern = "No_set"
        self.pattern_okay: bool = False
        self.pattern_type: PatternType = PatternType.INVALID
        self.update_pattern(tag_pattern)

        self.checked_out_tag: Optional[str] = None

        self.newest_tag: Optional[str] = None
        self.newest_tag_sha: Optional[str] = None

    def update_pattern(self, tag_pattern):
        self.pattern = tag_pattern
        self.pattern_okay, self.pattern_type = self._validated_pattern(tag_pattern)

    def get_newest_tag(self) -> str:
        # Find latest tag matching the passed pattern
        tags = self.get_sorted_tags()

        if not tags:
            raise NoTagsFoundException("No Tags found in repository")

        if self.pattern_type == PatternType.ALL:
            return tags[-1]
        elif self.pattern_type in [PatternType.MAJOR, PatternType.MINOR]:
            r = re.compile(
                self.pattern.replace("*", "[0-9]*").replace(".", "\.")  # noqa: W605
            )
            return [tag for tag in tags if r.match(tag) is not None][-1]
        else:
            # Should not really happen but we still add and exception
            raise RepoWatcherException("Invalid Pattern type")

    def get_sorted_tags(self) -> List[str]:
        if self.repo is None:
            raise RepoNotInitializedException("Repo not initialized")

        return sorted([ref.name for ref in self.repo.tags])

    def get_sha_for_tag(self, tag: str) -> str:
        if self.repo is None:
            raise RepoNotInitializedException("Repo not initialized")

        refs = [ref for ref in self.repo.references if isinstance(ref, TagReference)]

        for ref in refs:
            if ref.name == tag:
                return ref.commit.hexsha

        raise InvalidTagException("Not reference for tag %s found" % tag)

    def observe(self) -> bool:
        if self.repo is None:
            raise RepoNotInitializedException("Repo not initialized")

        if self.checked_out_tag is None:
            logger.debug("Checkout out tag not set")

        self._fetch_remote()

        self.newest_tag = self.get_newest_tag()
        logger.debug("Latest tag: %s", self.newest_tag)

        self.newest_tag_sha = self.get_sha_for_tag(self.newest_tag)
        logger.debug("Sha for tag: %s", self.newest_tag_sha)

        self.commit = self.repo.head.commit.hexsha
        logger.debug("Currently on commit: %s", self.commit)

        if self.commit != self.newest_tag_sha:
            logger.info("Head is not a latest tag")
            return True
        else:
            if not self.repo.head.is_detached:
                logger.info("Repository head is not detaced")
                return True
            logger.info("Head is on latest tag")
            return False

    def update_head(self):
        if self.repo is None:
            raise RepoNotInitializedException("Repo not initialized")

        logger.info(
            "Updating local repository to tag %s at %s",
            self.newest_tag,
            self.newest_tag_sha,
        )

        self.repo.git.checkout(self.newest_tag_sha)

    @staticmethod
    def _validated_pattern(pattern) -> Tuple[bool, PatternType]:
        valid_pattern_a = re.compile("[0-9]*\.\*\Z")  # noqa: W605
        valid_pattern_b = re.compile("[0-9]*\.[0-9]*\.\*\Z")  # noqa: W605

        if pattern == "*":
            return True, PatternType.ALL
        elif valid_pattern_a.match(pattern) is not None:
            return True, PatternType.MAJOR
        elif valid_pattern_b.match(pattern) is not None:
            return True, PatternType.MINOR
        else:
            return False, PatternType.INVALID
