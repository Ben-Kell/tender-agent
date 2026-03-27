"""Command-line entry point for the tender-agent."""

import argparse

from app.workflow import run_workflow


def main() -> None:
    """Parse CLI arguments and run the tender response workflow."""
    parser = argparse.ArgumentParser(
        prog="tender-agent",
        description="AI-assisted tender response agent for government and defence procurement.",
    )
    parser.add_argument(
        "rft_id",
        help="RFT identifier for the tender to process (e.g. RFT-123).",
    )
    args = parser.parse_args()
    run_workflow(args.rft_id)


if __name__ == "__main__":
    main()
