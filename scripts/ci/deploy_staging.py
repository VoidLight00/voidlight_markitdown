#!/usr/bin/env python3
"""Deploy to staging environment."""

import os
import sys
import subprocess
from pathlib import Path
import argparse
import json
from typing import Dict, Any

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

def deploy_docker(config: Dict[str, Any]) -> None:
    """Deploy using Docker."""
    registry = config.get("docker", {}).get("registry", "docker.io")
    image = config.get("docker", {}).get("image", "voidlight/voidlight-markitdown")
    tag = config.get("docker", {}).get("staging_tag", "staging")
    
    # Build and push image
    run_command(["docker", "build", "-t", f"{registry}/{image}:{tag}", "."])
    run_command(["docker", "push", f"{registry}/{image}:{tag}"])
    
    # Deploy to staging server
    staging_host = config.get("staging", {}).get("host")
    if staging_host:
        # SSH and deploy
        deploy_cmd = f"""
        docker pull {registry}/{image}:{tag} &&
        docker stop voidlight-markitdown-staging || true &&
        docker rm voidlight-markitdown-staging || true &&
        docker run -d --name voidlight-markitdown-staging \\
            -p 8080:8080 \\
            -e ENVIRONMENT=staging \\
            --restart unless-stopped \\
            {registry}/{image}:{tag}
        """
        run_command(["ssh", staging_host, deploy_cmd])

def deploy_kubernetes(config: Dict[str, Any]) -> None:
    """Deploy using Kubernetes."""
    namespace = config.get("kubernetes", {}).get("staging_namespace", "staging")
    
    # Apply kubernetes manifests
    manifests_dir = Path("deploy/kubernetes/staging")
    if manifests_dir.exists():
        for manifest in manifests_dir.glob("*.yaml"):
            run_command(["kubectl", "apply", "-f", str(manifest), "-n", namespace])
    
    # Wait for deployment
    deployment_name = config.get("kubernetes", {}).get("deployment_name", "voidlight-markitdown")
    run_command([
        "kubectl", "rollout", "status", 
        f"deployment/{deployment_name}", 
        "-n", namespace
    ])

def deploy_pypi_test(config: Dict[str, Any]) -> None:
    """Deploy to test PyPI."""
    # Build package
    run_command([sys.executable, "-m", "build"])
    
    # Upload to test PyPI
    run_command([
        sys.executable, "-m", "twine", "upload",
        "--repository", "testpypi",
        "dist/*"
    ])

def run_smoke_tests(config: Dict[str, Any]) -> None:
    """Run smoke tests against staging."""
    staging_url = config.get("staging", {}).get("url")
    if staging_url:
        # Run basic health check
        result = run_command([
            "curl", "-f", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            f"{staging_url}/health"
        ], check=False)
        
        if result.returncode != 0 or result.stdout.strip() != "200":
            print("ERROR: Health check failed!")
            sys.exit(1)
        
        print("Smoke tests passed!")

def main():
    parser = argparse.ArgumentParser(description="Deploy to staging environment")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("deploy/config.json"),
        help="Path to deployment configuration"
    )
    parser.add_argument(
        "--method",
        choices=["docker", "kubernetes", "pypi", "all"],
        default="docker",
        help="Deployment method"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip smoke tests"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Deploy based on method
    if args.method in ["docker", "all"]:
        print("Deploying with Docker...")
        deploy_docker(config)
    
    if args.method in ["kubernetes", "all"]:
        print("Deploying with Kubernetes...")
        deploy_kubernetes(config)
    
    if args.method in ["pypi", "all"]:
        print("Deploying to test PyPI...")
        deploy_pypi_test(config)
    
    # Run smoke tests
    if not args.skip_tests:
        print("Running smoke tests...")
        run_smoke_tests(config)
    
    print("Staging deployment completed successfully!")

if __name__ == "__main__":
    main()