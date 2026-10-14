<<<<<<< Updated upstream
DOCKER_IMAGE = "ghcr.io/vferat/meeg-pipelines:smriprep-0.19.1-main"
=======
import os

from ._version import __version__, __version_tuple__

# The wrapper runs the image built from the same release: wrapper X.Y.Z runs
# ghcr.io/vferat/meeg-pipelines:X.Y.Z. Development versions (e.g. 0.2.0.dev3+g1234567)
# have no matching image and run the latest build of main instead.
# Set MEEGPYPE_IMAGE to use another image, e.g. a PR build
# (ghcr.io/vferat/meeg-pipelines:pr-9) or a local build (meeg-pipelines:local).
_is_release = len(__version_tuple__) == 3
DOCKER_IMAGE = os.environ.get(
    "MEEGPYPE_IMAGE",
    f"ghcr.io/vferat/meeg-pipelines:{__version__ if _is_release else 'latest'}",
)

# Docker pull policy (docker run --pull): release images never change and are only
# pulled when missing, other tags (latest, branches, PRs) are always pulled to get the
# last build. Set MEEGPYPE_PULL=never to run a locally built image.
_default_pull = (
    "missing" if _is_release and "MEEGPYPE_IMAGE" not in os.environ else "always"
)
DOCKER_PULL = os.environ.get("MEEGPYPE_PULL", _default_pull)
>>>>>>> Stashed changes
