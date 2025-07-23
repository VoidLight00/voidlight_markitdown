#!/bin/bash

# Docker Health Check Script for voidlight_markitdown

echo "=== Docker Health Check ==="
echo "Date: $(date)"
echo ""

# Set Docker path
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

# Check Docker daemon
echo "1. Docker Daemon Status:"
if docker info > /dev/null 2>&1; then
    echo "   ✓ Docker daemon is running"
    docker version --format "   Version: {{.Server.Version}}"
else
    echo "   ✗ Docker daemon is not running"
    exit 1
fi

echo ""
echo "2. Image Status:"
if docker images | grep -q "voidlight-markitdown-test"; then
    echo "   ✓ Docker image exists"
    docker images | grep "voidlight-markitdown-test" | awk '{print "   Size: " $7 " " $8}'
else
    echo "   ✗ Docker image not found"
fi

echo ""
echo "3. Quick Container Test:"
if docker run --rm voidlight-markitdown-test:latest python3 -c "print('Container running OK')"; then
    echo "   ✓ Container can execute Python"
else
    echo "   ✗ Container execution failed"
fi

echo ""
echo "4. Korean Locale Test:"
docker run --rm voidlight-markitdown-test:latest python3 -c "
import locale
print('   Default locale:', locale.getlocale())
korean = '한글 테스트'
print(f'   Korean text: {korean}')
print(f'   UTF-8 encoding: {korean.encode(\"utf-8\")}')"

echo ""
echo "5. Package Availability:"
docker run --rm voidlight-markitdown-test:latest python3 -c "
import pkg_resources
packages = ['voidlight-markitdown', 'voidlight-markitdown-mcp', 'mcp', 'pytest']
for pkg in packages:
    try:
        version = pkg_resources.get_distribution(pkg).version
        print(f'   ✓ {pkg} v{version}')
    except:
        print(f'   ✗ {pkg} not found')"

echo ""
echo "=== Health Check Complete ==="