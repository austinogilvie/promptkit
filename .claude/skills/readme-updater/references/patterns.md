# Detection Patterns

Regex patterns and heuristics for detecting project changes that require README updates.

## Table of Contents
- [Environment Variable Patterns](#environment-variable-patterns)
- [Dependency File Patterns](#dependency-file-patterns)
- [Feature Addition Patterns](#feature-addition-patterns)
- [Breaking Change Patterns](#breaking-change-patterns)
- [Configuration File Patterns](#configuration-file-patterns)
- [Script/Command Patterns](#scriptcommand-patterns)
- [Documentation Trigger Heuristics](#documentation-trigger-heuristics)
- [Version Detection Patterns](#version-detection-patterns)
- [Ignore Patterns](#ignore-patterns)

---

## Environment Variable Patterns

### JavaScript/TypeScript
```regex
process\.env\.([A-Z_][A-Z0-9_]*)
process\.env\[['"]([A-Z_][A-Z0-9_]*)['"]\]
```

### Python
```regex
os\.environ\[['"]([A-Z_][A-Z0-9_]*)['"]\]
os\.environ\.get\(['"]([A-Z_][A-Z0-9_]*)['"]
os\.getenv\(['"]([A-Z_][A-Z0-9_]*)['"]
```

### Rust
```regex
std::env::var\(['"]([A-Z_][A-Z0-9_]*)['"]
env::var\(['"]([A-Z_][A-Z0-9_]*)['"]
```

### Go
```regex
os\.Getenv\(['"]([A-Z_][A-Z0-9_]*)['"]
os\.LookupEnv\(['"]([A-Z_][A-Z0-9_]*)['"]
```

### Ruby
```regex
ENV\[['"]([A-Z_][A-Z0-9_]*)['"]\]
ENV\.fetch\(['"]([A-Z_][A-Z0-9_]*)['"]
```

### Shell/Bash
```regex
\$\{([A-Z_][A-Z0-9_]*)\}
\$([A-Z_][A-Z0-9_]*)
```

---

## Dependency File Patterns

### Identify Project Type by File

| File | Project Type |
|------|--------------|
| `package.json` | Node.js |
| `requirements.txt` | Python (pip) |
| `pyproject.toml` | Python (modern) |
| `Pipfile` | Python (pipenv) |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `Gemfile` | Ruby |
| `pom.xml` | Java (Maven) |
| `build.gradle` | Java (Gradle) |
| `*.csproj` | .NET |
| `composer.json` | PHP |

### Parse Dependencies

#### package.json
```regex
"dependencies"\s*:\s*\{([^}]+)\}
"devDependencies"\s*:\s*\{([^}]+)\}
```

#### requirements.txt
```regex
^([a-zA-Z0-9_-]+)([=<>!~]+[0-9.]+)?
```

#### pyproject.toml
```regex
dependencies\s*=\s*\[(.*?)\]
```

---

## Feature Addition Patterns

### New API Endpoints

#### Express.js
```regex
app\.(get|post|put|patch|delete)\s*\(\s*['"]([^'"]+)['"]
router\.(get|post|put|patch|delete)\s*\(\s*['"]([^'"]+)['"]
```

#### FastAPI
```regex
@app\.(get|post|put|patch|delete)\s*\(\s*['"]([^'"]+)['"]
@router\.(get|post|put|patch|delete)\s*\(\s*['"]([^'"]+)['"]
```

#### Flask
```regex
@app\.route\s*\(\s*['"]([^'"]+)['"]
@blueprint\.route\s*\(\s*['"]([^'"]+)['"]
```

### New CLI Commands

#### Commander.js
```regex
\.command\s*\(\s*['"]([^'"]+)['"]
```

#### Click (Python)
```regex
@click\.command\s*\(\s*(?:name\s*=\s*)?['"]?([^'")\s]+)
@click\.group\s*\(\s*(?:name\s*=\s*)?['"]?([^'")\s]+)
```

#### argparse (Python)
```regex
add_subparsers.*?add_parser\s*\(\s*['"]([^'"]+)['"]
```

---

## Breaking Change Patterns

### Commit Message Patterns

```regex
^BREAKING(\s+CHANGE)?:
^[a-z]+(\([^)]+\))?!:
```

### Semver Major Version Bump
```regex
"version"\s*:\s*"([0-9]+)\.
```
Compare extracted major version with previous to detect bump.

### Deprecation Markers

```regex
@deprecated
\[deprecated\]
DEPRECATED
# DEPRECATED:
// DEPRECATED:
```

---

## Configuration File Patterns

### Config Files to Monitor

| Pattern | Section to Update |
|---------|-------------------|
| `.env.example` | Configuration |
| `config/*.json` | Configuration |
| `*.config.js` | Configuration |
| `*.config.ts` | Configuration |
| `docker-compose.yml` | Deployment |
| `Dockerfile` | Deployment/Prerequisites |
| `.github/workflows/*` | Development |
| `Makefile` | Usage/Development |

### New Config Keys

#### JSON config
```regex
"([a-zA-Z_][a-zA-Z0-9_]*)"\s*:
```

#### YAML config
```regex
^(\s*)([a-zA-Z_][a-zA-Z0-9_]*):\s*
```

---

## Script/Command Patterns

### package.json scripts
```regex
"scripts"\s*:\s*\{([^}]+)\}
```

Extract individual scripts:
```regex
"([a-zA-Z:_-]+)"\s*:\s*"([^"]+)"
```

### Makefile targets
```regex
^([a-zA-Z_][a-zA-Z0-9_-]*):\s*
```

### pyproject.toml scripts
```regex
\[project\.scripts\](.*?)(?=\[|$)
\[tool\.poetry\.scripts\](.*?)(?=\[|$)
```

---

## Documentation Trigger Heuristics

### High Priority (Immediate Update Needed)
- New files in `src/cli/` or `bin/` → Update Usage section
- Changes to `.env.example` → Update Configuration section
- New files in `src/api/` or `routes/` → Update API/Usage section
- `BREAKING` in recent commits → Update Migration/Changelog section

### Medium Priority (Should Update Soon)
- New directories in `src/` → Consider Architecture section
- Changes to CI/CD files → Update Development section
- New test directories → Update Testing section
- Dockerfile changes → Update Deployment section

### Low Priority (Optional Update)
- Internal refactoring → Usually no update needed
- Dev dependency changes → Rarely needs documentation
- Style/lint config changes → Rarely needs documentation

---

## Version Detection Patterns

### Semantic Version
```regex
([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?
```

### Common Version Locations

| Project Type | File | Pattern |
|--------------|------|---------|
| Node.js | `package.json` | `"version": "X.Y.Z"` |
| Python | `pyproject.toml` | `version = "X.Y.Z"` |
| Python | `__version__.py` | `__version__ = "X.Y.Z"` |
| Rust | `Cargo.toml` | `version = "X.Y.Z"` |
| Go | `go.mod` | Module version in path |

---

## Ignore Patterns

Files/directories to skip when scanning:

```
node_modules/
venv/
.venv/
__pycache__/
dist/
build/
.git/
coverage/
.pytest_cache/
.mypy_cache/
*.min.js
*.bundle.js
vendor/
```
