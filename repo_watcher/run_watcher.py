import logging
from time import sleep

import click

from repo_watcher.repo_watcher import TagRepoWatcher

logging.getLogger("git").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """CLI interface to run a RepoWatcher"""
    pass


@cli.command()
@click.option("--repo", help="Local path to the repository to watch")
@click.option(
    "--pattern",
    help="Tag pattern for the watcher. Supported are '*', 'X.*', and 'X.Y.*'",
)
@click.option(
    "--log_level", type=click.Choice(["WARNING", "INFO", "DEBUG"]), default="INFO"
)
@click.option("--interval", help="Update interval in minutes", default=30, type=int)
def tag(repo, pattern, log_level, interval):
    """
    Run a TagRepoWatcher on a passed local repository.
    """
    logging.basicConfig(
        format="[%(asctime)s] %(name)-40s %(levelname)-8s %(message)s",
        level=log_level,
    )

    logger.info("Starting a TagRepoWatcher for %s" % repo)

    watcher = TagRepoWatcher(repo, pattern)
    watcher.initialize_git()
    while True:
        if watcher.observe():
            watcher.update_head()
        logger.debug("Sleeping for %s minutes", interval)
        sleep(interval * 60)


if __name__ == "__main__":
    cli()
