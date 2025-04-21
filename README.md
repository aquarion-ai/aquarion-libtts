# Aquarion AI - Text To Speech (TTS)

Experiment in creating a scalable local AI voice chat bot.

## About

### About Aquarion AI

The goal of this project is to create an LLM-based voice chat bot / assistant, but to
built it in such a way that is can be scaled down to a single desktop app, all the way
up to a distributed multi-server, horizontally scalable system.  Also, desired is a
taking head / avatar who's mouth moves with the speech.  Lastly, it should all run
locally / offline, even in an air gapped environment.  Oh, and it should be modular
enough to support multiple alternate STT, LLM and TTS models/engines/options.

### About this Repository

The repository contains the Text To Speech (TTS) backend components for Aquarion AI.

### Disclaimer

While this project is FOSS and you are welcome to use it (if it ever becomes something
usable), know that I am making this for myself. So do not expect any kind of support or
updates or maintenance or longevity.  Caveat Emptor.

## Development Standards

This project follows the following standard practices:

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) for
  commit messages.
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) for versioning.

## Getting Started

1. Clone this repository.
1. Install [Devbox](https://www.jetify.com/docs/devbox/installing_devbox/)
1. Run `devbox shell`
1. Run `aq init`
1. Run `aq --help` to see what else it can do.

### Details

- Devbox is a tool for creating per-project development environments using Nix.
- On first run, `devbox shell` will download and install all that is needed for the
  environment.
- `devbox shell` enters the devbox, starts nuShell as the terminal shell, and then
  activates the Python virtual environment.
- `aq` is a custom script to help developers with common tasks.
- `aq init` is only needed on a fresh clone of if one delete's one's devbox.  It
  downloads and installs all dependencies.
