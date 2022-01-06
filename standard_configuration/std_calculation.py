from feature_judge import *

import sys
sys.path.append("../code")
from util import *
import pandas as pd
from statsmodels.tsa.stattools import adfuller as ADF
import numpy as np


if __name__ == "__main__":
    # 更改需要计算的时间序列路径
    timeseries_name = "wave_test"
    config_path = "../config/" + timeseries_name
    image_path = "../images/" + timeseries_name
    timeseries_path = "../data/" + timeseries_name + ".csv"
    trend_config, threshold_config, resample_frequency = read_config(config_path)
    timeseries = read_timeseries(timeseries_path, str(resample_frequency) + "min")
    ts_numeric = pd.to_numeric(timeseries)
    std_value = np.std(ts_numeric)
    # 除以的是n
    print(std_value)