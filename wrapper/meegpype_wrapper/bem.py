import os
import subprocess
import tempfile

from ._checks import ensure_subject
from . import DOCKER_IMAGE

def add_parser(subparsers) -> None:
    subparser = subparsers.add_parser("bem", help="Run BEM surfaces pipeline")
    subparser.add_argument(
        "subject",
        help="The subject identifier (the sub- prefix can be removed).",
    )
    subparser.add_argument(
        "subjects_dir",
        type=os.path.abspath,
        help="The FreeSurfer subjects directory. "
             "The BEM surfaces are written to subjects_dir/subject/bem.",
    )
    subparser.add_argument(
        "--bem-method", "--method",
        help="Method to use for BEM surface generation. Options: 'basic' or 'refined'. Default is 'basic'.",
        choices=["basic", "refined"],
        default="basic",
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
    subparser.add_argument(
        "--engine",
        help="Engine to use for running the pipeline. Can be 'docker' or 'apptainer'. Default is 'docker'.",
        type=str,
        default="docker",
    )
    return(subparser)


def run(args, unknown_args) -> None:
    """Run bem() command."""

    engine = args.engine
    if engine == "apptainer":
        command = ['apptainer', 'exec', '--cleanenv', "--containall", "--writable-tmpfs"]
    else:
        command = ['docker', 'run', '--rm', '--pull=always']
    main_args = []

    # subjects_dir
    subjects_dir = args.subjects_dir
    if not os.path.exists(subjects_dir):
        raise FileNotFoundError(f"Subjects directory {subjects_dir} does not exist.")

    # subject
    subject = ensure_subject(args.subject, subjects_dir)
    main_args.extend([subject])

    if engine == "apptainer":
        command.extend(["-B", f"{subjects_dir}:/subjects_dir"])
    else:
        command.extend(["-v", f"{subjects_dir}:/subjects_dir"])
    main_args.extend(["/subjects_dir"])

    # work_dir
    work_dir = args.work_dir
    if work_dir is not None:
        if not os.path.exists(work_dir):
            os.makedirs(work_dir, exist_ok=True)
    else:
        work_dir = tempfile.mkdtemp(prefix="meegpype_workdir_")
    if engine == "apptainer":
        command.extend(["-B", f"{work_dir}:/scratch"])
    else:
        command.extend(["-v", f"{work_dir}:/scratch"])
    main_args.extend(["--work-dir", "/scratch"])

    # fs-license-file
    fs_license_file = args.fs_license_file
    if fs_license_file is not None:
        if not os.path.exists(fs_license_file):
            raise FileNotFoundError(f"FreeSurfer license file {fs_license_file} does not exist.")
        if engine == "apptainer":
            command.extend(["-B", f"{fs_license_file}:/opt/freesurfer/license.txt"])
            command.extend(["--env", "FS_LICENSE=/opt/freesurfer/license.txt"])
        else:
            command.extend(["-v", f"{fs_license_file}:/opt/freesurfer/license.txt"])

    # bem-method
    if args.bem_method:
        unknown_args.extend(["--bem-method", args.bem_method])

    # nprocs
    if args.nprocs:
        unknown_args.extend(["--nprocs", str(args.nprocs)])

    # image
    if engine == "apptainer":
        docker_image = "docker://" + DOCKER_IMAGE
    else:
        docker_image = DOCKER_IMAGE
    command.extend([docker_image])

    # Command
    if engine == "apptainer":
        command.extend(["/usr/local/bin/entrypoint.sh"])
    command.extend(["meegpype-bem"])
    command.extend(main_args)
    command.extend(unknown_args)

    # Run
    print(f"Running command: { ' '.join(command) }")
    ret = subprocess.run(command)
    if ret.returncode != 0:
        raise RuntimeError(f"Command {' '.join(command)} failed with return code {ret.returncode}.")
    return ret
