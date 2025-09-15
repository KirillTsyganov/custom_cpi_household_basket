"""Class to manage and utilise ARIMA models for forecasting CPI baskets."""

import os
import pickle


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

        self.debug = debug

        self.artifacts_dir = artifacts_dir
        self.models = {}
        self._load_models()

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

    def forecast(self, basket_idx, period=1):
        """
        Forecast the next value(s) for a specific CPI basket using basket index

        Args:
            basket_idx (int): Index of the CPI basket to forecast.
            period (int): Number of quarters to forecast. Default is 1, meaning the next quarter.

        Returns:
            pd.Series: Forecasted values for the specified number of quarters.
        """

        assert period >= 1, "Period must be at least 1"
        assert isinstance(period, int), "Period must be an integer"

        # TODO: need to check if basket_idx is valid
        model = self.get_model(basket_idx)
        forecast = model.forecast(steps=period)

        return forecast
