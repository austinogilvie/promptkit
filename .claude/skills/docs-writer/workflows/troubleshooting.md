# Troubleshooting Guide Workflow

## Trigger

User asks for troubleshooting documentation, FAQ, or problem-solving guides.

## Process

### Step 1: Identify Common Issues

Sources for common issues:
- Error handling code (catch blocks, error types)
- GitHub issues (if accessible)
- Existing documentation
- Configuration validation
- Known limitations

### Step 2: Categorize Problems

Organize issues by:
- Installation problems
- Configuration issues
- Runtime errors
- Performance problems
- Integration failures

### Step 3: Create Structure

```markdown
# Troubleshooting Guide

## Quick Diagnostics

Before diving into specific issues, run these checks:

```bash
# Check version
[command] --version

# Verify configuration
[command] config validate

# Test connectivity
[command] health
```

## Common Issues

### Installation

#### [Issue: Package installation fails]
**Symptoms**: Error message "..."
**Cause**: Missing system dependency
**Solution**:
```bash
# Install missing dependency
[command]
```

### Configuration

#### [Issue: Configuration not found]
**Symptoms**: "Config file not found" error
**Cause**: Missing or mislocated config file
**Solution**:
1. Check if config exists: `ls ~/.config/[app]/`
2. Create default config: `[app] init`
3. Verify location matches expected path

### Runtime

#### [Issue: Connection refused]
**Symptoms**: "ECONNREFUSED" or "Connection refused"
**Cause**: Service not running or wrong port
**Solution**:
1. Verify service is running: `ps aux | grep [service]`
2. Check port: `lsof -i :[port]`
3. Verify configuration matches running service

### Performance

#### [Issue: Slow response times]
**Symptoms**: Requests take > 5 seconds
**Possible Causes**:
- Database connection issues
- Missing indexes
- Memory pressure
**Diagnostic Steps**:
1. Check database connectivity
2. Review slow query logs
3. Monitor memory usage

## Error Reference

| Error Code | Message | Cause | Solution |
|------------|---------|-------|----------|
| E001 | ... | ... | ... |
| E002 | ... | ... | ... |

## Getting Help

If your issue isn't listed here:

1. **Search existing issues**: [link to issues]
2. **Check logs**: `[app] logs --tail 100`
3. **Enable debug mode**: `[app] --debug`
4. **Report a bug**: [link to report template]

When reporting issues, include:
- Version: `[app] --version`
- OS: `uname -a`
- Configuration (sanitized)
- Full error message
- Steps to reproduce
```

### Step 4: Write Each Issue Entry

For each issue, follow this template:

```markdown
#### [Descriptive Issue Title]

**Symptoms**
What the user sees/experiences. Include exact error messages.

**Cause**
Why this happens. Be specific.

**Solution**
Step-by-step fix:
1. First step
2. Second step
3. Verification step

**Prevention**
How to avoid this in the future (if applicable).
```

### Step 5: Add Diagnostic Tools

```markdown
## Diagnostic Commands

### Check System Status
```bash
[app] status
```
Expected output when healthy:
```text
Status: Running
Database: Connected
Cache: Active
```

### Validate Configuration
```bash
[app] config validate
```
Expected output:
```text
Configuration valid
```

### View Logs
```bash
# Last 100 lines
[app] logs --tail 100

# Filter errors
[app] logs | grep ERROR

# Follow live
[app] logs -f
```

### Health Check
```bash
curl http://localhost:[port]/health
```
Expected response:
```json
{"status": "ok", "version": "x.y.z"}
```
```

### Step 6: Create FAQ Section

```markdown
## Frequently Asked Questions

### General

**Q: How do I check my version?**
A: Run `[app] --version`

**Q: Where are logs stored?**
A: Logs are stored in `~/.local/share/[app]/logs/`

### Configuration

**Q: Can I use environment variables instead of config file?**
A: Yes, prefix any config key with `[APP]_`. Example: `[APP]_PORT=3000`

### Troubleshooting

**Q: How do I reset to defaults?**
A: Remove config directory and reinitialize:
```bash
rm -rf ~/.config/[app]
[app] init
```
```

## Output Options

**Single file**: `docs/troubleshooting.md`
- Good for smaller projects
- Easy to search

**Multi-file**:
- `docs/troubleshooting/index.md` - Overview and quick diagnostics
- `docs/troubleshooting/installation.md` - Install issues
- `docs/troubleshooting/configuration.md` - Config issues
- `docs/troubleshooting/runtime.md` - Runtime errors
- `docs/troubleshooting/faq.md` - FAQ
