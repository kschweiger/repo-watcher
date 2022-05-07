import logging
import os
from time import sleep

import click

from repo_watcher.watcher import TagRepoWatcher

logging.getLogger("git").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """CLI interface to run a RepoWatcher"""
    pass


@cli.command()
@click.option("--repo", help="Local path to the repository to watch")
@click.option(
    "--pattern",
    help="Tag pattern for the watcher. Supported are '*', 'X.*', and 'X.Y.*'",
)
@click.option(
    "--log_level",
    type=click.Choice(["WARNING", "INFO", "DEBUG"]),
    default="INFO",
    envvar="WATCHER_LOGLEVEL",
)
@click.option(
    "--interval",
    help="Update interval in minutes",
    default=30,
    type=int,
    envvar="WATCHER_INTERVAL",
)
def tag(
    repo: str, pattern: str, log_level: str, interval: int, single_run: bool = False
) -> None:
    """
    Run a TagRepoWatcher on a passed local repository.
    """
    logging.basicConfig(
        format="[%(asctime)s] %(name)-40s %(levelname)-8s %(message)s",
        level=log_level,
    )

    if os.getenv("WATCHER_INTERVAL") is not None:
        logger.info("Interval read from ENV")
    if os.getenv("WATCHER_LOGLEVEL") is not None:
        logger.info("Logging level read from ENV")

    logger.info("Starting a TagRepoWatcher for %s" % repo)

    watcher = TagRepoWatcher(repo, pattern)
    watcher.initialize_git()
    exit_condition = True
    while exit_condition:
        if watcher.observe():
            watcher.update_head()
        logger.debug("Sleeping for %s minutes", interval)
        sleep(interval * 60)
        if single_run:
            exit_condition = False


if __name__ == "__main__":
    cli()
