#!/bin/bash

function help() {
  echo "USAGE: ./$(basename ${0}) <local|remote>"
  echo ""
  echo "  Options:"
  echo ""
  echo "    - local  - user localhost url"
  echo "    - remote - user remote azure url"
  echo ""
}

payload='{
    "basket_idx": 0,
    "period": 1
}'

if [[ ${1} == "local" ]]; then
  url="http://localhost:7071/api/forecast"
elif [[ ${1} == "remote" ]]; then
  url="https://cpiforecasting-app.azurewebsites.net/api/forecast"
else
  help
  exit 1
fi

curl -X POST \
  -H "Content-Type: application/json" \
  -d "$payload" \
  ${url}
