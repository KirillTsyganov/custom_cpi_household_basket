#!/bin/bash

deploy_dir="app"
deploy_artifact="${deploy_dir}.zip"

origin=$(dirname ${BASH_SOURCE[0]})
echo "MSG: Origin script path: ${origin}"
cd ${origin}/../${deploy_dir}

# echo "" >> "requirements.txt"
# echo "gunicorn==20.1.0" >> "requirements.txt"

# echo "gunicorn --bind=0.0.0.0 --timeout 600 run:app" > "startup.txt"

rg_name="cpiforecasting-rg"
webapp_name="cpiforecasting-webapp"

echo "MSG: Deployment stage"

zip -r ${deploy_artifact} .

az webapp \
        deploy \
            --resource-group ${rg_name} \
            --name ${webapp_name} \
            --src-path ${deploy_artifact} \
            --type zip

rm ${deploy_artifact}