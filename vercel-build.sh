#!/bin/bash
# Vercel Build Script for MediQA

# Make sure the script exits on any error
set -e

echo "Starting Vercel build script..."

# Make sure the target directory exists
mkdir -p .vercel/output/static/attached_assets

# Copy the document to the static output directory
echo "Copying pharmacy_guide.docx to deployment output..."
cp attached_assets/pharmacy_guide.docx .vercel/output/static/attached_assets/

# Ensure we have requirements installed
echo "Installing Python requirements..."
pip install -r requirements.txt

echo "Build process completed successfully!"