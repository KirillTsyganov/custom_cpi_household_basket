# %%
from forecast_models import ForecastModels

models = ForecastModels()
models
# %%
basket_idx = 1  # Housing
period = 1 # Next quarter

# results = models.forecast(basket_idx, period)
results = models.forecast()
results
# %%
models.get_forecast_results()
# %%
models.results()
# %%
models.results(output_format='dataframe')
# %%
