"""Build the meeg-pipelines Docker image locally, for development or to test a PR.

Usage (from anywhere in the repository, only needs Python and Docker)::

    python docker/build.py                      # builds meeg-pipelines:local
    python docker/build.py --tag meeg-pipelines:my-branch
    python docker/build.py --build-base         # also rebuild the base image
    python docker/build.py --dry-run            # print the commands only

The base image (``ARG BASE_IMAGE`` in the Dockerfile) is pulled from the registry if it
exists, and built from docker/Dockerfile.base otherwise (e.g. when a PR bumps its tag).
"""

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = "linux/amd64"  # FreeSurfer and AFNI are only available for amd64


def _run(command: list[str], dry_run: bool, check: bool = True) -> int:
    print(f"$ {shlex.join(command)}", flush=True)
    if dry_run:
        return 0
    return subprocess.run(command, cwd=ROOT, check=check).returncode


def _quiet(command: list[str]) -> bool:
    """Run a command silently and return whether it succeeded."""
    ret = subprocess.run(
        command, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return ret.returncode == 0


def _base_image() -> str:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    match = re.search(r"^ARG BASE_IMAGE=(\S+)", dockerfile, flags=re.MULTILINE)
    if match is None:
        sys.exit("Could not find 'ARG BASE_IMAGE=' in the Dockerfile.")
    return match.group(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python docker/build.py",
        description="Build the meeg-pipelines Docker image locally.",
    )
    parser.add_argument(
        "-t", "--tag",
        default="meeg-pipelines:local",
        help="Name and tag of the built image (default: %(default)s).",
    )
    parser.add_argument(
        "--build-base",
        action="store_true",
        help="Rebuild the base image even if it is available.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Build without using the Docker build cache.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands without running them.",
    )
    args = parser.parse_args()

    # Base image: local, else registry, else build it
    base = _base_image()
    if args.build_base:
        build_base = True
    elif _quiet(["docker", "image", "inspect", base]):
        print(f"Base image {base} found locally.")
        build_base = False
    elif _quiet(["docker", "manifest", "inspect", base]):
        print(f"Base image {base} found in the registry.")
        build_base = False
    else:
        print(f"Base image {base} not found, building it (this takes a while).")
        build_base = True

    no_cache = ["--no-cache"] if args.no_cache else []
    if build_base:
        _run(
            ["docker", "build", "--platform", PLATFORM, *no_cache,
             "-f", "docker/Dockerfile.base", "-t", base, "."],
            args.dry_run,
        )

    # Main image. .git is part of the build context: uncommitted changes show up in
    # meegpype's version as a +dYYYYMMDD suffix.
    _run(
        ["docker", "build", "--platform", PLATFORM, *no_cache, "-t", args.tag, "."],
        args.dry_run,
    )

    if os.name == "nt":  # PowerShell
        env = f"$env:MEEGPYPE_IMAGE='{args.tag}'; $env:MEEGPYPE_PULL='never'; "
    else:
        env = f"MEEGPYPE_IMAGE={args.tag} MEEGPYPE_PULL=never "
    print(
        f"\nBuilt {args.tag}. To use it with meegpype-wrapper:\n"
        f"  {env}meegpype-wrapper ...\n"
        f"Or directly:\n"
        f"  docker run --rm {args.tag} meegpype-sys_info"
    )


if __name__ == "__main__":
    main()
