#!/bin/bash

resource_group="cpiforecasting-rg"
function_app="cpiforecasting-app"

deploy_dir="modeling"
deploy_artifact="${deploy_dir}.zip"

origin=$(dirname ${BASH_SOURCE[0]})
echo "MSG: Origin script path: ${origin}"
cd ${origin}/../${deploy_dir}
echo "MSG: Current working directory: ${PWD}"

zip -r ${deploy_artifact} .

echo "MSG: Deploying Azure Function App"

az functionapp deployment source config-zip \
  --resource-group ${resource_group} \
  --name ${function_app} \
  --src ${deploy_artifact}

rm -rf ${deploy_artifact}