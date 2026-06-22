#!/usr/bin/env bash
# Regenerate the typed contract from the JSON Schemas (single source of truth).
#   shared/schemas/*.json  ->  shared/ts/*.ts        (client types)
#                          ->  shared/py/*.py        (server/content Pydantic models)
# CI runs this and fails if the working tree drifts (git diff --exit-code).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[codegen] TypeScript types -> shared/ts"
pnpm codegen:ts

echo "[codegen] Pydantic models -> shared/py"
uv run datamodel-codegen \
  --input shared/schemas \
  --input-file-type jsonschema \
  --output shared/py \
  --output-model-type pydantic_v2.BaseModel \
  --use-double-quotes \
  --use-schema-description \
  --disable-timestamp

echo "[codegen] done"
