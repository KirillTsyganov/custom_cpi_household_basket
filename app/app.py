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
    results = {
        name: request.form.get(name)
        for name in categories
    }
    # Example: using first category as basket_idx and a static period
    payload = {
        "basket_idx": request.form.get(categories[0]),
        "period": request.form.get("period", "2025")
    }
    try:
        resp = requests.post("https://external-endpoint.com", json=payload)
        resp.raise_for_status()
        external_response = resp.json()  # expecting a list of JSONs
    except Exception as e:
        external_response = [{"error": str(e)}]
    return render_template(
        "forecast.html",
        categories=categories,
        results=results,
        external_response=external_response
    )

if __name__ == "__main__":
    app.run(debug=True)