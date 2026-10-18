#!/usr/bin/env bash
# Genera build/lambda.zip con el código y las dependencias para Lambda (Python 3.12, arm64).
set -euo pipefail

cd "$(dirname "$0")/.."
rm -rf build && mkdir -p build/paquete

pip install -r requirements.txt -t build/paquete \
  --platform manylinux2014_aarch64 --implementation cp --python-version 3.12 \
  --only-binary=:all: --quiet

cp -r app build/paquete/
(cd build/paquete && zip -qr ../lambda.zip . -x '*__pycache__*')
echo "Paquete listo: build/lambda.zip ($(du -h build/lambda.zip | cut -f1))"
