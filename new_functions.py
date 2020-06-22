import json

import numpy as np
import requests
from constants import *


def moving_average(x, n, type='simple'):
    """
	compute an n period moving average.

	type is 'simple' | 'exponential'

	"""
    x = np.asarray(x)
    if type == 'simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()

    a = np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a


def relative_strength(prices, n=14):
    """
	compute the n period relative strength indicator
	http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
	http://www.investopedia.com/terms/r/rsi.asp
	"""

    deltas = np.diff(prices)
    seed = deltas[:n + 1]
    up = seed[seed >= 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100. / (1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (n - 1) + upval) / n
        down = (down * (n - 1) + downval) / n

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi


def moving_average_convergence(x, nslow=26, nfast=12):
    """
	compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
	return value is emaslow, emafast, macd which are len(x) arrays
	"""
    emaslow = moving_average(x, nslow, type='simple')
    emafast = moving_average(x, nfast, type='simple')
    return emaslow, emafast, emafast - emaslow


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


def predict_from_array(data_m1):
    ema_slow, ema_fast, ema_dif = moving_average_convergence(data_m1, nslow=15, nfast=5)
    if ema_dif[-2] < 0 and ema_dif[-1] > 0 or ema_dif[-2] > 0 and ema_dif[-1] < 0:
        return [ema_dif[-2] - ema_dif[-1], ema_slow[-1], ema_fast[-1], ema_dif[-1]]
    return [None, ema_slow[-1], ema_fast[-1], ema_dif[-1]]