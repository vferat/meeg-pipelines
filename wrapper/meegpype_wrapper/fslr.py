import os
import subprocess

from . import DOCKER_IMAGE

def add_parser(subparsers) -> None:
    subparser = subparsers.add_parser("fslr", help="Run fslr pipeline")
    subparser.add_argument(
        "subject",
        help="The subject identifier.",
    )
    subparser.add_argument(
        "subjects_dir",
        type=os.path.abspath,
        help="The FreeSurfer subjects directory.",
    )
    subparser.add_argument(
        "output_dir",
        type=os.path.abspath,
        help="The output path for the outcomes of preprocessing and visual reports.",
    )
    subparser.add_argument(
        "--atlas",
        help="The atlas to use for labelling (e.g., subparc374).",
    )
    subparser.add_argument(
        "-w", "--work-dir",
        type=os.path.abspath,
        help="Path where intermediate results should be stored.",
    )
    subparser.add_argument(
        "--fs-license-file",
        type=os.path.abspath,
        help="Path to FreeSurfer license key file.",
    )
    subparser.add_argument(
        "--nprocs", "--nthreads", "--n_cpus", "--n-cpus",
        default=1,
        type=int,
        help="Maximum number of threads across all processes.",

    )
    return(subparser)


def run(args, unknown_args) -> None:
    """Run fslr command."""
    command = ['docker', 'run', '--rm']

    # subjects_dir
    subjects_dir = args.subjects_dir
    if not os.path.exists(subjects_dir):
        raise FileNotFoundError(f"Subjects directory {subjects_dir} does not exist.")
    command.extend(["-v", f"{subjects_dir}:/subjects_dir"])

    # output_dir
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    command.extend(["-v", f"{output_dir}:/out"])

    # work_dir
    work_dir = args.work_dir
    if work_dir is not None:
        if not os.path.exists(work_dir):
            os.makedirs(work_dir, exist_ok=True)
        command.extend(["-v", f"{work_dir}:/scratch"])

    # fs-license-file
    fs_license_file = args.fs_license_file
    if fs_license_file is not None:
        if not os.path.exists(fs_license_file):
            raise FileNotFoundError(f"FreeSurfer license file {fs_license_file} does not exist.")
        command.extend(["-v", f"{fs_license_file}:/opt/freesurfer/license.txt"])

    # docker image
    docker_image = DOCKER_IMAGE
    command.extend([docker_image])

    # Command
    command.extend(["meegpype-fslr"])

    # subject
    subject = args.subject
    if subject is None:
        raise ValueError("--subject is required for fslr pipeline.")
    else:
        command.extend([subject])
        # subjects_dir
        command.extend(["/subjects_dir"])
        # output_dir
        command.extend(["/out"])
        # atlas
        if args.atlas:
            command.extend(["--atlas", args.atlas])
        # work_dir
        if work_dir is not None:
            command.extend(["--work-dir", "/scratch"])
        # nprocs
        if args.nprocs:
            command.extend(["--nprocs", str(args.nprocs)])

        full_command = command + unknown_args
        # Run
        print(f"Running command: { ' '.join(full_command) }")
        ret = subprocess.run(full_command)
        if ret.returncode != 0:
            raise RuntimeError(f"Command {' '.join(full_command)} failed with return code {ret.returncode}.")
