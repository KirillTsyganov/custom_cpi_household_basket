#!/bin/bash

infra_dir='.'
main_bicep='main.bicep'
# params_file='parameters.private.json'

print_help() {
    echo ""
    echo "Usage: $0 [check|prod]"
    echo ""
    echo "  Options:"
    echo ""
    echo "    - check: Do a dry-run, will show infra changes "
    echo "    - prod:  Deploy the infrastructure"
    echo ""
}

run_what_if() {
    echo "MSG: Dry Run"

    az deployment sub what-if \
        --location AustraliaEast \
        --template-file "${infra_dir}/${main_bicep}"
        # --parameters "@${infra_dir}/${params_file}"
}

run_deployment() {
    echo "MSG: Applying new infrastructure"

    az deployment sub create \
        --location AustraliaEast \
        --template-file "${infra_dir}/${main_bicep}"
        # --parameters "@${infra_dir}/${params_file}"
}

case ${1} in
    check)
        run_what_if
        ;;
    prod)
        read -p "Are you sure you want to run the production deployment? (y/N) " -n 1 -r
        echo    # Move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            run_deployment
        else
            echo "Deployment cancelled."
        fi
        ;;
    *)
        print_help
        exit 1
        ;;
esac