import sys
import json
import requests
import pandas as pd

class ABSData:
    def __init__(self, dataflow_id, debug=False):

        # dataflow_id = 'CPI'
        # MEASURE.INDEX.TSEST.REGION.FREQ

        self.debug = debug

        self.dataflow_id = dataflow_id
        self.base_url = "https://data.api.abs.gov.au:443/rest"
        self.url = f"{self.base_url}/data/{self.dataflow_id}"

        self.api_data = None
        self.data_key = None
        self.status_code = None

        self.obs = None
        self.obs_columns = None

        self.series_keys = None
        self.dims = None

    def _set_observation_struct(self):

        self.obs = self.api_data['data'] \
                            ['structures'] \
                            [0] \
                            ['dimensions'] \
                            ['observation'] \
                            [0] \
                            ['values']

        self.obs_columns = list(self.obs[0].keys())

    def _set_dimensions(self):
        # TODO: Need smarter implementation
        # Maybe it's own class Dimensions..?

        self.dims = self.api_data['data'] \
                                    ['structures'] \
                                    [0] \
                                    ['dimensions'] \
                                    ['series']

        # TODO: For now I'll assume the order of the dimensions is correct
        # but the proper way is to check keyPosition value

    def _set_series_keys(self):

        self.series_keys = list(self.api_data['data']['dataSets'][0]['series'].keys())

    def _get_series_values(self, key):

        return self.api_data['data'] \
                                ['dataSets']\
                                [0]\
                                ['series']\
                                [key]\
                                ['observations']

    def _call_api_data(self, url, headers):

        response = requests.get(url, headers=headers)
        self.status_code = response.status_code

        if self.status_code != 200:
            raise ValueError(f"API response code -> {self.status_code}")

        self.api_data = response.json()

        self._set_observation_struct()
        self._set_series_keys()
        self._set_dimensions()

        print(f"MSG: Data loaded for -> {self.data_key}")

    def call_api_data(self, data_key, start=None):
        """
        Call the ABS API to get the data

        Args:
            data_key (str): The data key to use
            start (str): The start date to use
        Returns:
            int: The status code of the request
        """
        # TODO: add smart handling of data_key
        # create self.data_key, if data_key != self.data_key then call the api with new data_key

        url = f"{self.url}/{data_key}"

        if start:
            url += f"?startPeriod={start}"

        if self.debug:
            print(f"DEBUG: Requesting -> {url}")

        headers={'accept': 'application/vnd.sdmx.data+json'}

        if self.data_key is not None and self.data_key != data_key:
            self._call_api_data(url, headers)
        elif self.api_data is None:
            self._call_api_data(url, headers)

        return f"MSG: API response code -> {self.status_code}"

    def get_observation(self):
        if self.obs:
            return self.obs
        else:
            raise ValueError("No observation data available, call call_api_data() first")

    def get_observation_columns(self):
        if self.obs_columns:
            return self.obs_columns
        else:
            raise ValueError("No observation columns available, call call_api_data() first")

    def get_api_data(self):
        if self.api_data:
            return self.api_data
        else:
            raise ValueError("No data available, call call_api_data() first")


    def make_table(self):

        res = []

        for series_key in self.series_keys:
            # TODO: I need to break up the key into indecies
            idx = list(map(int, series_key.split(':')))

            if self.debug:
                print(f"DEBUG: Indices -> {idx}")

            # TODO: Now I need to look up dimensions based on the index
            # But I don't know how to figure out which dimension I need..?
            keep = [1, 3, 4]

            series = self._get_series_values(series_key)
            # print(f"DEBUG: Series type -> {type(series)}")

            for i, o in enumerate(self.obs):
                t = {}

                # print(f"DEBUG: Observation -> {o}")
                # print(f"DEBUG: Series -> {series}")
                # print(f"DEBUG: i -> {i}")

                t['start'] = o['start']
                t['end'] = o['end']
                # t['cal_quarter'] = o['name'].split('-')[-1]
                t['cal_quarter'] = o['name']
                t['cpi_value'] = series[str(i)][0] # The index has to come from somewhere ..? This causes a bug if filtering on year

                # t['decimal'] = series[str(i)][2]

                for i in range(len(idx)):
                    if i in keep:
                        k = self.dims[i]['name']
                        v = self.dims[i]['values'][idx[i]]['name']
                        t[k] = v

                res.append(t)

        return pd.DataFrame(res)