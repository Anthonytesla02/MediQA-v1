# Vercel Deployment Guide for MediQA

This document explains how to properly deploy the MediQA application on Vercel.

## Requirements

1. A Vercel account connected to your GitHub repository
2. The `pharmacy_guide.docx` document in your `attached_assets` directory
3. PostgreSQL database (Vercel doesn't provide this, so you'll need an external service)

## Deployment Steps

1. **Ensure your repository is up to date**
   - The repository must include the `pharmacy_guide.docx` file in the `attached_assets` directory
   - Make sure you have the latest version of `vercel.json` and `vercel-build.sh`

2. **Connect your GitHub repository to Vercel**
   - Log in to Vercel dashboard
   - Click "Add New" → "Project"
   - Select your GitHub repository

3. **Configure the deployment settings**
   - **Framework Preset**: Select "Other" 
   - **Build Command**: Leave default (Vercel will use the configuration in vercel.json)
   - **Output Directory**: Leave default
   - **Root Directory**: Leave as `.` (root of the repository)

4. **Set up Environment Variables**
   - In the project settings, add the following environment variables:
     - `MISTRAL_API_KEY`: Your Mistral AI API key
     - `DATABASE_URL`: Your PostgreSQL database connection string
     - `SESSION_SECRET`: A secret key for session management
     - `VERCEL`: Set to `1` (to enable Vercel-specific document handling)

5. **Deploy the Project**
   - Click "Deploy" to start the deployment process
   - The build script will automatically copy the document file to the right locations

## How This Deployment Works

The deployment uses a custom build script (`vercel-build.sh`) to ensure the document is accessible in the Vercel environment:

1. During build, the document is copied to multiple locations:
   - To `.vercel/output/static/attached_assets/` for serving as a static file
   - To `/tmp/attached_assets/` for direct filesystem access by the application

2. The application has been modified to look for the document in these locations when running on Vercel.

## Troubleshooting

If you encounter issues with document access:

1. **Check build logs**
   - Verify that the `vercel-build.sh` script executed successfully
   - Look for messages confirming the document was copied correctly

2. **Try redeploying**
   - Sometimes a fresh deployment can resolve issues

3. **Check environment variables**
   - Ensure the `VERCEL` environment variable is set to `1`

4. **Verify document is in the repository**
   - The `pharmacy_guide.docx` must be committed to your repository in the `attached_assets` directory

## Alternative Deployment Options

If you continue to experience issues with Vercel deployment, consider using Render.com as described in the `DEPLOYMENT.md` file. Render's architecture is better suited for applications that require persistent file access and background processing.