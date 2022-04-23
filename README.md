# Repo-Watcher

[![.github/workflows/ci.yml](https://github.com/kschweiger/repo-watcher/actions/workflows/ci.yml/badge.svg)](https://github.com/kschweiger/repo-watcher/actions/workflows/ci.yml)

Lightweight application for monitoring remote activity on a local repository and
updating the HEAD of the local repo on certain triggers.

## Watchers
### TagRepoWatcher

Initialize the watcher with a local repository and a tag pattern. Only tags in X.Y.Z
style (*X* - **major release**, *Y* - **minor release**, *Z* - **patch release**) are
supported. Currently, the following patters are supported:

|   Pattern | Description                                                                                                                                         |
|----------:|-----------------------------------------------------------------------------------------------------------------------------------------------------|
|     `'*'` | Always update the HEAD to the latest tag                                                                                                            |
|   `'X.*'` | Replace *X* with the major version that should be fixed. Will always be updated to the latest minor and patch release in the defined major release. |
| `'X.Y.*'` | Replace *X.Y* with the minor version that should be fixed. Will always update to the latest patch release.                                          |

#### Usage

```
Usage: run-watcher tag [OPTIONS]

  Run a TagRepoWatcher on a passed local repository.

Options:
  --repo TEXT                     Local path to the repository to watch
  --pattern TEXT                  Tag pattern for the watcher. Supported are
                                  '*', 'X.*', and 'X.Y.*'
  --log_level [WARNING|INFO|DEBUG]
  --interval INTEGER              Update interval in minutes
  --help                          Show this message and exit.
```
