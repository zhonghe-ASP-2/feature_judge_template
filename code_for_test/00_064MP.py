from feature_judge import *
from util import *


if __name__ == "__main__":
    # timeseries_name = "064MP"
    timeseries_name = "QF_01_1RCP604MP_AVALUE"
    # option: iotdb, csv
    data_source = "csv"
    iotdb_config = {
        "ip": "10.101.66.13",
        "port": "6667",
        "username": 'root',
        "passwd": 'root'
    }

    config_path = "../config/" + timeseries_name
    timeseries_path = "../data/" + timeseries_name + ".csv"



    trend_config, threshold_config, timeseries_config, resample_frequency = read_config(config_path)
    image_path = "../images/" + timeseries_name + "_"+timeseries_config["time_point"].split(' ')[0]+"/"
    if not os.path.exists(image_path):
        os.mkdir(image_path)
    if data_source == "csv":
        timeseries = read_timeseries(timeseries_path, timeseries_config, str(resample_frequency)+"min")
    elif data_source == "iotdb":
        end_time_str = timeseries_config["time_point"]
        end_time_unix_time = time.mktime(time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S"))
        start_time_unix_time = end_time_unix_time - timeseries_config["trend_range_day"] * 24 * 3600
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time_unix_time))
        timeseries_sql = "select re_sample(" + timeseries_name + ", 'every'='"+str(resample_frequency)+"m', 'interp'='linear')" + " from root.CNNP." + timeseries_name[
                                                                                                                                 :2] + "." + timeseries_name[
                                                                                                                                             3:5]
        timeseries_sql = timeseries_sql + " where time < " + end_time_str + " and time > " + \
                         start_time_str + ";"
        timeseries = read_timeseries_iotdb(timeseries_sql, resample_frequency, iotdb_config)
    Dplot = 'yes'
    s_tf = trend_features(timeseries, timeseries_name, trend_config, image_path, Dplot, "")
    print(s_tf)
    s_tf1 = threshold_features(timeseries, timeseries_name, threshold_config, image_path, Dplot)
    print(s_tf1)

