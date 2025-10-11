targetScope = 'subscription'

@description('Location for all resources.')
param location string = 'Australia East'
param resourceNamePrefix string = 'cpiforecasting'

var functionAppName = '${resourceNamePrefix}-app'
var storageAccountName = toLower('${resourceNamePrefix}sa')
var appInsightsName = '${resourceNamePrefix}-ai'
var resourceGroupName = '${resourceNamePrefix}-rg'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
}

// Reference the newly created resource group for module scope
module functionResources './function-app.bicep' = {
  name: 'function-resources-deployment'
  scope: resourceGroup
  params: {
    location: location
    functionAppName: functionAppName
    storageAccountName: storageAccountName
    appInsightsName: appInsightsName
  }
}

module webAppResources './webapp.bicep' = {
  name: 'webapp-resources-deployment'
  scope: resourceGroup
  params: {
    location: location
    appServicePlanName: '${resourceNamePrefix}-asp'
    appServiceName: '${resourceNamePrefix}-webapp'
  }
}
