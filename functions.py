from constants import *
import requests
import json
import numpy as np


def get_data(instr, granularity, from_, to_):
    url = BASE_URL + "v3/instruments/%s/candles" % instr

    parameters = {
        "granularity": granularity,
        "from": from_,
        "to": to_
    }

    headers = {'Content-Type': ': application/json', "Authorization": "Bearer %s" % API_KEY,
               "accountID": ACCOUNT_NUMBER}

    r = requests.get(url, headers=headers, params=parameters)

    r = json.loads(r.text)
    candles = r["candles"]
    return np.asarray([float(i["mid"]["c"]) for i in candles])


def moving_average(n, arr):
    sum = 0
    for i in range(n, 0, -1):
        new_arr = arr[-i:]
        sum += np.average(new_arr)
    return sum / n


def predict_from_array(data_m1):
    minutes = 1
    data_m5 = [data_m1[k] for k in range(len(data_m1)) if k % minutes == minutes - 1]
    fast_k = 3
    slow_k = 15
    ma_m5_slow = moving_average(slow_k, data_m5)
    ma_m5_fast = moving_average(fast_k, data_m5)

    macd = ma_m5_slow - ma_m5_fast

    ma_m5_slow_previous = moving_average(slow_k, data_m5[:-1])
    ma_m5_fast_previous = moving_average(fast_k, data_m5[:-1])

    ma_m5_difference = ma_m5_slow - ma_m5_fast
    ma_m5_difference_previous = ma_m5_slow_previous - ma_m5_fast_previous

    ma_m5_increase = ma_m5_fast - ma_m5_fast_previous
    if ma_m5_difference_previous < 0 and ma_m5_difference > 0 or ma_m5_difference_previous > 0 and ma_m5_difference < 0:
        return [ma_m5_increase * 10000, -macd * 10000]
    return [None, -macd]


def get_general_trend(data_m1):
    ma_m1 = moving_average(21, data_m1[-1:])
    ma_m1_previous = moving_average(21, data_m1[-2:])
    return ma_m1_previous - ma_m1