#!/usr/bin/env python3
"""Deploy to production environment."""

import os
import sys
import subprocess
from pathlib import Path
import argparse
import json
from typing import Dict, Any
import time

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load deployment configuration."""
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)

def confirm_deployment() -> bool:
    """Confirm production deployment."""
    print("\n" + "="*50)
    print("WARNING: You are about to deploy to PRODUCTION!")
    print("="*50 + "\n")
    
    response = input("Are you sure you want to continue? (yes/no): ")
    return response.lower() == "yes"

def check_staging_status(config: Dict[str, Any]) -> bool:
    """Verify staging deployment is healthy."""
    staging_url = config.get("staging", {}).get("url")
    if not staging_url:
        print("WARNING: No staging URL configured, skipping staging check")
        return True
    
    result = run_command([
        "curl", "-f", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        f"{staging_url}/health"
    ], check=False)
    
    if result.returncode != 0 or result.stdout.strip() != "200":
        print("ERROR: Staging health check failed!")
        return False
    
    print("Staging environment is healthy")
    return True

def deploy_docker(config: Dict[str, Any]) -> None:
    """Deploy using Docker with blue-green deployment."""
    registry = config.get("docker", {}).get("registry", "docker.io")
    image = config.get("docker", {}).get("image", "voidlight/voidlight-markitdown")
    version = subprocess.check_output(
        ["python", "-c", "from src.voidlight_markitdown.__about__ import __version__; print(__version__)"],
        text=True
    ).strip()
    
    # Tag and push production image
    run_command(["docker", "tag", f"{registry}/{image}:staging", f"{registry}/{image}:{version}"])
    run_command(["docker", "tag", f"{registry}/{image}:staging", f"{registry}/{image}:latest"])
    run_command(["docker", "push", f"{registry}/{image}:{version}"])
    run_command(["docker", "push", f"{registry}/{image}:latest"])
    
    # Deploy to production servers
    prod_hosts = config.get("production", {}).get("hosts", [])
    for host in prod_hosts:
        print(f"Deploying to {host}...")
        
        # Blue-green deployment
        deploy_cmd = f"""
        # Pull new image
        docker pull {registry}/{image}:{version} &&
        
        # Start new container (green)
        docker run -d --name voidlight-markitdown-green \\
            -p 8081:8080 \\
            -e ENVIRONMENT=production \\
            --restart unless-stopped \\
            {registry}/{image}:{version} &&
        
        # Wait for health check
        sleep 10 &&
        curl -f http://localhost:8081/health &&
        
        # Switch traffic
        docker stop voidlight-markitdown-blue || true &&
        docker rm voidlight-markitdown-blue || true &&
        docker rename voidlight-markitdown-green voidlight-markitdown-blue &&
        
        # Update nginx/load balancer
        sudo nginx -s reload
        """
        run_command(["ssh", host, deploy_cmd])

def deploy_kubernetes(config: Dict[str, Any]) -> None:
    """Deploy using Kubernetes with rolling update."""
    namespace = config.get("kubernetes", {}).get("production_namespace", "production")
    deployment_name = config.get("kubernetes", {}).get("deployment_name", "voidlight-markitdown")
    
    # Apply production manifests
    manifests_dir = Path("deploy/kubernetes/production")
    if manifests_dir.exists():
        for manifest in manifests_dir.glob("*.yaml"):
            run_command(["kubectl", "apply", "-f", str(manifest), "-n", namespace])
    
    # Perform rolling update
    version = subprocess.check_output(
        ["python", "-c", "from src.voidlight_markitdown.__about__ import __version__; print(__version__)"],
        text=True
    ).strip()
    
    run_command([
        "kubectl", "set", "image",
        f"deployment/{deployment_name}",
        f"{deployment_name}=voidlight/voidlight-markitdown:{version}",
        "-n", namespace
    ])
    
    # Wait for rollout
    run_command([
        "kubectl", "rollout", "status",
        f"deployment/{deployment_name}",
        "-n", namespace
    ])

def deploy_pypi(config: Dict[str, Any]) -> None:
    """Deploy to PyPI."""
    # Verify package
    run_command([sys.executable, "-m", "twine", "check", "dist/*"])
    
    # Upload to PyPI
    run_command([
        sys.executable, "-m", "twine", "upload",
        "dist/*"
    ])

def create_github_release(config: Dict[str, Any]) -> None:
    """Create GitHub release."""
    version = subprocess.check_output(
        ["python", "-c", "from src.voidlight_markitdown.__about__ import __version__; print(__version__)"],
        text=True
    ).strip()
    
    # Generate release notes
    release_notes = subprocess.check_output(
        ["python", "scripts/maintenance/generate_release_notes.py", version],
        text=True
    )
    
    # Create release
    run_command([
        "gh", "release", "create",
        f"v{version}",
        "--title", f"Release v{version}",
        "--notes", release_notes,
        "dist/*"
    ])

def run_production_tests(config: Dict[str, Any]) -> None:
    """Run production smoke tests."""
    prod_url = config.get("production", {}).get("url")
    if not prod_url:
        print("WARNING: No production URL configured, skipping tests")
        return
    
    # Health check
    result = run_command([
        "curl", "-f", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        f"{prod_url}/health"
    ], check=False)
    
    if result.returncode != 0 or result.stdout.strip() != "200":
        print("ERROR: Production health check failed!")
        sys.exit(1)
    
    # Run smoke test suite
    test_result = run_command([
        sys.executable, "-m", "pytest",
        "tests/smoke/",
        "-v",
        "--production-url", prod_url
    ], check=False)
    
    if test_result.returncode != 0:
        print("ERROR: Production smoke tests failed!")
        sys.exit(1)
    
    print("Production tests passed!")

def rollback(config: Dict[str, Any]) -> None:
    """Rollback production deployment."""
    print("Initiating rollback...")
    
    # Docker rollback
    prod_hosts = config.get("production", {}).get("hosts", [])
    for host in prod_hosts:
        rollback_cmd = """
        docker tag voidlight-markitdown-previous voidlight-markitdown-blue &&
        docker stop voidlight-markitdown-blue &&
        docker rm voidlight-markitdown-blue &&
        docker run -d --name voidlight-markitdown-blue \\
            -p 8080:8080 \\
            -e ENVIRONMENT=production \\
            --restart unless-stopped \\
            voidlight-markitdown-previous
        """
        run_command(["ssh", host, rollback_cmd])
    
    print("Rollback completed!")

def main():
    parser = argparse.ArgumentParser(description="Deploy to production environment")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("deploy/config.json"),
        help="Path to deployment configuration"
    )
    parser.add_argument(
        "--method",
        choices=["docker", "kubernetes", "pypi", "all"],
        default="all",
        help="Deployment method"
    )
    parser.add_argument(
        "--skip-staging-check",
        action="store_true",
        help="Skip staging health check"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip production tests"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback to previous version"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Handle rollback
    if args.rollback:
        rollback(config)
        return
    
    # Confirm deployment
    if not args.force and not confirm_deployment():
        print("Deployment cancelled")
        sys.exit(0)
    
    # Check staging
    if not args.skip_staging_check and not check_staging_status(config):
        print("ERROR: Staging is not healthy, aborting deployment")
        sys.exit(1)
    
    # Deploy based on method
    try:
        if args.method in ["docker", "all"]:
            print("Deploying with Docker...")
            deploy_docker(config)
        
        if args.method in ["kubernetes", "all"]:
            print("Deploying with Kubernetes...")
            deploy_kubernetes(config)
        
        if args.method in ["pypi", "all"]:
            print("Deploying to PyPI...")
            deploy_pypi(config)
        
        # Create GitHub release
        if args.method == "all":
            print("Creating GitHub release...")
            create_github_release(config)
        
        # Run production tests
        if not args.skip_tests:
            print("Running production tests...")
            time.sleep(30)  # Wait for deployment to stabilize
            run_production_tests(config)
        
        print("\nProduction deployment completed successfully!")
        
    except Exception as e:
        print(f"\nERROR: Deployment failed: {e}")
        if input("Rollback? (yes/no): ").lower() == "yes":
            rollback(config)
        sys.exit(1)

if __name__ == "__main__":
    main()