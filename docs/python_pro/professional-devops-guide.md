# Professional DevOps Guide: GitHub Workflows & Checklists

## Table of Contents
1. Repository Setup & Configuration
2. Branching Strategy Implementation
3. CI/CD Pipeline Setup
4. Pull Request Workflow
5. Release Management
6. Security & Compliance
7. Monitoring & Incident Response
8. Team Checklists

---

## 1. Repository Setup & Configuration

### Initial Repository Structure

```
project-root/
├── .github/
│   ├── workflows/           # GitHub Actions CI/CD
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   └── CODEOWNERS          # Code ownership rules
├── .gitignore
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── docs/                   # Documentation
├── scripts/                # Build/deploy scripts
├── tests/                  # Test suites
└── src/                    # Source code
```

### Branch Protection Rules (GitHub Settings)

**For `main` branch:**
- ☑️ Require pull request before merging
- ☑️ Require 2 approvals (adjustable by team size)
- ☑️ Dismiss stale pull request approvals when new commits are pushed
- ☑️ Require review from Code Owners
- ☑️ Require status checks to pass before merging
  - ☑️ All CI tests must pass
  - ☑️ Security scans must pass
  - ☑️ Code coverage threshold met
- ☑️ Require branches to be up to date before merging
- ☑️ Require conversation resolution before merging
- ☑️ Require signed commits
- ☑️ Include administrators (no one bypasses rules)
- ☑️ Restrict who can push to matching branches
- ☑️ Allow force pushes: NEVER
- ☑️ Allow deletions: NEVER

**For `develop` branch (if using Git Flow):**
- ☑️ Require pull request before merging
- ☑️ Require 1 approval
- ☑️ Require status checks to pass
- ☑️ Less strict than `main` for faster iteration

### CODEOWNERS File Example

```
# Global owners
* @devops-team

# Backend code
/src/backend/** @backend-team @senior-backend-engineer

# Frontend code
/src/frontend/** @frontend-team

# Infrastructure as Code
/infrastructure/** @devops-team @platform-team
/terraform/** @devops-team
/.github/workflows/** @devops-team

# Database migrations
/migrations/** @database-team @backend-team

# Security-sensitive files
/src/auth/** @security-team @backend-team
/src/payment/** @security-team @backend-team

# Documentation
/docs/** @technical-writers

# CI/CD configuration
.github/workflows/** @devops-team
Dockerfile @devops-team
docker-compose.yml @devops-team
```

---

## 2. Branching Strategy Implementation

### Recommended: GitHub Flow (Modern SaaS/Web Apps)

**Branch Structure:**
```
main (production)
├── feature/PROJ-123-user-authentication
├── feature/PROJ-124-payment-integration
├── bugfix/PROJ-125-fix-memory-leak
└── hotfix/PROJ-126-security-patch
```

**Naming Convention:**
```
feature/TICKET-ID-short-description
bugfix/TICKET-ID-short-description
hotfix/TICKET-ID-short-description
release/v1.2.0
docs/update-readme
chore/upgrade-dependencies
```

### Alternative: Git Flow (Enterprise/Scheduled Releases)

**Branch Structure:**
```
main (production - v1.0.0)
│
develop (next release)
├── feature/PROJ-123-new-dashboard
├── feature/PROJ-124-api-v2
├── bugfix/PROJ-125-chart-rendering
│
release/v1.1.0 (release preparation)
│
hotfix/v1.0.1-security-fix (emergency patch)
```

### Branch Lifecycle

1. **Feature Branch**: 2-5 days lifespan
2. **Release Branch**: 1-3 days for testing and bug fixes
3. **Hotfix Branch**: Hours (urgent fixes only)
4. **Delete after merge**: Always clean up merged branches

---

## 3. CI/CD Pipeline Setup

### GitHub Actions Workflow Example

**`.github/workflows/ci.yml`**

```yaml
name: CI Pipeline

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint
      
      - name: Run unit tests
        run: npm test -- --coverage
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
      
      - name: Run integration tests
        run: npm run test:integration
      
      - name: Build application
        run: npm run build

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run security audit
        run: npm audit --audit-level=moderate
      
      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'

  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**`.github/workflows/cd.yml`** (Deployment)

```yaml
name: CD Pipeline

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t app:${{ github.sha }} .
      
      - name: Push to container registry
        run: |
          docker tag app:${{ github.sha }} registry.example.com/app:staging
          docker push registry.example.com/app:staging
      
      - name: Deploy to staging
        run: kubectl apply -f k8s/staging/
      
      - name: Run smoke tests
        run: npm run test:smoke -- --env=staging
      
      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Staging deployment completed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Manual approval required
        uses: trstringer/manual-approval@v1
        with:
          approvers: platform-team,senior-engineers
      
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: kubectl apply -f k8s/production/
      
      - name: Run production smoke tests
        run: npm run test:smoke -- --env=production
      
      - name: Monitor deployment
        run: ./scripts/monitor-deployment.sh
      
      - name: Rollback on failure
        if: failure()
        run: kubectl rollout undo deployment/app
```

### Pipeline Stages Explanation

**1. Build Stage**
- Compile code
- Install dependencies
- Generate artifacts
- Cache dependencies for speed

**2. Test Stage**
- **Unit Tests**: Test individual functions/components
- **Integration Tests**: Test how components work together
- **End-to-End Tests**: Test complete user workflows
- **Code Coverage**: Ensure 80%+ of code is tested

**3. Code Quality Stage**
- **Linting**: Enforce code style (ESLint, Prettier)
- **Static Analysis**: Find potential bugs (SonarQube)
- **Complexity Analysis**: Identify overly complex code

**4. Security Stage**
- **Dependency Scanning**: Check for vulnerable packages
- **SAST**: Static Application Security Testing
- **Secret Detection**: Ensure no API keys/passwords in code
- **License Compliance**: Verify open source licenses

**5. Deploy Stage**
- Build container images
- Push to registry (Docker Hub, ECR, GCR)
- Deploy to staging automatically
- Deploy to production with approval

**6. Post-Deployment Stage**
- Smoke tests (basic functionality checks)
- Performance monitoring
- Error rate monitoring
- Automatic rollback if issues detected

---

## 4. Pull Request Workflow

### PR Template (`.github/PULL_REQUEST_TEMPLATE.md`)

```markdown
## Description
<!-- Describe what this PR does and why -->

## Type of Change
- [ ] Feature (new functionality)
- [ ] Bugfix (fixes an issue)
- [ ] Hotfix (urgent production fix)
- [ ] Refactor (code improvement, no behavior change)
- [ ] Documentation
- [ ] Performance improvement
- [ ] Security fix

## Related Tickets
<!-- Link to Jira, Linear, or GitHub issues -->
- Closes #123
- Related to PROJ-456

## Changes Made
<!-- List the key changes -->
- Added user authentication service
- Implemented JWT token validation
- Updated API documentation

## Testing Done
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Tested on staging environment

## Screenshots/Videos
<!-- For UI changes, include before/after screenshots -->

## Database Changes
- [ ] No database changes
- [ ] Migrations included and tested
- [ ] Rollback plan documented

## Performance Impact
- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance impact assessed and acceptable

## Deployment Notes
<!-- Any special instructions for deployment -->
- Requires environment variable: `NEW_FEATURE_FLAG=true`
- Run migration before deployment: `npm run migrate`

## Checklist
- [ ] Code follows team style guidelines
- [ ] Self-review completed
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No console.log or debugging code
- [ ] No sensitive data (API keys, passwords)
- [ ] Branch is up to date with main
```

### PR Review Process

**For Reviewers:**

1. **Understand the Context** (2 minutes)
   - Read PR description and linked tickets
   - Understand what problem is being solved

2. **Review the Code** (10-30 minutes)
   - Check for logic errors
   - Verify edge cases are handled
   - Ensure proper error handling
   - Look for security vulnerabilities
   - Check performance implications
   - Verify tests are adequate

3. **Check Non-Code Changes**
   - Documentation updated
   - Database migrations included
   - Environment variables documented

4. **Provide Feedback**
   - **Blocking comments**: Must be fixed before merge
   - **Non-blocking comments**: Suggestions for improvement
   - **Questions**: Ask for clarification
   - **Praise**: Acknowledge good work

5. **Final Approval**
   - All CI checks passing
   - All conversations resolved
   - Changes meet requirements

**Review Turnaround Time:**
- **Critical/Hotfix**: Within 1 hour
- **Normal PR**: Within 24 hours
- **Large PR**: Within 48 hours

---

## 5. Release Management

### Semantic Versioning

```
v1.2.3
│ │ │
│ │ └─ PATCH: Bug fixes, no new features
│ └─── MINOR: New features, backward compatible
└───── MAJOR: Breaking changes
```

**Examples:**
- `v1.0.0` → `v1.0.1`: Bug fix
- `v1.0.1` → `v1.1.0`: New feature added
- `v1.1.0` → `v2.0.0`: Breaking API changes

### Release Process

**1. Create Release Branch**
```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0
```

**2. Update Version Numbers**
```bash
# Update package.json, version files
npm version 1.2.0 --no-git-tag-version
git add .
git commit -m "chore: bump version to 1.2.0"
```

**3. Create Release Notes**
Update `CHANGELOG.md`:
```markdown
## [1.2.0] - 2024-01-15

### Added
- User authentication with OAuth2
- Export data to CSV functionality
- Dark mode support

### Fixed
- Memory leak in data processing
- Mobile responsive layout issues

### Changed
- Improved search performance by 50%
- Updated API rate limits

### Security
- Fixed XSS vulnerability in user input
```

**4. Test Release Candidate**
```bash
# Deploy to staging
git push origin release/v1.2.0
# Run full test suite
# Perform manual QA
```

**5. Merge to Main and Tag**
```bash
# Merge to main
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop

# Delete release branch
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

**6. Deploy to Production**
```bash
# Automated deployment triggered by tag push
# Monitor metrics and error rates
# Be ready to rollback if needed
```

### Hotfix Process (Emergency Production Fix)

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/v1.2.1-security-fix

# 2. Make the fix
# ... fix the critical bug ...
git add .
git commit -m "fix: patch security vulnerability CVE-2024-1234"

# 3. Test quickly but thoroughly
npm test
npm run test:integration

# 4. Update version
npm version patch

# 5. Merge to main (fast-track review)
git checkout main
git merge --no-ff hotfix/v1.2.1-security-fix
git tag -a v1.2.1 -m "Hotfix: security patch"
git push origin main --tags

# 6. Merge to develop
git checkout develop
git merge --no-ff hotfix/v1.2.1-security-fix
git push origin develop

# 7. Deploy immediately
# Monitor closely
```

---

## 6. Security & Compliance

### Security Checklist

**Code Security:**
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] Input validation implemented
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection enabled
- [ ] Authentication and authorization implemented
- [ ] Sensitive data encrypted at rest and in transit
- [ ] Rate limiting on APIs
- [ ] Security headers configured

**Dependency Security:**
- [ ] Dependencies regularly updated
- [ ] No known vulnerabilities (run `npm audit`)
- [ ] License compliance checked
- [ ] Only trusted packages used

**Access Control:**
- [ ] Least privilege principle applied
- [ ] Service accounts use limited permissions
- [ ] Secrets stored in vault (AWS Secrets Manager, HashiCorp Vault)
- [ ] Environment variables used for configuration
- [ ] No production access without approval

### GitHub Security Features to Enable

**1. Dependabot Alerts**
- Settings → Security → Dependabot alerts: Enabled
- Automatic PR creation for vulnerable dependencies

**2. Secret Scanning**
- Settings → Security → Secret scanning: Enabled
- Prevents accidental commit of secrets

**3. Code Scanning**
- Settings → Security → Code scanning: Enabled
- Uses CodeQL for static analysis

**4. Branch Protection**
- Require signed commits (GPG keys)
- Restrict who can push to protected branches

**5. Security Policy**
- Create `SECURITY.md` with vulnerability reporting process

---

## 7. Monitoring & Incident Response

### Monitoring Setup

**Application Metrics:**
- Response time (p50, p95, p99)
- Error rate
- Request throughput
- Active users

**Infrastructure Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

**Business Metrics:**
- Successful transactions
- Failed payments
- User signups
- Feature usage

### Incident Response Process

**1. Detection** (0-5 minutes)
- Automated alerts trigger
- On-call engineer notified
- Initial assessment

**2. Response** (5-15 minutes)
```bash
# Check recent deployments
git log --oneline -10 main

# Check CI/CD pipeline
# Review monitoring dashboards
# Check error logs
```

**3. Communication** (Immediate)
- Update status page
- Notify stakeholders
- Create incident channel (Slack)

**4. Mitigation** (15-60 minutes)
```bash
# Option 1: Rollback deployment
kubectl rollout undo deployment/app

# Option 2: Hotfix
git checkout -b hotfix/incident-fix
# ... make fix ...
git push origin hotfix/incident-fix
# Fast-track merge and deploy

# Option 3: Feature flag disable
# Turn off problematic feature
```

**5. Resolution** (Variable)
- Verify metrics return to normal
- Conduct thorough testing
- Update status page

**6. Post-Mortem** (Within 48 hours)
- Document timeline
- Identify root cause
- List action items
- Share learnings with team

---

## 8. Team Checklists

### Daily Developer Checklist

**Morning:**
- [ ] Pull latest changes from `main`
- [ ] Check assigned PRs for review
- [ ] Check CI/CD pipeline status
- [ ] Review overnight production incidents

**Before Starting Work:**
- [ ] Create/update ticket in issue tracker
- [ ] Create feature branch from latest `main`
- [ ] Verify branch naming follows convention

**During Development:**
- [ ] Commit frequently with meaningful messages
- [ ] Run tests locally before pushing
- [ ] Keep branch updated with `main`
- [ ] No `console.log` or debug code
- [ ] No commented-out code

**Before Creating PR:**
- [ ] All tests pass locally
- [ ] Code self-reviewed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No merge conflicts with `main`

**After Creating PR:**
- [ ] Request reviews from appropriate team members
- [ ] Link to relevant tickets
- [ ] Monitor CI/CD checks
- [ ] Respond to feedback within 24 hours

### Code Reviewer Checklist

**Understanding:**
- [ ] Read PR description and context
- [ ] Understand the problem being solved
- [ ] Review linked tickets/documentation

**Code Review:**
- [ ] Logic is correct
- [ ] Edge cases handled
- [ ] Error handling implemented
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Code is readable and maintainable
- [ ] Tests are adequate
- [ ] No code duplication

**Quality Checks:**
- [ ] Follows team coding standards
- [ ] Documentation is clear
- [ ] No unnecessary complexity
- [ ] Proper abstractions used

**Final:**
- [ ] All CI checks passing
- [ ] All conversations resolved
- [ ] Approve or request changes with clear feedback
- [ ] Respond to PRs within agreed SLA

### DevOps/Platform Team Checklist

**Weekly:**
- [ ] Review and update dependencies
- [ ] Check security scan results
- [ ] Review CI/CD pipeline performance
- [ ] Update documentation
- [ ] Review infrastructure costs

**Monthly:**
- [ ] Audit access permissions
- [ ] Review and rotate secrets/keys
- [ ] Update runbooks
- [ ] Disaster recovery drill
- [ ] Review and optimize CI/CD pipelines

**Quarterly:**
- [ ] Review branching strategy effectiveness
- [ ] Update security policies
- [ ] Review and improve monitoring
- [ ] Team training on new tools/practices

### Release Manager Checklist

**Pre-Release (1 week before):**
- [ ] Create release branch
- [ ] Freeze feature development
- [ ] Deploy to staging
- [ ] Coordinate QA testing
- [ ] Prepare release notes
- [ ] Review database migrations
- [ ] Prepare rollback plan

**Release Day:**
- [ ] Final smoke tests on staging
- [ ] Notify stakeholders of deployment window
- [ ] Merge release branch to `main`
- [ ] Tag release version
- [ ] Deploy to production
- [ ] Monitor metrics closely (first 2 hours)
- [ ] Run production smoke tests
- [ ] Update status page
- [ ] Merge changes back to `develop`

**Post-Release (24 hours after):**
- [ ] Verify all features working
- [ ] Review error rates
- [ ] Check performance metrics
- [ ] Gather user feedback
- [ ] Document issues for next release

### Emergency Hotfix Checklist

**Immediate (0-15 minutes):**
- [ ] Confirm severity (production down?)
- [ ] Create incident channel
- [ ] Notify on-call team
- [ ] Update status page
- [ ] Create hotfix branch from `main`

**Mitigation (15-60 minutes):**
- [ ] Implement fix
- [ ] Test quickly but thoroughly
- [ ] Fast-track code review (1 approver)
- [ ] Deploy to staging first if possible
- [ ] Deploy to production
- [ ] Verify fix resolves issue

**Follow-up (Within 24 hours):**
- [ ] Merge hotfix to `develop`
- [ ] Update documentation
- [ ] Schedule post-mortem
- [ ] Create tickets for permanent fixes
- [ ] Update monitoring/alerts

---

## Summary: Professional DevOps Principles

### The Four Key Metrics (DORA)

1. **Deployment Frequency**: How often you deploy to production
   - Elite: Multiple deploys per day
   - High: Once per day to once per week

2. **Lead Time for Changes**: Time from commit to production
   - Elite: Less than one day
   - High: One day to one week

3. **Time to Restore Service**: How quickly you recover from incidents
   - Elite: Less than one hour
   - High: Less than one day

4. **Change Failure Rate**: % of deployments causing failures
   - Elite: 0-15%
   - High: 16-30%

### Core Principles

1. **Automate Everything**: If humans do it, robots should do it
2. **Shift Left**: Catch issues early in development
3. **Continuous Integration**: Integrate code frequently
4. **Continuous Deployment**: Deploy changes automatically
5. **Monitor Relentlessly**: Know when things break immediately
6. **Fail Fast, Recover Faster**: Quick rollbacks over perfect code
7. **Blameless Post-Mortems**: Learn from failures, don't punish
8. **Infrastructure as Code**: All infrastructure in version control
9. **Security by Default**: Security integrated, not added later
10. **Documentation as Code**: Docs live with code

---

## Tools Ecosystem

**Version Control:**
- GitHub (most common)
- GitLab
- Bitbucket

**CI/CD:**
- GitHub Actions
- Jenkins
- CircleCI
- GitLab CI
- Travis CI

**Container & Orchestration:**
- Docker
- Kubernetes
- Docker Compose
- Helm

**Monitoring:**
- Datadog
- New Relic
- Prometheus + Grafana
- Sentry (error tracking)

**Security:**
- Snyk
- SonarQube
- Trivy
- GitHub Advanced Security

**Communication:**
- Slack
- PagerDuty
- Statuspage

---

## Getting Started

For a new team implementing these practices:

**Week 1:**
- Set up branch protection rules
- Create PR template
- Configure CODEOWNERS

**Week 2:**
- Implement basic CI pipeline
- Add linting and unit tests
- Set up code coverage tracking

**Week 3:**
- Add security scanning
- Set up staging deployment
- Implement automated tests

**Week 4:**
- Add production deployment with approvals
- Set up monitoring and alerts
- Document the entire process

**Ongoing:**
- Iterate and improve based on metrics
- Regular retrospectives
- Continuous learning and adaptation