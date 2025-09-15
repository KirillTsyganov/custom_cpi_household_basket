# %%
import os
from forecast_models import ForecastModels
import azure.functions as func
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, 'artifacts')

models = ForecastModels(artifacts_dir=models_dir)

def main(req: func.HttpRequest) -> func.HttpResponse:
    # 1. Get the JSON payload from the request body
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Please pass a valid JSON payload in the request body.", status_code=400
        )

    # 2. Extract the values from the JSON
    try:
        basket_idx = req_body.get("basket_idx")
        period = req_body.get("period")
    except (TypeError, KeyError):
        return func.HttpResponse(
            "Please ensure 'basket_idx' and 'period' are present in the JSON payload.",
            status_code=400,
        )

    # 3. Use the extracted values in your model
    models.forecast(basket_idx, period)
    forecast_result = models.results()

    # 4. Return the result in a JSON response
    return func.HttpResponse(
        json.dumps(forecast_result), mimetype="application/json", status_code=200
    )
