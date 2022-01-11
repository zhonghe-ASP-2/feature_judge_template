from feature_judge import *
from util import *


if __name__ == "__main__":
    timeseries_name = "064MP"
    config_path = "../config/" + timeseries_name
    image_path = "../images/" + timeseries_name
    timeseries_path = "../data/" + timeseries_name + ".csv"
    trend_config, threshold_config, timeseries_config, resample_frequency = read_config(config_path)
    timeseries = read_timeseries(timeseries_path, timeseries_config, str(resample_frequency)+"min")
    Dplot = 'yes'
    s_tf = trend_features(timeseries, timeseries_name, trend_config, image_path, Dplot, "")
    print(s_tf)
    s_tf1 = threshold_features(timeseries, timeseries_name, threshold_config, image_path, Dplot)
    print(s_tf1)

