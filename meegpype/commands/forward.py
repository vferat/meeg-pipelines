import argparse

from ..pipelines.forward import run_forward_pipeline

def run() -> None:
    """Run forward() command."""
    parser = argparse.ArgumentParser(
        prog=f"{__package__.split('.')[0]}-forward", description="run_forward_pipeline"
    )
    parser.add_argument(
        "bids_dir",
        help="The root folder of a BIDS valid dataset.",
    )
    parser.add_argument(
        "output_dir",
        help="The output path for the outcomes of preprocessing and visual reports.",
    )
    parser.add_argument(
        "analysis_level",
        help="Possible choices: participant \n"\
             "Processing stage to be run, only “participant” in the case of meegpype-forward.",
    )
    parser.add_argument(
        "--participant-label", "--participant_label",
        nargs='+',
        help="A space delimited list of participant identifiers or a single identifier (the sub- prefix can be removed).",
    )
    parser.add_argument(
        "-w", "--work-dir",
        help="Path where intermediate results should be stored.",
    )
    parser.add_argument(
        "--surface-src", "--surface-src",
        action="store_true",
        help="Use a surface source distribution.",
    )
    parser.add_argument(
        "--volume-src", "--volume-src",
        action="store_true",
        help="Use a volumetric source distribution.",
    )
    parser.add_argument(
        "--pos", "--position",
        type=int,
        default=5,
        help="Positions to use for sources. A grid will be constructed with the spacing given by pos in mm, generating a volume source space"
    )
    parser.add_argument(
        "--nprocs", "--nthreads", "--n_cpus", "--n-cpus",
        default=1,
        type=int,
        help="Maximum number of threads across all processes.",

    )
    args = parser.parse_args()

    run_forward_pipeline(bids_root=args.bids_dir, output_dir=args.output_dir, subjects=args.participant_label, work_dir=args.work_dir,
                         volume_src=args.volume_src, surface_src=args.surface_src, pos=args.pos, n_procs=args.nprocs)
