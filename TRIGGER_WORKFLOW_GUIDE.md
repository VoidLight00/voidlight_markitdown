# Quick Guide: Triggering CI/CD Workflow

## 🚀 Fastest Method: Git Push

```bash
# 1. Stage the workflow changes
git add .github/workflows/integration-tests.yml

# 2. Commit with CI message
git commit -m "ci: update GitHub Actions workflow to latest versions"

# 3. Push to trigger (works on main/develop branches)
git push origin main
```

## 🌐 Web Interface Method

1. Go to: https://github.com/VoidLight00/voidlight_markitdown/actions
2. Click "MCP Integration Tests" in left sidebar
3. Click "Run workflow" button
4. Select:
   - Branch: `main`
   - Test suites: `enhanced comprehensive` (or leave default)
5. Click green "Run workflow" button

## 🖥️ GitHub CLI Method

```bash
# If not installed:
brew install gh
gh auth login

# Trigger with defaults:
gh workflow run integration-tests.yml

# Trigger with custom suites:
gh workflow run integration-tests.yml -f test_suites='enhanced comprehensive'

# Check status:
gh workflow list
gh run list --workflow=integration-tests.yml
```

## 📊 Monitor Progress

- **Live Logs**: https://github.com/VoidLight00/voidlight_markitdown/actions
- **Expected Duration**: 15-20 minutes total
- **Matrix Jobs**: Tests run on Python 3.9, 3.10, and 3.11 in parallel

## 🎯 What Happens Next

1. **Integration Tests** run for each Python version
2. **Artifacts** are collected (logs, reports)
3. **Performance Tests** run after integration tests
4. **Results** appear in Actions tab with ✅ or ❌

## 🔧 Troubleshooting

If the workflow doesn't trigger:
- Ensure you're on `main` or `develop` branch
- Check that you have push permissions
- Verify the workflow file syntax is valid

## 📦 Artifacts

After completion, download test results from:
- Actions → Select workflow run → Artifacts section

Includes:
- Test logs
- Performance metrics
- Coverage reports
- Error details (if any)

---

**Ready to go!** Use any method above to start your CI/CD pipeline.