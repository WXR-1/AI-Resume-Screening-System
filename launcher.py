"""
Launcher for AI Resume Screening System
Supports GUI, CLI, and email configuration modes
"""
import sys
import argparse
import warnings
import logging
from pathlib import Path


def configure_warning_suppression():
    warnings.filterwarnings(
        "ignore",
        message=r"Could not get FontBBox from font descriptor because None cannot be parsed as 4 floats"
    )
    for logger_name in ("reportlab", "fontTools", "matplotlib"):
        logging.getLogger(logger_name).setLevel(logging.ERROR)


def launch_gui():
    """Launch the GUI interface"""
    try:
        from gui import main
        main()
    except ImportError:
        print("Error: tkinter is required for GUI mode")
        print("Please install tkinter or run in CLI mode with: python main.py --role-file <file>")
        sys.exit(1)


def launch_mail_config():
    """Launch the mail configuration setup"""
    try:
        from mail_config import main
        main()
    except ImportError as e:
        print("Error: Required packages not found for mail configuration")
        print("Please install: pip install python-dotenv")
        sys.exit(1)


def launch_cli(args):
    """Launch the CLI interface"""
    from main import parse_args, main
    sys.argv = [sys.argv[0]] + args
    parsed_args = parse_args()
    main()


def main():
    configure_warning_suppression()
    parser = argparse.ArgumentParser(
        description="AI Resume Screening System - Choose between GUI, CLI, or Configuration"
    )
    parser.add_argument(
        "--mode",
        choices=["gui", "cli", "config"],
        default="gui",
        help="Launch mode: 'gui' for graphical interface (default), 'cli' for command-line, or 'config' for email setup"
    )
    parser.add_argument(
        "--role-file",
        help="Path to the role description text file (CLI mode only)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not send email, only simulate the workflow (CLI mode only)"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the default ollama model (CLI mode only)"
    )
    
    # If no arguments provided, launch GUI
    if len(sys.argv) == 1:
        print("Launching GUI interface...")
        launch_gui()
    else:
        args = parser.parse_args()
        
        if args.mode == "config":
            print("📧 Launching Email Configuration Setup...")
            launch_mail_config()
        elif args.mode == "gui":
            print("🎨 Launching GUI interface...")
            launch_gui()
        else:
            # CLI mode
            if not args.role_file:
                print("Error: --role-file is required for CLI mode")
                parser.print_help()
                sys.exit(1)
            
            print("💻 Launching CLI interface...")
            cli_args = ["--role-file", args.role_file]
            if args.dry_run:
                cli_args.append("--dry-run")
            if args.model:
                cli_args.extend(["--model", args.model])
            
            launch_cli(cli_args)


if __name__ == "__main__":
    main()
