# Docker

The image is built in two layers, following sMRIPrep's own setup:

| File | Role |
|---|---|
| `docker/Dockerfile.base` | Base image: Ubuntu, FreeSurfer 7.3.2, AFNI, MSM, Xvfb. Identical to sMRIPrep's `Dockerfile.base`; rarely rebuilt. |
| `docker/files/freesurfer7.3.2-exclude.txt` | FreeSurfer files left out of the base image. Unlike upstream, it keeps `mni/bin/mritotal`. |
| `Dockerfile` | Main image: builds the pixi environment `meegpype` from `pixi.lock`, pre-fetches TemplateFlow templates and installs the entrypoint. |
| `pyproject.toml` (`[tool.pixi.*]`) / `pixi.lock` | Conda and PyPI dependencies of the environment. |
| `docker/entrypoint.sh` | Activates the environment, starts Xvfb for headless rendering, then runs the command. |
| `docker/fetch_templates.py` | TemplateFlow templates cached in the image (copied from sMRIPrep). |

## Where dependencies come from

- **System (apt), in the base image only**: FreeSurfer, AFNI, MSM, Xvfb, `bc`, `tcsh`, ...
  Don't add apt packages for meegpype; add them to the pixi environment instead.
- **Conda (`[tool.pixi.dependencies]`)**:
  - sMRIPrep's tools: ANTs, FSL, connectome-workbench, graphviz, nodejs, ... These must stay
    in sync with sMRIPrep's `[tool.pixi.dependencies]` for the pinned sMRIPrep version.
  - meegpype's 3D rendering stack: VTK, PyVista, PySide6/Qt, Mesa, ffmpeg.
    `QT_API=pyside6` (in `[tool.pixi.activation.env]`) makes MNE use this conda Qt, rather
    than the PyQt6 wheel pulled in by `mne[full]`, which would need X11/OpenGL libraries from apt.
- **PyPI (`[project] dependencies`)**: meegpype's Python dependencies, including `smriprep==0.20.0`.
  meegpype itself is installed in editable mode at `/meeg-pipelines`.
- **npm**: `svgo` and `bids-validator`, installed in the `Dockerfile` (as sMRIPrep does).

## Common tasks

Regenerate `pixi.lock` after any change to the pixi or `[project]` dependencies:

```
pixi lock
# without pixi installed locally:
docker run --rm -v "$PWD:/meeg-pipelines" -w /meeg-pipelines ghcr.io/prefix-dev/pixi:0.77.1 pixi lock
```

Bump sMRIPrep:

1. Update `smriprep==<version>` in `[project] dependencies`.
2. Copy sMRIPrep's `[tool.pixi.dependencies]` for that version into ours (keep the meegpype section).
3. If sMRIPrep's `Dockerfile.base` changed, copy it to `docker/Dockerfile.base` and bump the base image tag (see below).
4. Regenerate `pixi.lock`.

Build the image locally (development, testing a PR), with Python and Docker only:

```
python docker/build.py                    # builds meeg-pipelines:local
python docker/build.py -t meeg-pipelines:my-branch
python docker/build.py --build-base       # also rebuild the base image
python docker/build.py --dry-run          # print the docker commands only
```

It pulls the base image if it's in the registry and builds it otherwise (e.g. when a PR
bumps its tag). Then run the local image with the wrapper; `MEEGPYPE_PULL=never` stops
`docker run` from trying to pull it from a registry:

```
MEEGPYPE_IMAGE=meeg-pipelines:local MEEGPYPE_PULL=never meegpype-wrapper forward ...
# PowerShell
$env:MEEGPYPE_IMAGE='meeg-pipelines:local'; $env:MEEGPYPE_PULL='never'; meegpype-wrapper forward ...
```

The wrapper's pull policy (`MEEGPYPE_PULL`, passed to `docker run --pull`) defaults to
`missing` for release images and `always` for other tags (`latest`, branches, PRs).

Build the base image, only when `docker/Dockerfile.base` or the exclude list changes:

```
docker build -f docker/Dockerfile.base -t ghcr.io/vferat/meeg-pipelines-base:<YYYYMMDD> .
docker push ghcr.io/vferat/meeg-pipelines-base:<YYYYMMDD>
```

Then set the same tag in `ARG BASE_IMAGE=` in `Dockerfile`. In CI (`.github/workflows/build-docker.yaml`)
the base image is built and pushed automatically when the tag in `Dockerfile` doesn't exist yet.

## Releases and `meegpype-wrapper`

`meegpype` and `meegpype-wrapper` (in `wrapper/`) get their version from git tags with
setuptools-scm (`release-branch-semver` scheme), so both always share the same version.
The wrapper runs the image matching its version: wrapper `X.Y.Z` runs
`ghcr.io/vferat/meeg-pipelines:X.Y.Z`. A development version (e.g. `0.2.0.dev3+g1234567`)
has no matching image and runs `latest` (the build of `main`).

To release, push the tag `vX.Y.Z`: CI pushes the image as `X.Y.Z` (and `vX.Y.Z`).

As in sMRIPrep, `.git` is part of the Docker build context (not in `.dockerignore`), so the
image build reads meegpype's version from git. CI checks out the full history for this.
Only add untracked files to `.dockerignore`: excluding a tracked file makes the tree look
modified inside the build and the version gets a `+dYYYYMMDD` suffix.

To run the wrapper against another image (e.g. a branch or PR build), set `MEEGPYPE_IMAGE`:

```
MEEGPYPE_IMAGE=ghcr.io/vferat/meeg-pipelines:pr-9 meegpype-wrapper forward ...
```

## Notes

- The pixi environment hard-codes its path, so the workspace is at `/meeg-pipelines` both in the
  build stage and in the final image (`/meeg-pipelines/.pixi/envs/meegpype`).
- Don't split the environment install with `pixi install --skip meegpype`: it leaves part of the
  environment uninstalled, and a later `pixi install` considers it up to date.
- `docker/**` and `Dockerfile` are forced to LF line endings (`.gitattributes`): CRLF breaks
  `entrypoint.sh` and the FreeSurfer exclude list on Windows checkouts.
