#!/usr/bin/env python3
"""
check-readme.py - Analyze README.md against project state

Compares the current README.md with project files to identify
missing or outdated sections. Outputs structured suggestions.

Usage:
    python check-readme.py [project_root]

If project_root is not specified, uses current directory.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional


def detect_project_type(root: Path) -> str:
    """Detect the primary project type based on config files."""
    indicators = {
        "node": ["package.json"],
        "python": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"],
        "rust": ["Cargo.toml"],
        "go": ["go.mod"],
        "ruby": ["Gemfile"],
        "java": ["pom.xml", "build.gradle"],
        "dotnet": ["*.csproj", "*.sln"],
    }

    for project_type, files in indicators.items():
        for pattern in files:
            if "*" in pattern:
                if list(root.glob(pattern)):
                    return project_type
            elif (root / pattern).exists():
                return project_type

    return "unknown"


def extract_dependencies(root: Path) -> dict:
    """Extract dependencies from various package managers."""
    deps = {"runtime": [], "dev": []}

    # Node.js
    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            deps["runtime"].extend(data.get("dependencies", {}).keys())
            deps["dev"].extend(data.get("devDependencies", {}).keys())
        except (json.JSONDecodeError, IOError):
            pass

    # Python - requirements.txt
    requirements = root / "requirements.txt"
    if requirements.exists():
        try:
            for line in requirements.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name (before ==, >=, etc.)
                    pkg = re.split(r"[=<>!\[]", line)[0].strip()
                    if pkg:
                        deps["runtime"].append(pkg)
        except IOError:
            pass

    # Python - pyproject.toml (basic parsing)
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            # Simple regex to find dependencies array
            dep_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if dep_match:
                dep_str = dep_match.group(1)
                for match in re.finditer(r'"([^"]+)"', dep_str):
                    pkg = re.split(r"[=<>!\[]", match.group(1))[0].strip()
                    if pkg:
                        deps["runtime"].append(pkg)
        except IOError:
            pass

    return deps


def extract_env_vars(root: Path) -> set:
    """Find environment variables used in source code."""
    env_vars = set()

    # Patterns for different languages
    patterns = [
        r'process\.env\.([A-Z_][A-Z0-9_]*)',  # Node.js
        r'os\.environ\[[\'"](.*?)[\'"]\]',     # Python
        r'os\.getenv\([\'"](.*?)[\'"]\)',      # Python
        r'env::var\([\'"](.*?)[\'"]\)',        # Rust
        r'os\.Getenv\([\'"](.*?)[\'"]\)',      # Go
    ]

    # Common source directories
    source_dirs = ["src", "lib", "app", ".", "scripts"]
    extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".rs", ".go", ".rb"]

    for src_dir in source_dirs:
        dir_path = root / src_dir if src_dir != "." else root
        if not dir_path.exists():
            continue

        for ext in extensions:
            for file_path in dir_path.rglob(f"*{ext}"):
                # Skip node_modules, venv, etc.
                if any(skip in str(file_path) for skip in ["node_modules", "venv", ".venv", "__pycache__", "dist", "build"]):
                    continue

                try:
                    content = file_path.read_text()
                    for pattern in patterns:
                        for match in re.finditer(pattern, content):
                            env_vars.add(match.group(1))
                except (IOError, UnicodeDecodeError):
                    pass

    # Also check .env.example
    env_example = root / ".env.example"
    if env_example.exists():
        try:
            for line in env_example.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    var_name = line.split("=")[0].strip()
                    env_vars.add(var_name)
        except IOError:
            pass

    return env_vars


def parse_readme_sections(readme_path: Path) -> dict:
    """Parse README into sections by heading."""
    sections = {}

    if not readme_path.exists():
        return sections

    try:
        content = readme_path.read_text()
    except IOError:
        return sections

    current_section = "intro"
    current_content = []

    for line in content.splitlines():
        # Match ## or # headings
        heading_match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if heading_match:
            # Save previous section
            if current_content:
                sections[current_section.lower()] = "\n".join(current_content).strip()

            current_section = heading_match.group(2).strip()
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_content:
        sections[current_section.lower()] = "\n".join(current_content).strip()

    return sections


def check_documented_env_vars(readme_sections: dict, code_env_vars: set) -> list:
    """Check if environment variables from code are documented."""
    missing = []

    # Look for env vars in configuration/environment sections
    config_sections = ["configuration", "environment variables", "environment", "config", "setup"]

    readme_text = ""
    for section_name in config_sections:
        for key, content in readme_sections.items():
            if section_name in key.lower():
                readme_text += content + "\n"

    # Also check the full readme if no specific section found
    if not readme_text:
        readme_text = "\n".join(readme_sections.values())

    for var in code_env_vars:
        if var not in readme_text:
            missing.append(var)

    return missing


def suggest_updates(root: Path) -> list:
    """Generate update suggestions by comparing project state to README."""
    suggestions = []
    readme_path = root / "README.md"

    if not readme_path.exists():
        suggestions.append({
            "type": "missing",
            "section": "README.md",
            "message": "No README.md found. Consider creating one.",
            "priority": "high"
        })
        return suggestions

    sections = parse_readme_sections(readme_path)
    project_type = detect_project_type(root)
    deps = extract_dependencies(root)
    env_vars = extract_env_vars(root)

    # Check for missing sections
    recommended_sections = {
        "installation": "installation",
        "usage": "usage",
        "prerequisites": "prerequisites",
    }

    section_keys = [k.lower() for k in sections.keys()]

    for section, name in recommended_sections.items():
        found = any(section in key for key in section_keys)
        if not found:
            suggestions.append({
                "type": "missing_section",
                "section": name.title(),
                "message": f"Consider adding a {name.title()} section",
                "priority": "medium"
            })

    # Check environment variables
    if env_vars:
        missing_env = check_documented_env_vars(sections, env_vars)
        if missing_env:
            suggestions.append({
                "type": "missing_env_vars",
                "section": "Configuration",
                "message": f"Undocumented environment variables: {', '.join(sorted(missing_env))}",
                "priority": "high",
                "details": list(sorted(missing_env))
            })

    # Check if .env.example exists but not documented
    if (root / ".env.example").exists():
        config_mentioned = any("env" in key.lower() for key in section_keys)
        if not config_mentioned:
            suggestions.append({
                "type": "missing_reference",
                "section": "Configuration",
                "message": ".env.example exists but may not be referenced in README",
                "priority": "medium"
            })

    # Check for common missing elements based on project type
    if project_type == "node":
        if deps["runtime"] and "installation" not in str(section_keys):
            suggestions.append({
                "type": "missing_section",
                "section": "Installation",
                "message": "Node.js project with dependencies but no installation instructions",
                "priority": "high"
            })

    return suggestions


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
    else:
        root = Path.cwd()

    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    suggestions = suggest_updates(root)

    if not suggestions:
        print("README appears to be up to date!")
        print(f"\nProject type: {detect_project_type(root)}")
        return

    print(f"README Update Suggestions for: {root}")
    print(f"Project type: {detect_project_type(root)}")
    print("=" * 50)

    # Group by priority
    high = [s for s in suggestions if s.get("priority") == "high"]
    medium = [s for s in suggestions if s.get("priority") == "medium"]
    low = [s for s in suggestions if s.get("priority") == "low"]

    if high:
        print("\n[HIGH PRIORITY]")
        for s in high:
            print(f"  - [{s['section']}] {s['message']}")
            if "details" in s:
                for detail in s["details"]:
                    print(f"      * {detail}")

    if medium:
        print("\n[MEDIUM PRIORITY]")
        for s in medium:
            print(f"  - [{s['section']}] {s['message']}")

    if low:
        print("\n[LOW PRIORITY]")
        for s in low:
            print(f"  - [{s['section']}] {s['message']}")

    # Output as JSON for programmatic use
    print("\n" + "=" * 50)
    print("JSON output:")
    print(json.dumps(suggestions, indent=2))


if __name__ == "__main__":
    main()
