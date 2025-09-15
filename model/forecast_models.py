"""Class to manage and utilise ARIMA models for forecasting CPI baskets."""

import os
import pickle
import pandas as pd


class ForecastModels:
    """
    Class to manage and utilise ARIMA models for forecasting CPI baskets.
    """

    def __init__(self, artifacts_dir="artifacts", debug=False):
        self._baskets = {
            "Housing": 1,
            "Clothing and footwear": 2,
            "Transport": 3,
            "Alcohol and tobacco": 4,
            "Food and non-alcoholic beverages": 5,
            "Furnishings, household equipment and services": 6,
            "Insurance and financial services": 7,
            "Communication": 8,
            "Health": 9,
            "Recreation and culture": 10,
            "Education": 11,
        }

        # self._baskets_rev = {v: k for k, v in self._baskets.items()}

        self.debug = debug

        self.artifacts_dir = artifacts_dir
        self.models = {}
        self._load_models()

        self.forecast_results = None

    def __repr__(self):
        msg = "ForecastModels("
        msg += "\n"
        msg += "\n"
        msg += f"  artifacts directory: {self.artifacts_dir}"
        msg += "\n"
        msg += f"  number of models: {len(self.models)}"
        msg += "\n"
        msg += "\n"
        msg += self.get_baskets_info()
        msg += "\n"
        msg += "\n"
        msg += ")"

        return msg

    def get_baskets_info(self):
        """
        Helper method to get information about available CPI baskets.

        Returns:
            str: A formatted string listing available CPI baskets and their indices.
        """

        baskets = "Available baskets:"
        baskets += "\n"

        for k, v in self._baskets.items():
            baskets += f"   - {v}  : {k}"
            baskets += "\n"

        return baskets.strip()

    def _load_models(self):
        """
        Internal method to load all ARIMA model files from the artifacts directory.

        Args:
            artifacts_dir (str): Directory where model artifacts are stored.

        Returns:
            dict: A dictionary with basket names as keys and model file paths as values.
        """

        _models = os.listdir(self.artifacts_dir)
        _models = [
            os.path.join(self.artifacts_dir, f)
            for f in _models
            if f.endswith("_arima_model.pkl")
        ]

        if self.debug:
            print(f"DEBUG: Found model files -> {_models}")

        for path in _models:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Model file {path} does not exist.")

            model_name = os.path.basename(path).replace("_arima_model.pkl", "")

            if model_name not in self._baskets:
                raise ValueError(f"Unexpected model name -> {model_name}")

            idx = self._baskets[model_name]

            self.models[idx] = path

    def get_model(self, basket_idx):
        """
        Retrieve the ARIMA model for a specific CPI basket using basket index
        """

        if basket_idx not in self.models:
            msg = f"Basket index not found -> {basket_idx}"
            msg += "\n"
            msg += self.get_baskets_info()

            raise ValueError(msg)

        model_path = self.models.get(basket_idx)

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        return model

    def forecast(self, period=1, basket_idx=None):
        """
        Forecast the next value(s) for all CPI baskets.

        Args:
            period (int): Number of quarters to forecast. Default is 1, meaning the next quarter.
            basket_idx (int, list): Index of the CPI basket to forecast. If None, forecasts all baskets.

        Returns:
            dict: A dictionary with basket indices as keys and their corresponding forecast results.
        """

        assert period >= 1, "Period must be at least 1"
        assert isinstance(period, int), "Period must be an integer"

        self.forecast_results = {}

        indices = list(self.models.keys())

        if basket_idx is not None:
            indices = [basket_idx]

        # print(f"DEBUG: Indices -> {indices}")

        for index in indices:
            model = self.get_model(index)
            results = model.get_forecast(steps=period)

            # TODO: overwrite previous results of a single forecasting.
            # I want to do that, but want to change messaging better
            if period not in self.forecast_results:
                self.forecast_results[period] = {}
            self.forecast_results[period][index] = results

    def get_forecast_results(self):
        """
        Get the latest forecast results.

        Returns:
            PredictionResults: The latest forecasted values and confidence intervals.
        """

        if self.forecast_results is None:
            raise ValueError(
                "No forecast has been made yet. run models.forecast() or models.forecast_all()"
            )

        return self.forecast_results

    def results(self, period=1, output_format="json"):
        """
        Prepare results for HTTP response

        Args:
            forecast_results (PredictionResults): The forecasted values and confidence intervals.
            output_format (str): Output format, either 'json' or 'dataframe'. Default is 'json'.
        Returns:
            dict: A dictionary containing the forecast and confidence intervals.
        """

        results = []

        for _, forecast_results in self.forecast_results[period].items():
            forecast = float(forecast_results.predicted_mean)
            # NOTE:
            # A 95% confidence interval means that
            # if you were to repeat this forecasting process 100 times,
            # you would expect the true value to fall within this range about 95 times.
            conf_int = forecast_results.conf_int()
            conf_int = conf_int.reset_index()
            # TODO: not very robust
            basket_name = conf_int.columns[1].split("lower ")[1]

            period = str(conf_int.iloc[0, 0])
            lower = float(conf_int.iloc[0, 1])
            upper = float(conf_int.iloc[0, 2])

            results.append(
                {
                    "basket_name": basket_name,
                    "period": str(period),
                    "forecast": forecast,
                    "conf_int": (lower, upper),
                }
            )

        if output_format == "dataframe":
            df = pd.DataFrame(results)
            df[["conf_int_lower", "conf_int_upper"]] = pd.DataFrame(
                df["conf_int"].tolist(), index=df.index
            )
            df = df.drop(columns=["conf_int"])

            return df

        return results
