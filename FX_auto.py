import time
from twisted.internet import task, reactor
from termcolor import colored
from new_functions import *


instrument = "EUR_AUD"
GRANULARITIES = ["M1", "M5", "M15", "H1"]


def macd_(data, slow=10, fast=5, signal=9):
    s_m_a = moving_average(data, slow, "exponential")
    f_m_a = moving_average(data, fast, "exponential")
    signal_9 = moving_average(data, signal, "exponential")
    slow_line = - s_m_a + signal_9
    fast_line = - signal_9 + f_m_a
    diff_1 = slow_line[-1] - fast_line[-1]
    diff_2 = slow_line[-2] - fast_line[-2]
    if diff_1 < 0 and diff_2 > 0 or diff_1 > 0 and diff_2 < 0:
        slope = fast_line[-1] - fast_line[-2]
        return {"slope": slope, "value": fast_line[-1]}


def predict(to_, granularity):
    data_m1 = get_data(instrument, granularity, to_ - 61 * 60, to_)
    general_trend = get_general_trend(data_m1)
    prediction, macd = predict_from_array(data_m1) if predict_from_array(data_m1) else [None, None]
    return [prediction, general_trend * 1000, macd]


timeout = 60.0  # Sixty seconds


def doWork():
    now = int(time.time())
    data = get_data("EUR_AUD", "M1", now - 61 * 60, now)
    a = macd_(data)
    if not a:
        print("        WAIT")
        print("#####################")
    else:
        macd = a["value"]
        incrocio = a["slope"]
        if incrocio < 0:
            str_m1 = colored(incrocio * 10000, "red") + " SELL"
        else:
            str_m1 = colored(incrocio * 10000, "green") + " BUY"
        str_f_moving_average = colored(macd, "green") if macd > 0 else colored(macd, "red")
        str_time = str(time.strftime('%H:%M:%S', time.localtime(time.time())))
        print(str_time, str_m1, "  _______  ", str_f_moving_average)



def start_program():
    now = time.time()
    seconds_from_60 = now % 60
    wait = (90 - seconds_from_60) % 60
    time.sleep(60-wait)
    r = task.LoopingCall(doWork)
    r.start(timeout)  # call every sixty seconds
    reactor.run()


start_program()
