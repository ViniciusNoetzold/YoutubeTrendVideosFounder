#!/usr/bin/env bash
set -o errexit

echo "==> [Mezzold Studio] Building YoutubeTrendVideosFounder..."
pip install --upgrade pip
pip install -r requirements.txt
echo "==> Build finished successfully!"
