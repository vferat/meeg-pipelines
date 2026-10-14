# meeg-pipelines Docker image
#
# Adapted from sMRIPrep's Dockerfile. The base image (FreeSurfer, AFNI, MSM and
# system libraries) is built from docker/Dockerfile.base; the Python/conda
# environment (sMRIPrep tools + meegpype) is built with pixi from pixi.lock.

ARG BASE_IMAGE=ghcr.io/vferat/meeg-pipelines-base:20261014

#
# Build pixi environment
#
FROM ghcr.io/prefix-dev/pixi:0.77.1 AS build
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    ca-certificates \
                    git && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Run post-link scripts during install, but use global to keep out of source tree
RUN pixi config set --global run-post-link-scripts insecure

# The workspace path is hard-coded in the environment, keep it identical in the final image
WORKDIR /meeg-pipelines

# Install the environment with the package (editable). Don't split this with
# `pixi install --skip meegpype`: it leaves part of the environment uninstalled
# and a later `pixi install` considers it up to date.
# .git is copied too: setuptools-scm reads meegpype's version from it.
COPY . /meeg-pipelines
RUN --mount=type=cache,target=/root/.cache/rattler pixi install -e meegpype --frozen
RUN --mount=type=cache,target=/root/.npm pixi run --as-is -e meegpype npm install -g svgo@^3.2.0 bids-validator@1.14.10
# Note that PATH gets hard-coded. Remove it and re-apply in final image
RUN pixi shell-hook -e meegpype --as-is | grep -v PATH > /shell-hook.sh

#
# Pre-fetch templates
#
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS templates
ENV TEMPLATEFLOW_HOME="/templateflow"
RUN uv pip install --system templateflow
COPY docker/fetch_templates.py fetch_templates.py
RUN python fetch_templates.py

#
# Main stage
#
FROM ${BASE_IMAGE}

# Create a shared $HOME directory
RUN useradd -m -s /bin/bash -G users meegpype
WORKDIR /home/meegpype
ENV HOME="/home/meegpype"

COPY --link --from=templates /templateflow /home/meegpype/.cache/templateflow

COPY --link --from=build /meeg-pipelines /meeg-pipelines
COPY --link --from=build /shell-hook.sh /shell-hook.sh
RUN cat /shell-hook.sh >> $HOME/.bashrc
ENV PATH="/meeg-pipelines/.pixi/envs/meegpype/bin:$PATH"

ENV FSLDIR="/meeg-pipelines/.pixi/envs/meegpype"

RUN chmod -R go=u $HOME

# Unless otherwise specified each process should only use one thread - nipype
# will handle parallelization
ENV MKL_NUM_THREADS=1 \
    OMP_NUM_THREADS=1

# For detecting the container (used by sMRIPrep)
ENV IS_DOCKER_8395080871=1

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh \
    && mkdir -p /out /scratch

WORKDIR /tmp
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
