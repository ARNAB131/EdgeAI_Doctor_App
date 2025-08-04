# Deploying VitalsPredictor to Google Cloud Run

This guide will walk you through deploying your Streamlit application to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account with billing enabled
2. **Google Cloud SDK**: Install the Google Cloud CLI
3. **Docker**: (Optional, but recommended for local testing)

## Step 1: Install Google Cloud SDK

### Windows
```powershell
# Download and install from:
# https://cloud.google.com/sdk/docs/install#windows
```

### macOS
```bash
# Using Homebrew
brew install --cask google-cloud-sdk

# Or download from:
# https://cloud.google.com/sdk/docs/install#mac
```

### Linux
```bash
# Download and install from:
# https://cloud.google.com/sdk/docs/install#linux
```

## Step 2: Set Up Your Google Cloud Project

1. **Create a new project** (or use existing):
   ```bash
   gcloud projects create YOUR_PROJECT_ID --name="VitalsPredictor"
   ```

2. **Set the project**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable billing** for your project in the Google Cloud Console

4. **Authenticate**:
   ```bash
   gcloud auth login
   ```

## Step 3: Configure Deployment

1. **Edit the deployment script**:
   - Open `deploy.ps1` (Windows) or `deploy.sh` (Linux/macOS)
   - Replace `your-project-id` with your actual Google Cloud Project ID
   - Optionally change the region (default: `us-central1`)

2. **Review the configuration**:
   - Service name: `vitalspredictor`
   - Memory: 1GB
   - CPU: 1 vCPU
   - Max instances: 10
   - Port: 8080

## Step 4: Deploy

### Using the Script (Recommended)

**Windows (PowerShell)**:
```powershell
.\deploy.ps1
```

**Linux/macOS**:
```bash
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment

If you prefer to deploy manually:

1. **Enable required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

2. **Build and push the image**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/vitalspredictor
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy vitalspredictor \
     --image gcr.io/YOUR_PROJECT_ID/vitalspredictor \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --memory 1Gi \
     --cpu 1 \
     --max-instances 10
   ```

## Step 5: Access Your Application

After successful deployment, you'll get a URL like:
```
https://vitalspredictor-xxxxxxxx-uc.a.run.app
```

## Configuration Options

### Environment Variables
You can add environment variables to your deployment:

```bash
gcloud run deploy vitalspredictor \
  --image gcr.io/YOUR_PROJECT_ID/vitalspredictor \
  --set-env-vars "KEY1=VALUE1,KEY2=VALUE2"
```

### Scaling Configuration
- **Min instances**: `--min-instances 0` (default)
- **Max instances**: `--max-instances 10` (default)
- **Memory**: `--memory 1Gi` (default)
- **CPU**: `--cpu 1` (default)

### Custom Domain
To use a custom domain:

1. **Map your domain**:
   ```bash
   gcloud run domain-mappings create \
     --service vitalspredictor \
     --domain your-domain.com \
     --region us-central1
   ```

2. **Update DNS** with the provided CNAME record

## Monitoring and Logs

### View Logs
```bash
gcloud logs read --service=vitalspredictor --limit=50
```

### Monitor in Console
Visit the Google Cloud Console → Cloud Run → vitalspredictor

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Permission Error**:
   - Ensure your account has the necessary IAM roles:
     - Cloud Run Admin
     - Cloud Build Editor
     - Service Account User

3. **Build Failures**:
   - Check that all dependencies are in `requirements.txt`
   - Verify the Dockerfile is correct
   - Check build logs: `gcloud builds log BUILD_ID`

4. **Runtime Errors**:
   - Check application logs: `gcloud logs read --service=vitalspredictor`
   - Verify environment variables are set correctly

### Cost Optimization

- **Set min instances to 0** for cost savings (cold starts)
- **Use appropriate memory/CPU** for your workload
- **Monitor usage** in Google Cloud Console

## Security Considerations

1. **Authentication**: Consider requiring authentication:
   ```bash
   gcloud run deploy vitalspredictor --no-allow-unauthenticated
   ```

2. **IAM**: Use least-privilege access
3. **Secrets**: Store sensitive data in Secret Manager
4. **HTTPS**: Cloud Run provides HTTPS by default

## Updates and Rollbacks

### Update Deployment
```bash
# Rebuild and redeploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/vitalspredictor
gcloud run deploy vitalspredictor --image gcr.io/YOUR_PROJECT_ID/vitalspredictor
```

### Rollback
```bash
# List revisions
gcloud run revisions list --service=vitalspredictor

# Rollback to specific revision
gcloud run services update-traffic vitalspredictor --to-revisions=REVISION_NAME=100
```

## Support

For issues with:
- **Google Cloud Run**: [Cloud Run Documentation](https://cloud.google.com/run/docs)
- **Streamlit**: [Streamlit Documentation](https://docs.streamlit.io/)
- **Docker**: [Docker Documentation](https://docs.docker.com/) 