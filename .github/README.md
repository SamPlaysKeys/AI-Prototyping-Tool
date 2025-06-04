# GitHub Actions CI/CD Setup

This directory contains comprehensive GitHub Actions workflows for continuous integration and deployment of the AI Prototyping Tool.

## 📋 Workflows Overview

### 🔄 Main CI/CD Pipeline (`ci-cd.yml`)
**Triggers:** Push to main/develop, Pull Requests, Releases

**Jobs:**
1. **Tests & Code Quality** - Multi-version Python testing, linting, formatting
2. **Documentation Validation** - Mermaid diagram validation, link checking
3. **Docker Build & Test** - Container building and testing
4. **Security Scanning** - Vulnerability scanning with Trivy
5. **Build & Publish** - Package building and PyPI publishing
6. **Docker Registry Push** - Container registry publishing
7. **Deploy** - Production deployment (configurable)

### 🔍 Code Quality (`code-quality.yml`)
**Triggers:** Push/PR to main/develop

**Features:**
- Black code formatting
- isort import sorting
- flake8 linting
- mypy type checking
- bandit security scanning
- Code complexity analysis with radon
- Documentation quality checks

### 📦 Dependency Updates (`dependency-update.yml`)
**Triggers:** Weekly schedule (Mondays 9 AM UTC), Manual

**Features:**
- Automated dependency updates
- Security vulnerability scanning
- Automated Pull Request creation

### 🚀 Release Management (`release.yml`)
**Triggers:** Version tags (v*.*.*), Manual

**Features:**
- Automated changelog generation
- GitHub release creation
- Asset uploading
- Pre-release detection

## 🛠️ Setup Instructions

### 1. Repository Secrets

Configure these secrets in your GitHub repository settings:

#### Required for PyPI Publishing
```bash
# For TestPyPI (optional)
TEST_PYPI_API_TOKEN=pypi-...

# For PyPI (required for releases)
PYPI_API_TOKEN=pypi-...
```

#### Optional for Enhanced Features
```bash
# For Codecov integration
CODECOV_TOKEN=your-codecov-token

# For Slack/Discord notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 2. Environment Configuration

#### Production Environment
1. Go to Settings → Environments
2. Create "production" environment
3. Add environment protection rules:
   - Required reviewers
   - Deployment branches (main only)
   - Environment secrets

#### Branch Protection
1. Go to Settings → Branches
2. Add rule for `main` branch:
   - Require status checks
   - Require branches to be up to date
   - Require review from code owners
   - Dismiss stale reviews

### 3. PyPI Setup

#### Get PyPI API Tokens
```bash
# 1. Create PyPI account at https://pypi.org
# 2. Go to Account Settings → API tokens
# 3. Create tokens for:
#    - TestPyPI: https://test.pypi.org
#    - PyPI: https://pypi.org
```

#### Test PyPI Publishing
```bash
# Manual test (optional)
pip install build twine
python -m build
twine upload --repository testpypi dist/*
```

### 4. Docker Registry Setup

The workflows automatically use GitHub Container Registry (ghcr.io). No additional setup required.

**Images will be published to:**
- `ghcr.io/samplayskeys/ai-prototyping-tool:latest`
- `ghcr.io/samplayskeys/ai-prototyping-tool-web:latest`

## 🎯 Workflow Triggers

### Automatic Triggers

| Event | Workflows Triggered |
|-------|-------------------|
| Push to `main` | CI/CD, Code Quality |
| Push to `develop` | CI/CD, Code Quality |
| Pull Request | CI/CD, Code Quality |
| Release Published | CI/CD, Release |
| Weekly Schedule | Dependency Updates |
| Tag `v*.*.*` | Release |

### Manual Triggers

All workflows can be triggered manually:
1. Go to Actions tab
2. Select workflow
3. Click "Run workflow"
4. Choose branch and parameters

## 📊 Status Badges

Add these badges to your README:

```markdown
[![CI/CD](https://github.com/SamPlaysKeys/AI-Prototyping-Tool/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/SamPlaysKeys/AI-Prototyping-Tool/actions/workflows/ci-cd.yml)
[![Code Quality](https://github.com/SamPlaysKeys/AI-Prototyping-Tool/actions/workflows/code-quality.yml/badge.svg)](https://github.com/SamPlaysKeys/AI-Prototyping-Tool/actions/workflows/code-quality.yml)
[![codecov](https://codecov.io/gh/SamPlaysKeys/AI-Prototyping-Tool/branch/main/graph/badge.svg)](https://codecov.io/gh/SamPlaysKeys/AI-Prototyping-Tool)
```

## 🔧 Customization

### Adding New Environments

1. **Staging Environment:**
```yaml
# Add to ci-cd.yml
deploy-staging:
  name: Deploy to Staging
  runs-on: ubuntu-latest
  needs: [docker-publish]
  if: github.ref == 'refs/heads/develop'
  environment: staging
```

2. **Custom Deployment:**
```yaml
# Replace deploy job in ci-cd.yml
- name: Deploy to Kubernetes
  run: |
    kubectl config use-context production
    helm upgrade --install ai-prototyping-tool ./helm/ai-prototyping-tool \
      --set image.tag=${{ github.sha }}
```

### Adding Notifications

```yaml
# Add to any workflow
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Custom Test Matrix

```yaml
# Modify strategy in ci-cd.yml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest, macos-latest]
```

## 🚨 Troubleshooting

### Common Issues

1. **PyPI Upload Fails**
   - Check API token is correct
   - Verify package version isn't already published
   - Ensure `setup.py` or `pyproject.toml` is properly configured

2. **Docker Build Fails**
   - Check Dockerfile syntax
   - Verify all required files are included
   - Check for missing dependencies

3. **Tests Fail**
   - Check if LM Studio mock is properly configured
   - Verify test dependencies are installed
   - Check for environment-specific issues

### Debug Mode

```yaml
# Add to any workflow step
- name: Debug Information
  run: |
    echo "GitHub Context:"
    echo "Event: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
    echo "Actor: ${{ github.actor }}"
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

**The CI/CD pipeline is designed to be comprehensive yet flexible. Modify workflows as needed for your specific requirements.**

