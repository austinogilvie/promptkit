# User Guide Template

Use this template for user-facing documentation and tutorials.

---

# [Product Name] User Guide

## Quick Start

Get started with [Product] in under 5 minutes.

### 1. Install

```bash
# Using npm
npm install -g product-name

# Using pip
pip install product-name

# Using Homebrew
brew install product-name
```

### 2. Configure

```bash
product-name init
```

This creates a configuration file at `~/.config/product-name/config.yaml`.

### 3. Run

```bash
product-name start
```

### 4. Verify

Open http://localhost:3000 in your browser. You should see:

```
Welcome to Product Name!
```

**Next steps**: Continue to [Installation](#installation) for detailed setup options.

---

## Installation

### System Requirements

- Operating System: macOS 10.15+, Ubuntu 20.04+, Windows 10+
- Runtime: Node.js 18+ / Python 3.9+
- Memory: 512MB RAM minimum
- Disk: 100MB free space

### Installation Methods

#### Package Manager (Recommended)

**npm**:
```bash
npm install -g product-name
```

**pip**:
```bash
pip install product-name
```

**Homebrew**:
```bash
brew install product-name
```

#### From Source

```bash
git clone https://github.com/example/product-name.git
cd product-name
make install
```

### Verify Installation

```bash
product-name --version
```

Expected output:
```
product-name v1.2.3
```

---

## Configuration

### Configuration File

Default location: `~/.config/product-name/config.yaml`

```yaml
# Core settings
port: 3000
host: localhost

# Authentication
auth:
  enabled: true
  provider: local

# Database
database:
  url: postgresql://localhost:5432/mydb

# Logging
logging:
  level: info
  format: json
```

### Environment Variables

All configuration options can be set via environment variables:

| Config Key | Environment Variable | Default |
|------------|---------------------|---------|
| `port` | `PRODUCT_PORT` | 3000 |
| `host` | `PRODUCT_HOST` | localhost |
| `auth.enabled` | `PRODUCT_AUTH_ENABLED` | true |
| `logging.level` | `PRODUCT_LOG_LEVEL` | info |

### Configuration Priority

1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

---

## Basic Usage

### [Core Feature 1]

#### Overview

What this feature does and why you'd use it.

#### Usage

```bash
product-name [command] [options]
```

#### Example

```bash
product-name process --input data.csv --output results.json
```

Output:
```
Processing data.csv...
Processed 1,000 records
Results written to results.json
```

---

### [Core Feature 2]

#### Overview

What this feature does and why you'd use it.

#### Usage

[Usage instructions]

#### Example

[Working example with expected output]

---

## Features

### Feature A: [Name]

#### What It Does

Description of the feature and its benefits.

#### How to Use

Step-by-step instructions:

1. **First step**
   ```bash
   command here
   ```

2. **Second step**
   Configure the setting:
   ```yaml
   setting: value
   ```

3. **Third step**
   Verify it's working:
   ```bash
   product-name status
   ```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--option1` | What it does | value |
| `--option2` | What it does | value |

#### Tips

- Tip 1 for getting the most out of this feature
- Tip 2 for common use cases

---

### Feature B: [Name]

[Same structure as Feature A]

---

## Advanced Usage

### [Advanced Topic 1]

For power users who need [capability].

#### Prerequisites

- Completed [Basic Usage](#basic-usage)
- Understanding of [concept]

#### Instructions

[Detailed instructions for advanced usage]

---

### [Advanced Topic 2]

[Same structure]

---

## Integrations

### Integrating with [Service/Tool]

#### Prerequisites

- [Service] account
- API key from [location]

#### Setup

1. Install the integration:
   ```bash
   product-name integrations add service-name
   ```

2. Configure credentials:
   ```bash
   product-name config set integrations.service.api_key YOUR_KEY
   ```

3. Verify connection:
   ```bash
   product-name integrations test service-name
   ```

---

## Troubleshooting

### Common Issues

#### [Issue: Product won't start]

**Symptoms**: Error message "Cannot bind to port 3000"

**Cause**: Port already in use

**Solution**:
```bash
# Find what's using the port
lsof -i :3000

# Use a different port
product-name start --port 3001
```

#### [Issue: Authentication failing]

**Symptoms**: "Invalid credentials" error

**Cause**: Expired or incorrect API key

**Solution**:
1. Verify your API key: `product-name auth verify`
2. Regenerate if needed: `product-name auth refresh`

### Getting Help

- **Documentation**: https://docs.example.com
- **Community**: https://community.example.com
- **Issues**: https://github.com/example/product-name/issues

When reporting issues, include:
- Version: `product-name --version`
- OS: `uname -a`
- Error message (full output)
- Steps to reproduce

---

## FAQ

### General

**Q: How do I update to the latest version?**

A: Use your package manager:
```bash
npm update -g product-name
# or
pip install --upgrade product-name
```

**Q: Where is data stored?**

A: By default, data is stored in `~/.local/share/product-name/`

### Configuration

**Q: Can I use multiple configuration files?**

A: Yes, use the `--config` flag:
```bash
product-name --config ./my-config.yaml start
```

### Troubleshooting

**Q: How do I reset to defaults?**

A:
```bash
product-name config reset
```

---

## Glossary

| Term | Definition |
|------|------------|
| **Term 1** | Definition of term 1 |
| **Term 2** | Definition of term 2 |
