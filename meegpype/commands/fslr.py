import argparse
from ..pipelines.fslr import run_fslr_pipeline


def run() -> None:
    """Run forward() command."""
    parser = argparse.ArgumentParser(
        prog=f"{__package__.split('.')[0]}-fslr", description="run_fslr_pipeline"
    )
    parser.add_argument(
        "subject",
        help="The subject ID to process (e.g., sub-01).",
    )
    parser.add_argument(
        "subjects_dir",
        help="The Freesurfer subjects directory containing the subject's recon-all outputs.",
    )
    parser.add_argument(
        "output_dir",
        help="The output path for the outcomes of preprocessing and visual reports.",
    )
    parser.add_argument(
        "--atlas",
        help="The atlas to use for labelling (e.g., subparc374).",
    )
    parser.add_argument(
        "-w", "--work-dir",
        help="Path where intermediate results should be stored.",
    )
    parser.add_argument(
        "--nprocs", "--nthreads", "--n_cpus", "--n-cpus",
        default=1,
        type=int,
        help="Maximum number of threads across all processes.",

    )
    args = parser.parse_args()

    run_fslr_pipeline(subject=args.subject, subjects_dir=args.subjects_dir, output_dir=args.output_dir, atlas=args.atlas, work_dir=args.work_dir, n_procs=args.nprocs)
