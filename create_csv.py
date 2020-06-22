import openpyxl
from constants import *
import time
import requests
import json
import numpy
import matplotlib
import matplotlib.pyplot as plt

now = time.time()


def get_data(instrument="EUR_GBP", granularity="M15", time_delta=100000):
    url = BASE_URL + "v3/instruments/%s/candles" % instrument
    parameters = {
        "granularity": granularity,
        "from": now - time_delta,
        "to": now
    }

    headers = {'Content-Type': ': application/json', "Authorization": "Bearer %s" % API_KEY,
               "accountID": ACCOUNT_NUMBER}

    r = requests.get(url, headers=headers, params=parameters)

    d = json.loads(r.text)
    d = d["candles"]
    new = []
    for i in d:
        time_ = i["time"]
        mid = i["mid"]
        o = mid["o"]
        c = mid["c"]
        h = mid["h"]
        l_ = mid["l"]
        obj = [instrument, time_, o, c, h, l_]
        new.append(obj)
    return new

def normalize_array(arr):
    mean = 0
    tot = 0
    for i in arr:
        if i:
            mean += i
            tot += 1
    mean = mean / tot
    return [i - mean if i else None for i in arr]



def convert_array_to_dict(arr):
    instrument = [arr[i][0] for i in range(len(arr))]
    time_ = [arr[i][1] for i in range(len(arr))]
    open_ = numpy.asarray([arr[i][2] for i in range(len(arr))], dtype=numpy.float)
    close_ = numpy.asarray([arr[i][3] for i in range(len(arr))], dtype=numpy.float)
    high = numpy.asarray([arr[i][4] for i in range(len(arr))], dtype=numpy.float)
    low = numpy.asarray([arr[i][5] for i in range(len(arr))], dtype=numpy.float)
    dict_ = dict(instrument=instrument, time=time_, open=open_, close=close_, high=high, low=low)
    return dict_


def add_open_close_difference_col(dict_):
    close = dict_["close"]
    open_ = dict_["open"]
    dif = close - open_
    dict_["dif"] = normalize_array(dif)
    return dict_


def add_mean(dict_, n):
    close_ = dict_["close"]
    mean_n = []
    for i in range(0, n+1):
        mean_n.append(None)
    for i in range(n+1, len(close_)):
        arr = close_[i-n:i]
        print(arr)
        mean_ = numpy.mean(arr)
        mean_n.append(mean_)
    dict_["mean_%s" % n] = normalize_array(mean_n)
    return dict_

def plot_data(instrument, granularity, time_delta, means):
    data = get_data(instrument=instrument, granularity=granularity, time_delta=time_delta)
    data = convert_array_to_dict(data)
    data = add_open_close_difference_col(data)
    fig, ax = plt.subplots()
    time = [15 * i for i in range(len(data["open"]))]
    for m in means:
        data = add_mean(data, m)
        ax.plot(time, data["mean_%s" % m], label="mean %s" % m)
        ax.plot(time, numpy.gradient([i if i else 0 for i in data["mean_%s" % m]]), label="mean %s gradient" % m)


    gradient = numpy.gradient(data["close"])
    gradient1 = numpy.gradient(gradient)
    gradient2 = numpy.gradient(gradient1)

    ax.plot(time, gradient, label="gradient")
    #ax.plot(time, gradient1, label="gradient1")
    #ax.plot(time, gradient2, label="gradient2")

    ax.plot(time, normalize_array(data["close"]), label="close")
    leg = ax.legend()

    ax.set(xlabel=granularity, ylabel='',
           title=instrument)
    ax.grid(alpha=0.2, )
    plt.show()


plot_data("EUR_CHF", "M15", 100000, [8])