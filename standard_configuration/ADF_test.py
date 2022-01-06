from feature_judge import *

import sys
sys.path.append("../code")
from util import *
import pandas as pd
from statsmodels.tsa.stattools import adfuller as ADF



if __name__ == "__main__":
    # 更改需要计算的时间序列路径
    timeseries_name = "stable_vibration_example"
    config_path = "../config/" + timeseries_name
    image_path = "../images/" + timeseries_name
    timeseries_path = "../data/" + timeseries_name + ".csv"
    trend_config, threshold_config, resample_frequency = read_config(config_path)
    timeseries = read_timeseries(timeseries_path, str(resample_frequency) + "min")
    ts_numeric = pd.to_numeric(timeseries)
    test_result = ADF(ts_numeric)
    p_value = test_result[1]
    # 是否还需要进行滑窗，有待商榷，目前效果应该不错
    print('p-value:', p_value)
