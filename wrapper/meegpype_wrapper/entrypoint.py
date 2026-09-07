import argparse
from .forward import add_parser as forward_add_parser
from .forward import run as run_forward
from .fslr import add_parser as fslr_add_parser
from .fslr import run as run_fslr
from .fslabelling import add_parser as fslabelling_add_parser
from .fslabelling import run as run_fslabelling


def run() -> None:
    parser = argparse.ArgumentParser(
        prog="meegpype-wrapper", description="Run meegpype-wrapper"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    forward_add_parser(subparsers)
    fslr_add_parser(subparsers)
    fslabelling_add_parser(subparsers)

    args, unknown_args = parser.parse_known_args()

    if args.command == "forward":
        run_forward(args, unknown_args)
    elif args.command == "fslr":
        run_fslr(args, unknown_args)
    elif args.command == "fslabelling":
        run_fslabelling(args, unknown_args)
    else:
        parser.print_help()
