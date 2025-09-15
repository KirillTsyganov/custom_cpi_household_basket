#!/bin/bash

RESOURCE_GROUP="cpi-forecasting-rg"
FUNCTION_APP="cpi-forecasting-app"
ZIP_PATH="./function.zip" # Path to your zipped function app code

echo "Publishing Azure Function App..."

az functionapp deployment source config-zip \
  --resource-group "$RESOURCE_GROUP" \
  --name "$FUNCTION_APP" \
  --src "$ZIP_PATH"

echo "Deployment complete."