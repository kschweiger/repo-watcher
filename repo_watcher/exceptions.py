class RepoWatcherException(Exception):
    pass


class NoTagsFoundException(RepoWatcherException):
    pass


class InvalidTagException(RepoWatcherException):
    pass


class RepoNotInitializedException(RepoWatcherException):
    pass


class RepoAlreadyInitializedException(RepoWatcherException):
    pass
