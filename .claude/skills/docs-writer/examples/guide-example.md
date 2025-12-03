# Example: CLI Tool User Guide

This example demonstrates the docs-writer agent's user guide output.

---

# DataSync CLI User Guide

DataSync is a command-line tool for synchronizing data between local files and cloud storage with encryption and compression support.

## Quick Start

Get DataSync running in under 2 minutes.

### 1. Install

```bash
brew install datasync
```

### 2. Configure

```bash
datasync init
```

Enter your cloud credentials when prompted:
```text
? Cloud provider: AWS S3
? Access Key ID: ********
? Secret Access Key: ********
? Default bucket: my-backup-bucket
? Region: us-east-1
Configuration saved to ~/.config/datasync/config.yaml
```

### 3. Sync Your First File

```bash
datasync push ./data.csv
```

Output:
```text
Uploading data.csv...
✓ Uploaded: data.csv (1.2 MB) → s3://my-backup-bucket/data.csv
```

**Next**: See [Installation](#installation) for alternative install methods.

---

## Installation

### System Requirements

- **macOS**: 10.15 (Catalina) or later
- **Linux**: Ubuntu 20.04+, Debian 11+, RHEL 8+
- **Windows**: Windows 10 version 1903 or later
- **Memory**: 128 MB RAM minimum
- **Disk**: 50 MB free space

### Installation Methods

#### Homebrew (macOS/Linux)

```bash
brew install datasync
```

#### APT (Debian/Ubuntu)

```bash
curl -fsSL https://datasync.io/install.sh | sudo bash
sudo apt install datasync
```

#### Winget (Windows)

```powershell
winget install DataSync.CLI
```

#### From Binary

Download from [releases](https://github.com/example/datasync/releases):

```bash
# macOS/Linux
curl -LO https://github.com/example/datasync/releases/latest/download/datasync-linux-amd64
chmod +x datasync-linux-amd64
sudo mv datasync-linux-amd64 /usr/local/bin/datasync

# Windows (PowerShell)
Invoke-WebRequest -Uri https://github.com/example/datasync/releases/latest/download/datasync-windows-amd64.exe -OutFile datasync.exe
```

### Verify Installation

```bash
datasync --version
```

Expected output:
```text
datasync v2.1.0 (build abc123)
```

---

## Configuration

### Interactive Setup

Run the setup wizard:

```bash
datasync init
```

This creates `~/.config/datasync/config.yaml`.

### Configuration File

```yaml
# ~/.config/datasync/config.yaml

# Cloud provider settings
provider: s3
credentials:
  access_key_id: ${AWS_ACCESS_KEY_ID}
  secret_access_key: ${AWS_SECRET_ACCESS_KEY}
  region: us-east-1

# Default bucket/container
default_bucket: my-backup-bucket

# Sync options
sync:
  compression: gzip      # none, gzip, lz4
  encryption: aes-256    # none, aes-256
  delete_missing: false  # Delete remote files not in local

# Ignore patterns (gitignore syntax)
ignore:
  - "*.tmp"
  - ".git/"
  - "node_modules/"

# Logging
logging:
  level: info
  file: ~/.local/share/datasync/sync.log
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATASYNC_CONFIG` | Path to config file | `~/.config/datasync/config.yaml` |
| `AWS_ACCESS_KEY_ID` | AWS access key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - |
| `DATASYNC_BUCKET` | Override default bucket | From config |
| `DATASYNC_LOG_LEVEL` | Log level | `info` |

---

## Basic Usage

### Push Files to Cloud

Upload local files to cloud storage:

```bash
# Single file
datasync push ./report.pdf

# Directory
datasync push ./data/

# With custom destination
datasync push ./local/file.txt s3://bucket/remote/path/file.txt
```

### Pull Files from Cloud

Download files from cloud storage:

```bash
# Single file
datasync pull s3://bucket/report.pdf ./downloads/

# Directory
datasync pull s3://bucket/data/ ./local-data/

# Latest version
datasync pull s3://bucket/file.txt --latest
```

### Sync Bidirectional

Keep local and remote in sync:

```bash
# Two-way sync
datasync sync ./local-folder s3://bucket/remote-folder

# Prefer local changes
datasync sync ./local s3://bucket/remote --prefer local

# Prefer remote changes
datasync sync ./local s3://bucket/remote --prefer remote
```

### List Remote Files

```bash
# List bucket contents
datasync ls s3://bucket/

# With details
datasync ls s3://bucket/ --long

# Recursive
datasync ls s3://bucket/folder/ --recursive
```

---

## Features

### Encryption

DataSync encrypts files before upload using AES-256.

#### Enable Encryption

In config:
```yaml
sync:
  encryption: aes-256
```

Or per-command:
```bash
datasync push ./sensitive-data.csv --encrypt
```

#### Encryption Key

Set your encryption key:
```bash
# Environment variable
export DATASYNC_ENCRYPTION_KEY="your-32-character-secret-key!!"

# Or in config
encryption_key: ${DATASYNC_ENCRYPTION_KEY}
```

#### Verify Encryption

```bash
datasync inspect s3://bucket/sensitive-data.csv
```

Output:
```text
File: sensitive-data.csv
Size: 1.2 MB (encrypted: 1.4 MB)
Encryption: AES-256-GCM
Uploaded: 2024-01-15T10:30:00Z
```

---

### Compression

Reduce storage costs with compression.

#### Options

| Algorithm | Speed | Ratio | Best For |
|-----------|-------|-------|----------|
| `none` | Fastest | 1:1 | Already compressed files |
| `gzip` | Fast | 3:1 | Text, logs, JSON |
| `lz4` | Very fast | 2:1 | Large files, speed priority |

#### Usage

```bash
# Config
sync:
  compression: gzip

# Command line
datasync push ./logs/ --compress gzip
```

---

### Ignore Patterns

Skip files matching patterns (gitignore syntax).

#### In Config

```yaml
ignore:
  - "*.log"
  - "*.tmp"
  - ".git/"
  - "node_modules/"
  - "**/__pycache__/"
```

#### Ignore File

Create `.datasyncignore` in your project:

```gitignore
# Dependencies
node_modules/
vendor/
venv/

# Build outputs
dist/
build/
*.o

# Secrets
.env
*.key
credentials.json
```

---

## Advanced Usage

### Versioning

Access file versions (requires bucket versioning enabled):

```bash
# List versions
datasync versions s3://bucket/important.doc

# Download specific version
datasync pull s3://bucket/important.doc --version v2

# Restore old version
datasync restore s3://bucket/important.doc --version v1
```

### Scheduled Sync

Run sync on a schedule:

```bash
# Every hour
datasync schedule add "0 * * * *" "./docs s3://bucket/docs"

# List schedules
datasync schedule list

# Remove schedule
datasync schedule remove 1
```

### Bandwidth Limits

Control upload/download speed:

```bash
# Limit to 10 MB/s
datasync push ./large-file.zip --bandwidth 10M

# In config
sync:
  max_bandwidth: 10M
```

---

## Troubleshooting

### Connection Issues

**Problem**: `Error: connection refused`

**Solutions**:
1. Check internet connection
2. Verify credentials: `datasync auth verify`
3. Check region setting matches bucket location

### Permission Denied

**Problem**: `Error: access denied to bucket`

**Solutions**:
1. Verify IAM permissions include s3:GetObject, s3:PutObject
2. Check bucket policy allows your account
3. Ensure bucket name is correct

### Slow Uploads

**Problem**: Uploads taking too long

**Solutions**:
1. Enable compression: `--compress gzip`
2. Increase parallelism: `--parallel 10`
3. Check network bandwidth

### Getting Help

```bash
# General help
datasync --help

# Command-specific help
datasync push --help

# Verbose output for debugging
datasync push ./file.txt --verbose
```

---

## FAQ

**Q: How do I change cloud providers?**

A: Run `datasync init` again and select a different provider.

**Q: Are my credentials stored securely?**

A: Yes, credentials are stored encrypted in your config file. For additional security, use environment variables.

**Q: Can I sync to multiple buckets?**

A: Yes, specify the bucket in each command or create named profiles in config.

**Q: How do I exclude large files?**

A: Add to ignore patterns:
```yaml
ignore:
  - "*.iso"
  - "*.zip"
```

Or use size filter:
```bash
datasync push ./folder --max-size 100M
```
