class RepoWatcherException(Exception):
    pass


class NoTagsFoundException(RepoWatcherException):
    pass


class InvalidTagException(RepoWatcherException):
    pass
