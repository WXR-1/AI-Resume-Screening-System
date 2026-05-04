from __future__ import annotations

import argparse
import warnings
import logging
from pathlib import Path

from agents.orchestrator import OrchestratorAgent
from config import RESUMES_DIR


def configure_warning_suppression() -> None:
    warnings.filterwarnings(
        "ignore",
        message=r"Could not get FontBBox from font descriptor because None cannot be parsed as 4 floats"
    )
    for logger_name in ("reportlab", "fontTools", "matplotlib"):
        logging.getLogger(logger_name).setLevel(logging.ERROR)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CrewAI resume screening orchestrator")
    parser.add_argument("--role-file", required=True, help="Path to the role description text file")
    parser.add_argument("--dry-run", action="store_true", help="Do not send email, only simulate the workflow")
    parser.add_argument("--model", default=None, help="Override the default ollama model")
    return parser.parse_args()


def main() -> None:
    configure_warning_suppression()
    args = parse_args()
    role_file = Path(args.role_file)
    if not role_file.exists():
        raise SystemExit(f"Role file not found: {role_file}")

    orchestrator = OrchestratorAgent(model=args.model)
    orchestrator.run(role_file=role_file, resumes_path=Path(RESUMES_DIR), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
