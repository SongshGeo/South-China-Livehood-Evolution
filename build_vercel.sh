#!/bin/bash
# Vercel build script for Python/MkDocs project

set -e

echo "🐍 Python version:"
python3 --version

echo "📦 Installing dependencies..."
# Use --break-system-packages for Vercel environment
python3 -m pip install --upgrade pip --break-system-packages || python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-docs.txt --break-system-packages || python3 -m pip install -r requirements-docs.txt

echo "🔨 Building documentation..."
python3 -m mkdocs build --clean

echo "✅ Build completed!"
echo "📁 Output files:"
ls -lh site/ | head -10 || true

