#!/bin/bash

origin=$(dirname ${BASH_SOURCE[0]})

echo "MSG: Origin -> ${origin}"

python ${origin}/get_cpi_data.py
# regular snapshot
# python ${origin}/fetch_crude_oil_data.py 
# historical take
# python ${origin}/fetch_crude_oil_data.py --start_days_ago 1973-01-01 --end_days_ago 2025-10-03

# regular snapshot
# python ${origin}/get_fx_data.py 