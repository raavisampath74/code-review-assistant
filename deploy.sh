#!/bin/bash
# Deploy Code Review Assistant to Google Cloud Run
# Usage: ./deploy.sh YOUR_PROJECT_ID

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Code Review Assistant - Deployment   ${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if project ID is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide your GCP Project ID${NC}"
    echo "Usage: ./deploy.sh YOUR_PROJECT_ID"
    exit 1
fi

PROJECT_ID=$1
REGION="us-central1"
SERVICE_NAME="code-review-assistant"

echo -e "\n${YELLOW}Step 1: Setting up GCP project...${NC}"
gcloud config set project $PROJECT_ID

echo -e "\n${YELLOW}Step 2: Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo -e "\n${YELLOW}Step 3: Building and deploying...${NC}"
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete! 🚀${NC}"
echo -e "${GREEN}========================================${NC}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo -e "\n${GREEN}Your app is live at:${NC}"
echo -e "${YELLOW}$SERVICE_URL${NC}"
