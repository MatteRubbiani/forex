from new_functions import *
import time
SLOW_LINE = 25
FAST_LINE = 5


def macd(data, slow=SLOW_LINE, fast=FAST_LINE, signal=9):
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


now = int(time.time()) - 1 * 60 * 60 * 24
from_ = now - 24 * 60 * 60
data = get_data("EUR_AUD", "M1", from_, now)
crosses = []

for i in range(SLOW_LINE, len(data)):
    close = data[i]
    new_arr = data[:i+1]
    macd_ = macd(new_arr)
    date = str(time.strftime('%H:%M:%S', time.localtime(from_ + i * 60)))
    if macd_:
        macd_["date"] = date
        macd_["close"] = close
        crosses.append(macd_)
tot = 0
for i in range(len(crosses)-1):
    macd_ = crosses[i]
    macd_1 = crosses[i+1]
    difference = macd_1["close"] - macd_["close"]
    slope = macd_["slope"]
    difference = difference * -1 if slope < 0 else difference
    difference = difference * 30000
    difference = difference if difference > -15 else -15
    difference -= 5
    if macd_["value"] * macd_["slope"] < 0:
        if abs(macd_["value"] * 10000) > 1:
            print(macd_["date"], " --- ", macd_1["date"], "profit: ", difference, "macd slope: ", macd_["slope"] * 10000, "macd value: ", macd_["value"] * 10000)
            tot += difference

print(tot)

