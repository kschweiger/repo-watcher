# Repo-Watcher

[![.github/workflows/ci.yml](https://github.com/kschweiger/repo-watcher/actions/workflows/ci.yml/badge.svg)](https://github.com/kschweiger/repo-watcher/actions/workflows/ci.yml)

Lightweight cli application for monitoring remote activity on a local repository and
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


## Run Repo-Watcher in a Docker container

### Initial thing to consider

- The repo that should be watched is assumed to be outside the docker container. So the directory with the repository to watch has to be mounted.
- If you clone the repo via ssh (which you probably do and should), the easiest way to still pull (which is an essential function of the watcher) is to forward your ssh-agent to the container (see Docs: [MacOS](https://docs.docker.com/desktop/mac/networking/#ssh-agent-forwarding))
  - Some Docker+MacOS notes:
    - You should add your key to the agent in `.zprofile` first.
    - You might encounter problems that the ssh-agent is not forwarded properly to the container.
      A reason could be that you start a new agent in your `.zprofile` (or need to use some other agent).
      In that case you can try to start DockerDesktop from a terminal with added and running agent with `/Applications/Docker.app/Contents/MacOS/Docker &`
      and not as usual from the Dock/Spotlight/Finder.

### Setup

1. Clone this repository
2. Build the image with provided docker file
    ```zsh
    docker build -t repo-watcher-daemon .
    ```
3. Find the (absolute) path to the repository that should be watched and updated


Run the image:

### Running the watcher as daemon

#### On MacOS:

```zsh
docker run -d \
  --mount type=bind,source=/path/to/repo/on/host,target=/repo \
  --mount type=bind,src=/run/host-services/ssh-auth.sock,target=/run/host-services/ssh-auth.sock \
  -e SSH_AUTH_SOCK="/run/host-services/ssh-auth.sock"  \
  -e GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" \
  --memory="100mb" \
  --name repo-watcher-daemon repo-watcher-daemon
```

#### On Linux:

```zsh
docker run -d \
  --mount type=bind,source=/path/to/repo/on/host,target=/repo \
  --mount type=bind,src=$(readlink -f $SSH_AUTH_SOCK),target=/ssh-agent \
  -e SSH_AUTH_SOCK="/ssh-agent"  \
  -e GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" \
  --memory="100mb" \
  --name repo-watcher-daemon repo-watcher-daemon
```


#### Explanation

- First `--mount`: Mount the repo that should be watched in the container
- Second `--mount` and first environment variable (`-e`): Proved the ssh-agent of the host to the container
- Second environment variable: Git should not to the host authentication when fetching the remote
- The memory is constrained to 100mb (preliminary setting). In principle the watcher should not use much memory but the GitPython package is known to leak memory

#### Additional info

Interval and log level inside the container can be set via env variables. Add:

```zsh
-e WATCHER_LOGLEVEL="DEBUG" # OR ERROR/WARNING/INFO
```

```zsh
-e WATCHER_INTERVAL=10 # 10 minute interval instead of 30 min
```