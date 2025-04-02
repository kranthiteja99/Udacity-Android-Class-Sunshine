# Read up on just here: https://github.com/casey/just

set shell := ["bash", "-uc"]
set windows-shell := ["sh", "-uc"]

set ignore-comments
set positional-arguments

# Print help.
help:
  @just --list

_default: help

# Build everything.
build:
  uv sync --all-extras --all-packages --dev

# Format the code.
@format:
  ruff format

# Run tests.
@test:
  uv run pytest

# Run main.
# Run main benchmark (default run)
@run:
  uv run python -m battle_test.cli benchmark

# Show all personas without running Whisper
show-personas:
  uv run python -m battle_test.cli show-personas


