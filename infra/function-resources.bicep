param location string
param functionAppName string
param storageAccountName string
param appInsightsName string

resource storageAccount 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource storageContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = {
  parent: blobService
  name: '${functionAppName}-code-container'
}

resource appServicePlan 'Microsoft.Web/serverfarms@2024-11-01' = {
  name: '${functionAppName}-plan'
  location: location
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
  }
  kind: 'functionapp'
  properties: {
    reserved: true
  }
}

// --- UPDATED FUNCTION APP RESOURCE ---
resource functionApp 'Microsoft.Web/sites@2024-11-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    // --- RE-ENABLED AND CORRECTED FUNCTIONAPPCONFIG ---
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          // Point the deployment to the storage container you've defined
          value: '${storageAccount.properties.primaryEndpoints.blob}${storageContainer.name}'
          authentication: {
            type: 'SystemAssignedIdentity'
          }
        }
      }
      runtime: {
        name: 'python'
        version: '3.12' // Set the Python version
      }
      scaleAndConcurrency: {
        instanceMemoryMB: 2048 // Required for FlexConsumption
        maximumInstanceCount: 40 // Also required, as per previous errors
      }
    }
    // appSettings are now managed by functionAppConfig for most settings
    siteConfig: {
      alwaysOn: false
    }
  }
}

resource webApp 'Microsoft.Web/sites@2024-11-01' = {
  name: '${functionAppName}-webapp'
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      alwaysOn: false
      appSettings: [
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
      ]
    }
  }
  identity: {
    type: 'SystemAssigned'
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

// The AppInsights connection string is now handled differently.
// For FlexConsumption, you can use the parent-child resource model.
resource appInsightsConnection 'Microsoft.Web/sites/config@2022-09-01' = {
  parent: functionApp
  name: 'appsettings'
  properties: {
    // AzureWebJobsStorage is still a required app setting
    AzureWebJobsStorage: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'

    // Application Insights connection string
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
  }
}


// --- NEW RESOURCE: ROLE ASSIGNMENT ---
// Grant the Function App's identity the Storage Blob Data Contributor role on the storage account
resource storageAccountRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${functionApp.id}-storage-role-assignment')
  scope: storageAccount
  properties: {
    roleDefinitionId: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/ba92f5b4-2d11-453d-a403-e96b0029c9fe' // Built-in Storage Blob Data Contributor role definition ID
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}
