from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

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

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", categories=categories)

@app.route("/forecast", methods=["POST"])
def forecast():
    results = {}
    for name in categories:
        value = request.form.get(name, "")
        try:
            results[name] = float(value) if value.strip() != "" else 0.0
        except ValueError:
            results[name] = 0.0
    total_spending = sum(results.values())
    payload = {
        "basket_idx": 0,
        "period": 1
    }
    try:
        endpoint_url = "https://cpiforecasting-app.azurewebsites.net/api/forecast"
        resp = requests.post(endpoint_url, json=payload)
        resp.raise_for_status()
        external_response = resp.json()  # list of dicts with basket_name and forecast

        forecast_map = {item["basket_name"]: item["forecast"] for item in external_response}

        # Calculate personal inflation rate
        personal_inflation_rate = 0.0
        if total_spending > 0:
            for name in categories:
                proportion = results[name] / total_spending
                cpi = forecast_map.get(name, 0)
                personal_inflation_rate += proportion * cpi
        else:
            personal_inflation_rate = 0.0

        # Prepare filled categories and their CPI
        filled_categories = [
            {"name": name, "cpi": forecast_map.get(name, 0), "amount": results[name]}
            for name in categories if results[name] > 0
        ]

        error_message = None
    except Exception as e:
        personal_inflation_rate = None
        filled_categories = []
        error_message = str(e)

    return render_template(
        "forecast.html",
        personal_inflation_rate=personal_inflation_rate,
        filled_categories=filled_categories,
        error_message=error_message
    )

if __name__ == "__main__":
    app.run(debug=True)