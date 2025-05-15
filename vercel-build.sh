#!/bin/bash
# Vercel Build Script for MediQA

# Make sure the script exits on any error
set -e

echo "===== Starting Vercel build script... ====="

# Debug: Show current directory and list files
echo "Current directory: $(pwd)"
echo "Listing attached_assets directory:"
ls -la attached_assets/

# Make sure target directories exist (multiple possible locations)
echo "Creating output directories..."
mkdir -p .vercel/output/static/attached_assets
mkdir -p /tmp/attached_assets

# Copy the document to multiple possible locations for redundancy
echo "Copying pharmacy_guide.docx to deployment output locations..."

# Copy to .vercel output directory (for static file serving)
if [ -f "attached_assets/pharmacy_guide.docx" ]; then
    cp attached_assets/pharmacy_guide.docx .vercel/output/static/attached_assets/
    echo "✓ Copied to .vercel/output/static/attached_assets/"
    
    # Verify the copy was successful
    if [ -f ".vercel/output/static/attached_assets/pharmacy_guide.docx" ]; then
        echo "✓ Verified file exists in .vercel/output/static/attached_assets/"
        ls -la .vercel/output/static/attached_assets/
    else
        echo "✗ Failed to verify file in .vercel/output/static/attached_assets/"
    fi
else
    echo "✗ Source file attached_assets/pharmacy_guide.docx not found!"
fi

# Also copy to /tmp for function access
cp attached_assets/pharmacy_guide.docx /tmp/attached_assets/
echo "✓ Copied to /tmp/attached_assets/"

# Ensure we have requirements installed
echo "Installing Python requirements..."
pip install -r requirements.txt

echo "===== Build process completed! ====="
echo "Document placed in the following locations:"
echo "- .vercel/output/static/attached_assets/pharmacy_guide.docx (for URL access)"
echo "- /tmp/attached_assets/pharmacy_guide.docx (for direct filesystem access)"