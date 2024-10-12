#!/usr/bin/env sh
set -euo pipefail
wget -Oopenapi.json localhost:8080/openapi.json
npx openapi-typescript-codegen -i openapi.json -o webapp/lib/apiClient --exportCore=false --exportServices=false
rm openapi.json
