import json
import pandas as pd
import azure.functions as func
from forecast_models import ForecastModels

models = ForecastModels(artifacts_dir="artifacts")

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="forecast", methods=["POST"])
def forecast_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Please pass a valid JSON payload in the request body.", status_code=400
        )

    try:
        basket_idx = req_body.get("basket_idx")
        period = req_body.get("period")
    except (TypeError, KeyError):
        return func.HttpResponse(
            "Please ensure 'basket_idx' and 'period' are present in the JSON payload.",
            status_code=400,
        )

    models.forecast(period=period, basket_idx=basket_idx)
    forecast_result = models.results()

    return func.HttpResponse(
        json.dumps(forecast_result), mimetype="application/json", status_code=200
    )


@app.route(route="cpi_weights", methods=["GET"])
def cpi_weights_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        dat = pd.read_csv("artifacts/cpi_weights_total_contribution.csv")
        weights = dat.set_index("group")["cpi_weights"].to_dict()
    except Exception as e:
        return func.HttpResponse(
            f"Error retrieving CPI weights: {str(e)}", status_code=500
        )

    return func.HttpResponse(
        json.dumps(weights), mimetype="application/json", status_code=200
    )
