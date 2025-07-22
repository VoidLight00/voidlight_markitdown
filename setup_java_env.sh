#!/bin/bash
# Setup Java environment for KoNLPy

# Add OpenJDK to PATH
export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"

# Set JAVA_HOME
export JAVA_HOME="/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home"

# Suppress Java warnings for native access (optional)
export _JAVA_OPTIONS="-XX:+IgnoreUnrecognizedVMOptions --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED"

echo "Java environment configured for KoNLPy:"
echo "  JAVA_HOME: $JAVA_HOME"
echo "  Java version: $(java -version 2>&1 | head -n 1)"
echo ""
echo "To use this configuration in your shell:"
echo "  source setup_java_env.sh"