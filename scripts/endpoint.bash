#!/bin/bash

payload='{
    "basket_idx": 0,
    "period": 1
}'

curl -X POST \
  -H "Content-Type: application/json" \
  -d "$payload" \
  https://cpiforecasting-app.azurewebsites.net/api/forecast
