#!/usr/bin/env python3
"""Interactive first-run initializer for .pencil-normalize.config.json."""

import json
import shutil
import sys
from pathlib import Path

CONFIG_FILENAME = ".pencil-normalize.config.json"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def minimal_config(scan_path: str = "src") -> dict:
    """Return a minimal starter config."""
    return {
        "version": 1,
        "scan_path": scan_path,
        "css_var_map": {},
        "tailwind_literal_map": {},
    }


def parse_args(argv: list[str]) -> dict:
    """Parse CLI arguments from sys.argv (no external deps)."""
    opts = {
        "non_interactive": False,
        "scan_path": "src",
        "template": None,
    }
    for arg in argv[1:]:
        if arg == "--non-interactive":
            opts["non_interactive"] = True
        elif arg.startswith("--scan-path="):
            opts["scan_path"] = arg.split("=", 1)[1]
        elif arg.startswith("--template="):
            opts["template"] = arg.split("=", 1)[1]
        else:
            print(f"Unknown argument: {arg}", file=sys.stderr)
            print(
                "Usage: init_config.py [--non-interactive] "
                "[--scan-path=<path>] [--template=<name>]",
                file=sys.stderr,
            )
            sys.exit(1)
    return opts


def load_template(name: str, scan_path: str) -> dict:
    """Load a template file and override its scan_path."""
    template_file = TEMPLATES_DIR / f"pencil-normalize.config.{name}.json"
    if not template_file.exists():
        available = [
            p.stem.replace("pencil-normalize.config.", "")
            for p in TEMPLATES_DIR.glob("pencil-normalize.config.*.json")
        ]
        print(f"Template '{name}' not found at {template_file}", file=sys.stderr)
        if available:
            print(f"Available templates: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)
    with open(template_file, "r") as f:
        config = json.load(f)
    config["scan_path"] = scan_path
    return config


def prompt_user(opts: dict) -> dict:
    """Run the interactive prompts and return final config."""
    print(f"Initializing {CONFIG_FILENAME}...")

    scan_path = input(f"Default scan path [{opts['scan_path']}]: ").strip()
    if not scan_path:
        scan_path = opts["scan_path"]

    template_choice = input("Seed from template? (minimal/cloakling/none) [none]: ").strip().lower()
    if not template_choice or template_choice == "none":
        return minimal_config(scan_path)

    return load_template(template_choice, scan_path)


def main() -> None:
    opts = parse_args(sys.argv)
    config_path = Path.cwd() / CONFIG_FILENAME

    if config_path.exists():
        if opts["non_interactive"]:
            print(f"{CONFIG_FILENAME} already exists. Aborting.", file=sys.stderr)
            sys.exit(1)
        answer = input(f"{CONFIG_FILENAME} already exists. Overwrite? [y/N]: ").strip().lower()
        if answer != "y":
            print("Aborted.")
            sys.exit(0)

    if opts["non_interactive"]:
        if opts["template"]:
            config = load_template(opts["template"], opts["scan_path"])
        else:
            config = minimal_config(opts["scan_path"])
    else:
        config = prompt_user(opts)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    print(f"Created {CONFIG_FILENAME}")
    print(f"Remember to: git add {CONFIG_FILENAME}")


if __name__ == "__main__":
    main()
