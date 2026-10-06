#!/usr/bin/env bash
# Build dist/audiopod-openai.zip for upload to the OpenAI plugin portal.
# See scripts/build_openai_zip.py for what goes in and the size limits enforced.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/build_openai_zip.py "$@"
