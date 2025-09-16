
resource_group="cpiforecasting-rg"
function_app="cpiforecasting-app"

az functionapp function list \
    --resource-group ${resource_group} \
    --name ${function_app}

# function_name="myfunction"

# az functionapp function show \
#     --resource-group ${resource_group} \
#     --name ${function_app} \
#     --function-name ${function_name}