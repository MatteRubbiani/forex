from constants import *
import numpy as np

import requests
import json
import time
from termcolor import colored

now = time.time()
from_ = now - TIME_DELTA

instrument = "AUD_USD"
url = BASE_URL + "v3/instruments/%s/candles" % instrument

def difference(candle):
    return float(candle["mid"]["c"]) - float(candle["mid"]["o"])


def moving_average(n, arr):
    sum = 0
    for i in range(n+1, 1, -1):
        new_arr = arr[:i]
        sum += np.average(new_arr)
    return sum / n


print(moving_average(3, [1, 2, 3]))
"""
def hour_trend(days):
    time_delta = days * 60 * 60
    parameters = {
        "granularity": "H1",
        "from": now - time_delta,
        "to": now
    }

    headers = {'Content-Type': ': application/json', "Authorization": "Bearer %s" % API_KEY,
               "accountID": ACCOUNT_NUMBER}

    r = requests.get(url, headers=headers, params=parameters)

    r = json.loads(r.text)
    candles = r["candles"]
    candles_values = [difference(i) for i in candles]
    c = np.asarray(candles_values)
    last_four = c[-4:]

    return last_four


print(json.dumps(list(hour_trend(30)), indent=4))
"""