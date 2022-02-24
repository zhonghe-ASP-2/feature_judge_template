from feature_judge import *

import sys
sys.path.append("../code_for_test")
from util import *
import pandas as pd
from statsmodels.tsa.stattools import adfuller as ADF
import numpy as np


if __name__ == "__main__":
    # 更改需要计算的时间序列路径
    timeseries_name = "stable_example"
    config_path = "../config/" + timeseries_name
    image_path = "../images/" + timeseries_name
    timeseries_path = "../data/" + timeseries_name + ".csv"
    trend_config, threshold_config, resample_frequency = read_config(config_path)
    timeseries = read_timeseries(timeseries_path, str(resample_frequency) + "min")
    ts_numeric = pd.to_numeric(timeseries)
    std_value = np.std(ts_numeric)
    # 除以的是n
    print(std_value)
    ts_numeric_frame = pd.DataFrame(ts_numeric)
    mad_value = ts_numeric_frame.mad().get(0)
    print("mad value is {:.3f}".format(mad_value))
