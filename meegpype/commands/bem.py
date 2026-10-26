import argparse

from ..pipelines.bem import run_bem_pipeline, BEM_METHODS


def run() -> None:
    """Run bem() command."""
    parser = argparse.ArgumentParser(
        prog=f"{__package__.split('.')[0]}-bem", description="run_bem_pipeline"
    )
    parser.add_argument(
        "subject",
        help="The subject ID to process (e.g., sub-01).",
    )
    parser.add_argument(
        "subjects_dir",
        help="The Freesurfer subjects directory containing the subject's recon-all outputs. "
             "The BEM surfaces are written to subjects_dir/subject/bem.",
    )
    parser.add_argument(
        "--bem-method", "--method",
        choices=BEM_METHODS,
        default="basic",
        help="Method to use for BEM surface generation. Default is 'basic'.",
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
    run_bem_pipeline(subject=args.subject,
                     subjects_dir=args.subjects_dir,
                     method=args.bem_method,
                     work_dir=args.work_dir,
                     n_procs=args.nprocs)
