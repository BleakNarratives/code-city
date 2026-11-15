#!/bin/bash
# Download Three.js locally for offline use

THREE_DIR="/data/data/com.termux/files/home/_bmad-output/threejs"

mkdir -p "$THREE_DIR"

echo "Downloading Three.js r128..."
curl -s https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js -o "$THREE_DIR/three.min.js"

if [ -f "$THREE_DIR/three.min.js" ]; then
    echo "✓ Three.js downloaded"
else
    echo "✗ Failed to download Three.js"
    exit 1
fi

echo "Downloading OrbitControls..."
curl -s https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js -o "$THREE_DIR/OrbitControls.js"

if [ -f "$THREE_DIR/OrbitControls.js" ]; then
    echo "✓ OrbitControls downloaded"
else
    echo "✗ Failed to download OrbitControls"
    exit 1
fi

echo "✓ All Three.js files downloaded to $THREE_DIR"
echo "You can now use --offline flag with boardroom_city_integrated.py"
