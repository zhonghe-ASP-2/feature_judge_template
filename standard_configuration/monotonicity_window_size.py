from feature_judge import *

import sys
sys.path.append("../code_for_test")
from util import *
import pandas as pd
from statsmodels.tsa.stattools import adfuller as ADF

def monotonicity_increase(timeseries):
    for i in range(1, len(timeseries)):
        if timeseries[i] < timeseries[i - 1]:
            return False

    return True

def monotonicity_decrease(timeseries):
    for i in range(1, len(timeseries)):
        if timeseries[i] > timeseries[i-1]:
            return False

    return True


if __name__ == "__main__":
    # 更改需要计算的时间序列路径
    timeseries_name = "tu_or_monotocity"
    config_path = "../config/" + timeseries_name
    image_path = "../images/" + timeseries_name
    timeseries_path = "../data/" + timeseries_name + ".csv"
    trend_config, threshold_config, resample_frequency = read_config(config_path)
    timeseries = read_timeseries(timeseries_path, str(resample_frequency) + "min")
    window_size = 10
    exist_mononicity_windows = False
    print("时间序列的长度为{:d}".format(len(timeseries)))

    # 若最后单调的窗口太小，则不认为具有单调性
    for i in range(window_size, int(len(timeseries)-len(timeseries)/2)):
        timeseries_temp = timeseries.rolling(window=int(i)).mean()
        if monotonicity_decrease(timeseries_temp):
            exist_mononicity_windows = True
            print("window size = {:d}, 序列判定为单调下降".format(i))
            break
        if monotonicity_increase(timeseries_temp):
            exist_mononicity_windows = True
            print("window size = {:d}, 序列判定为单调上升".format(i))
            break

    if not exist_mononicity_windows:
        print("遍历完所有的窗口都不是单调时间序列")
    # trend_config, threshold_config, resample_frequency = read_config(config_path)
    # timeseries = read_timeseries(timeseries_path, str(resample_frequency)+"min")