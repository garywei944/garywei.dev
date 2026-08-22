#!/usr/bin/env bash

set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if ! command -v hugo >/dev/null 2>&1; then
  printf 'error: Hugo is not installed or not available in PATH\n' >&2
  exit 127
fi

exec hugo server --environment development --buildDrafts "$@"
