from flask import Flask, render_template, request, session, redirect, url_for
import requests
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_super_secret_key"  # Add this line

categories = [
    "Housing",
    "Clothing and footwear",
    "Transport",
    "Alcohol and tobacco",
    "Food and non-alcoholic beverages",
    "Furnishings, household equipment and services",
    "Insurance and financial services",
    "Communication",
    "Health",
    "Recreation and culture",
    "Education",
]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "")
        session["name"] = name
        return redirect(url_for("form"))

    return render_template("index.html")


@app.route("/form", methods=["GET"])
def form():
    name = session.get("name", "")
    average_spend = (
        pd.read_csv("average_spend.csv")
        .set_index("categories")["weekly_spend"]
        .to_dict()
    )
    average_spend = {k: v * 13 for k, v in average_spend.items()}
    return render_template(
        "form.html", categories=categories, name=name, average_spend=average_spend
    )


@app.route("/forecast", methods=["POST"])
def forecast():
    actual_cpi_fn = "./last_quarter_cpi.csv"
    dat = pd.read_csv(actual_cpi_fn)

    filled_categories = {}
    form_results = {}
    for name in categories:
        value = request.form.get(name, "")
        try:
            form_results[name] = float(value) if value.strip() != "" else 0.0
        except ValueError:
            form_results[name] = 0.0
    total_spending = sum(form_results.values())
    payload = {"basket_idx": 0, "period": 1}
    try:
        endpoint_url = "https://cpiforecasting-app.azurewebsites.net/api/forecast"
        # endpoint_url = "http://localhost:7071/api/forecast"
        resp = requests.post(endpoint_url, json=payload)
        resp.raise_for_status()
        external_response = resp.json()  # list of dicts with basket_name and forecast
        # print(f"DEBUG: External response: {external_response}")

        forecast_map = {
            item["basket_name"]: item["forecast"] for item in external_response
        }
        print(f"DEBUG: Forecast map: {forecast_map}")

        endpoint_weights = "https://cpiforecasting-app.azurewebsites.net/api/cpi_weights"
        # endpoint_weights = "http://localhost:7071/api/cpi_weights"
        resp2 = requests.get(endpoint_weights)
        resp2.raise_for_status()
        cpi_weights = resp2.json()
        print(f"DEBUG: CPI weights: {cpi_weights}")

        # Calculate personal inflation rate
        if total_spending > 0:
            for name in categories:
                proportion = form_results[name] / total_spending
                cpi = forecast_map.get(name + "_qoq", 0)
                last_quarter_cpi = float(dat[name].values[0])
                personal_inflation_forecast = proportion * cpi
                personal_inflation_actual = proportion * last_quarter_cpi

                if name not in filled_categories:
                    filled_categories[name] = {}

                filled_categories[name] = {
                    "forecast_cpi": cpi,
                    "last_quarter_cpi": last_quarter_cpi,
                    "quarterly_spend": form_results[name],
                    "personal_inflation_forecast": personal_inflation_forecast,
                    "personal_inflation_actual": personal_inflation_actual,
                    "cpi_weights": float(cpi_weights.get(name, 0)),
                }
        else:
            raise ValueError("Total spending must be greater than zero.")

        error_message = None
    except Exception as e:
        error_message = str(e)

    personal_inflation_rate = sum(
        item["personal_inflation_forecast"] for item in filled_categories.values()
    )
    personal_inflation_actual = sum(
        item["personal_inflation_actual"] for item in filled_categories.values()
    )

    # NOTE I think these aren't particularly correct calculations
    # total_values = {
    #     "forecast_cpi": sum(item["forecast_cpi"] for item in filled_categories.values()),
    #     "last_quarter_cpi": sum(
    #         item["last_quarter_cpi"] for item in filled_categories.values()
    #     ),
    #     "quarterly_spend": sum(
    #         item["quarterly_spend"] for item in filled_categories.values()
    #     ),
    #     "personal_inflation_forecast": personal_inflation_rate,
    #     "personal_inflation_actual": personal_inflation_actual,
    # }
    user_name = session.get("name", "")  # Get user name from session
    return render_template(
        "forecast.html",
        personal_inflation_rate=personal_inflation_rate,
        personal_inflation_actual=personal_inflation_actual,
        filled_categories=filled_categories,
        # total_values=total_values,
        error_message=error_message,
        name=user_name,
    )


if __name__ == "__main__":
    app.run(debug=True)
