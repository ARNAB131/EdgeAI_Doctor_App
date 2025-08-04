# Google Cloud Run Deployment Script for VitalsPredictor (PowerShell)

# Configuration
$PROJECT_ID = "vitals-467103"  # Your Google Cloud Project ID
$SERVICE_NAME = "vitalspredictor"
$REGION = "us-central1"  # Change to your preferred region
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "🚀 Starting deployment to Google Cloud Run..." -ForegroundColor Green

# Check if gcloud is installed
try {
    $null = Get-Command gcloud -ErrorAction Stop
} catch {
    Write-Host "❌ Google Cloud SDK is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Check if user is authenticated
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $authStatus) {
    Write-Host "🔐 Please authenticate with Google Cloud:" -ForegroundColor Yellow
    gcloud auth login
}

# Set the project
Write-Host "📋 Setting project to: $PROJECT_ID" -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "🔧 Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Build and push the Docker image
Write-Host "🏗️  Building and pushing Docker image..." -ForegroundColor Cyan
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
Write-Host "🚀 Deploying to Cloud Run..." -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --memory 1Gi `
    --cpu 1 `
    --max-instances 10

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your application is available at:" -ForegroundColor Cyan
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
Write-Host $serviceUrl -ForegroundColor Yellow 