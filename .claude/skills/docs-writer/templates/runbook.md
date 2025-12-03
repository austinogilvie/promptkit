# Operational Runbook Template

Use this template for deployment guides, operational procedures, and incident response.

---

# [System/Service] Runbook

**Last Updated**: YYYY-MM-DD
**Owner**: [Team/Person]
**On-Call**: [Rotation or contact info]

## Overview

Brief description of the system/service this runbook covers.

### Key Information

| Item | Value |
|------|-------|
| Service URL | https://service.example.com |
| Repository | https://github.com/org/repo |
| Dashboard | [Link to monitoring dashboard] |
| Logs | [Link to log aggregation] |
| Alerts | [Link to alert configuration] |

### Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Server    │────▶│  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Cache     │
                    └─────────────┘
```

---

## Deployment

### Prerequisites

- [ ] Access to deployment environment
- [ ] Required credentials configured
- [ ] Approval from [role]

### Standard Deployment

```bash
# 1. Pull latest code
git checkout main
git pull origin main

# 2. Run tests
npm test

# 3. Build
npm run build

# 4. Deploy
npm run deploy:production
```

### Deployment Verification

After deployment, verify:

1. **Health check**:
   ```bash
   curl https://service.example.com/health
   ```
   Expected: `{"status": "ok"}`

2. **Version check**:
   ```bash
   curl https://service.example.com/version
   ```
   Expected: Shows new version

3. **Smoke tests**:
   ```bash
   npm run test:smoke
   ```

### Rollback Procedure

If issues are detected:

```bash
# 1. Identify last good version
git log --oneline -10

# 2. Rollback to specific version
npm run deploy:production -- --version v1.2.3

# 3. Verify rollback
curl https://service.example.com/version
```

**Rollback SLA**: Complete within 15 minutes of issue detection

---

## Operational Procedures

### Scaling

#### Scale Up

When to scale: CPU > 80% for 5+ minutes, or response time > 2s

```bash
# Scale to N instances
kubectl scale deployment service-name --replicas=N

# Verify
kubectl get pods -l app=service-name
```

#### Scale Down

When to scale: CPU < 30% for 30+ minutes during off-peak

```bash
# Minimum 2 replicas for redundancy
kubectl scale deployment service-name --replicas=2
```

### Database Operations

#### Backup

Automated backups run at 02:00 UTC daily.

Manual backup:
```bash
pg_dump -h hostname -U user database > backup_$(date +%Y%m%d).sql
```

#### Restore

```bash
# 1. Stop application
kubectl scale deployment service-name --replicas=0

# 2. Restore database
psql -h hostname -U user database < backup_YYYYMMDD.sql

# 3. Restart application
kubectl scale deployment service-name --replicas=3
```

### Cache Operations

#### Flush Cache

When to flush: After schema changes or suspected cache corruption

```bash
redis-cli -h cache.example.com FLUSHALL
```

**Warning**: Will cause temporary performance degradation

---

## Incident Response

### Alert: High Error Rate

**Trigger**: Error rate > 5% for 5 minutes

**Response Steps**:

1. **Assess severity**
   ```bash
   # Check error logs
   kubectl logs -l app=service-name --tail=100 | grep ERROR
   ```

2. **Check dependencies**
   - Database: [Dashboard link]
   - Cache: [Dashboard link]
   - External APIs: [Status page links]

3. **If database issue**:
   - Check connection pool: `SELECT count(*) FROM pg_stat_activity;`
   - Check slow queries: [Slow query dashboard]

4. **If code issue**:
   - Identify bad deployment
   - Rollback (see [Rollback Procedure](#rollback-procedure))

5. **Communicate**
   - Update status page
   - Notify stakeholders via [channel]

### Alert: High Latency

**Trigger**: p99 latency > 5s for 5 minutes

**Response Steps**:

1. **Check resource utilization**
   - CPU: [Dashboard]
   - Memory: [Dashboard]
   - Network: [Dashboard]

2. **If resource constrained**:
   - Scale up (see [Scale Up](#scale-up))

3. **If database slow**:
   - Check active queries: `SELECT * FROM pg_stat_activity WHERE state = 'active';`
   - Kill long-running queries if needed

4. **If cache miss rate high**:
   - Check cache hit ratio: [Dashboard]
   - Consider warming cache

### Alert: Service Down

**Trigger**: Health check failing for 3+ checks

**Response Steps**:

1. **Verify outage**
   ```bash
   curl -v https://service.example.com/health
   ```

2. **Check pod status**
   ```bash
   kubectl get pods -l app=service-name
   kubectl describe pod [pod-name]
   ```

3. **Common fixes**:
   - Pods in CrashLoopBackOff: Check logs, likely app error
   - Pods Pending: Check node resources
   - ImagePullBackOff: Check image exists and credentials

4. **Escalate** if not resolved in 15 minutes

---

## Maintenance Windows

### Scheduled Maintenance

**Window**: Sundays 02:00-06:00 UTC

**Procedure**:

1. Announce maintenance 48 hours in advance
2. Update status page
3. Enable maintenance mode
4. Perform maintenance
5. Verify service health
6. Disable maintenance mode
7. Update status page

### Emergency Maintenance

**Approval required from**: [Role/Person]

**Procedure**:

1. Assess urgency and impact
2. Get approval
3. Announce immediately on [channel]
4. Update status page
5. Perform maintenance
6. Post-incident review within 24 hours

---

## Contacts

### Primary Contacts

| Role | Name | Contact |
|------|------|---------|
| On-Call | Rotation | [PagerDuty link] |
| Tech Lead | [Name] | [Email/Slack] |
| Product Owner | [Name] | [Email/Slack] |

### Escalation Path

1. On-Call Engineer
2. Tech Lead
3. Engineering Manager
4. VP Engineering

### External Contacts

| Service | Support | SLA |
|---------|---------|-----|
| Cloud Provider | [Link] | 4 hours |
| Database Vendor | [Link] | 2 hours |
| CDN Provider | [Link] | 1 hour |

---

## Appendix

### Useful Commands

```bash
# View recent logs
kubectl logs -l app=service-name --tail=100 -f

# Get pod details
kubectl describe pod [pod-name]

# Execute command in pod
kubectl exec -it [pod-name] -- /bin/sh

# Port forward for local debugging
kubectl port-forward svc/service-name 8080:80
```

### Related Documentation

- [Architecture Documentation](link)
- [API Reference](link)
- [Security Procedures](link)
- [Disaster Recovery Plan](link)
