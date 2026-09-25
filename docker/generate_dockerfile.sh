#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

neurodocker generate docker \
  --base-image ghcr.io/vferat/smriprep:0.19.1-dev \
  --pkg-manager apt \
  --install graphviz ffmpeg libsm6 libxext6 xvfb x11-utils libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1 libxcb-xkb1 libxcb-cursor0 \
  --install libosmesa6 libegl1 libgl1-mesa-dri \
  --run "micromamba install -y -n smriprep -c conda-forge 'nodejs>=20' && micromamba clean --all --yes" \
  --copy . /meeg-pipelines \
  --run "micromamba run -n smriprep pip install --no-cache-dir -e /meeg-pipelines" \
  --copy docker/entrypoint.sh /usr/local/bin/entrypoint.sh \
  --run "chmod +x /usr/local/bin/entrypoint.sh" \
  --entrypoint /usr/local/bin/entrypoint.sh \
  --run "mkdir -p /out /scratch" \
  > Dockerfile
