import os
import subprocess
import tempfile
from . import DOCKER_IMAGE

def add_parser(subparsers) -> None:
    subparser = subparsers.add_parser("forward", help="Run forward piepline")
    subparser.add_argument(
        "bids_dir",
        type=os.path.abspath,
        help="The root folder of a BIDS valid dataset.",
    )
    subparser.add_argument(
        "output_dir",
        type=os.path.abspath,
        help="The output path for the outcomes of preprocessing and visual reports.",
    )
    subparser.add_argument(
        "analysis_level",
        help="Possible choices: participant \n"\
             "Processing stage to be run, only “participant” in the case of meegpype-forward.",
    )
    subparser.add_argument(
        "--participant-label", "--participant_label",
        nargs='+',
        help="A space delimited list of participant identifiers or a single identifier (the sub- prefix can be removed).",
    )
    subparser.add_argument(
        "-w", "--work-dir",
        type=os.path.abspath,
        help="Path where intermediate results should be stored.",
    )
    subparser.add_argument(
        "--surface-src", "--surface-src",
        action="store_true",
        help="Use a surface source distribution.",
    )
    subparser.add_argument(
        "--volume-src", "--volume-src",
        action="store_true",
        help="Use a volumetric source distribution.",
    )
    subparser.add_argument(
        "--pos", "--position",
        type=int,
        default=5,
        help="Positions to use for sources. A grid will be constructed with the spacing given by pos in mm, generating a volume source space"
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
        "--apptainer",
        action="store_true",
        help="Use apptainer instead of docker.",
    )
    return(subparser)


def run(args, unknown_args) -> None:
    """Run forward() command."""

    apptainer = args.apptainer
    if apptainer:
        command = ['apptainer', 'exec', '--cleanenv', "--containall", "--writable-tmpfs"]
    else:
        command = ['docker', 'run', '--rm']
    main_args = []

    # bids_dir
    bids_dir = args.bids_dir
    if not os.path.exists(bids_dir):
        raise FileNotFoundError(f"BIDS directory {bids_dir} does not exist.")

    if apptainer:
        command.extend(["-B", f"{bids_dir}:/data"])
    else:
        command.extend(["-v", f"{bids_dir}:/data"])
    main_args.extend(["/data"])

    # output_dir
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if apptainer:
        command.extend(["-B", f"{output_dir}:/out"])
    else:
        command.extend(["-v", f"{output_dir}:/out"])
    main_args.extend(["/out"])

    # work_dir
    work_dir = args.work_dir
    if work_dir is not None:
        if not os.path.exists(work_dir):
            os.makedirs(work_dir, exist_ok=True)
    else:
        work_dir = tempfile.mkdtemp(prefix="meegpype_workdir_")
    if apptainer:
        command.extend(["-B", f"{work_dir}:/scratch"])
    else:
        command.extend(["-v", f"{work_dir}:/scratch"])
    main_args.extend(["--work-dir", "/scratch"])

    # templateflow_dir
    templateflow_dir = tempfile.mkdtemp(prefix="meegpype_workdir_")
    if apptainer:
        command.extend(["-B", f"{templateflow_dir}:/opt/templateflow"])
        command.extend(["--env", "TEMPLATEFLOW_HOME=/opt/templateflow"])

    # fs-license-file
    fs_license_file = args.fs_license_file
    if fs_license_file is not None:
        if not os.path.exists(fs_license_file):
            raise FileNotFoundError(f"FreeSurfer license file {fs_license_file} does not exist.")
        if apptainer:
            command.extend(["-B", f"{fs_license_file}:/opt/freesurfer/license.txt"])
            command.extend(["--env", "FS_LICENSE=/opt/freesurfer/license.txt"])
        else:
            command.extend(["-v", f"{fs_license_file}:/opt/freesurfer/license.txt"])

    # analysis_level
    analysis_level = args.analysis_level
    main_args.extend([analysis_level])

    # participant_label
    participant_label = args.participant_label
    if participant_label is not None:
        unknown_args.extend(["--participant-label"])
        unknown_args.extend(participant_label)

    # surface-src
    if args.surface_src:
        unknown_args.extend(["--surface-src"])

    # volume-src
    if args.volume_src:
        unknown_args.extend(["--volume-src"])

    # pos
    if args.pos:
        unknown_args.extend(["--pos", str(args.pos)])

    # nprocs
    if args.nprocs:
        unknown_args.extend(["--nprocs", str(args.nprocs)])

    # image
    if apptainer:
        docker_image = "docker://" + DOCKER_IMAGE
    else:
        docker_image = DOCKER_IMAGE
    command.extend([docker_image])

    # Command
    if apptainer:
        command.extend(["/usr/local/bin/entrypoint.sh"])
    command.extend(["meegpype-forward"])
    command.extend(main_args)
    command.extend(unknown_args)

    # Run
    print(f"Running command: { ' '.join(command) }")
    ret = subprocess.run(command)
    return ret
