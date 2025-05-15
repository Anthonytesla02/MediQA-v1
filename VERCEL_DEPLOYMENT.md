# Vercel Deployment Guide for MediQA

This document explains how to properly deploy the MediQA application on Vercel.

## Requirements

1. A Vercel account connected to your GitHub repository
2. The `pharmacy_guide.docx` document in your `attached_assets` directory

## Deployment Steps

1. Push all code changes to your GitHub repository
2. In your Vercel dashboard, create a new project from the GitHub repository
3. Configure the following settings:

### Build and Output Settings

- **Framework Preset**: Select "Other" 
- **Build Command**: Leave default (Vercel will use the configuration in vercel.json)
- **Output Directory**: Leave default

### Environment Variables

Add the following environment variables:

- `MISTRAL_API_KEY`: Your Mistral AI API key
- `DATABASE_URL`: Your PostgreSQL database connection string
- `SESSION_SECRET`: A secret key for session management (or use the one in config.py)

## Important Notes

### Document Access

The MediQA application relies on accessing the document file `pharmacy_guide.docx` which is included in your repository. The application has been modified to use Vercel's static file serving capability to access this document.

### Known Limitations

1. **Document Access**: In some Vercel serverless environments, the application may have difficulty accessing the document. If you encounter the message "The medical guidelines document could not be loaded in this deployment environment", this is a known limitation with Vercel's serverless architecture.

2. **Database Persistence**: Ensure your `DATABASE_URL` points to an externally hosted PostgreSQL database (like Supabase, Neon, or Railway) as Vercel doesn't provide built-in database hosting.

3. **Cold Starts**: Vercel's serverless functions may experience "cold starts" where the first request after a period of inactivity takes longer to respond.

## Alternative Deployment Options

If you encounter persistent issues with document access on Vercel, consider using Render.com as described in the `DEPLOYMENT.md` file, which is better suited for this application's architecture.