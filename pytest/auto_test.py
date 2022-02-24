import sys
sys.path.append(r"E:\github\feature_judge_template")
sys.path.append(r"E:\github\feature_judge_template\code_for_test")
from code_for_test.feature_judge import *

def test_concave():
    timeseries_name = "concave"
    # option: iotdb, csv
    data_source = "csv"
    iotdb_config = {
        "ip": "10.101.66.13",
        "port": "6667",
        "username": 'root',
        "passwd": 'root'
    }

    config_path = "../pytest_config/" + timeseries_name
    timeseries_path = "../pytest_data/" + timeseries_name + ".csv"
    trend_config, threshold_config, timeseries_config, resample_frequency = read_config(config_path)
    image_path = "../pytest_images/" + timeseries_name + "_" + timeseries_config["time_point"].split(' ')[0] + "/"

    if not os.path.exists(image_path):
        os.mkdir(image_path)
    if data_source == "csv":
        timeseries = read_timeseries(timeseries_path, timeseries_config, str(resample_frequency) + "min")
    elif data_source == "iotdb":
        end_time_str = timeseries_config["time_point"]
        end_time_unix_time = time.mktime(time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S"))
        start_time_unix_time = end_time_unix_time - timeseries_config["trend_range_day"] * 24 * 3600
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time_unix_time))
        timeseries_sql = "select re_sample(" + timeseries_name + ", 'every'='" + str(
            resample_frequency) + "m', 'interp'='linear')" + " from root.CNNP." + timeseries_name[
                                                                                  :2] + "." + timeseries_name[
                                                                                              3:5]
        timeseries_sql = timeseries_sql + " where time < " + end_time_str + " and time > " + \
                         start_time_str + ";"
        timeseries = read_timeseries_iotdb(timeseries_sql, resample_frequency, iotdb_config)

    Dplot = 'yes'
    s_tf = trend_features(timeseries, timeseries_name, trend_config, image_path, Dplot, "")
    assert  s_tf == [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
    s_tf1 = threshold_features(timeseries, timeseries_name, threshold_config, image_path, Dplot)
    assert s_tf1 == [0, 0, 0, 0, 0, 0]


def test_convex():
    timeseries_name = "convex"
    # option: iotdb, csv
    data_source = "csv"
    iotdb_config = {
        "ip": "10.101.66.13",
        "port": "6667",
        "username": 'root',
        "passwd": 'root'
    }

    config_path = "../pytest_config/" + timeseries_name
    timeseries_path = "../pytest_data/" + timeseries_name + ".csv"
    trend_config, threshold_config, timeseries_config, resample_frequency = read_config(config_path)
    image_path = "../pytest_images/" + timeseries_name + "_" + timeseries_config["time_point"].split(' ')[0] + "/"

    if not os.path.exists(image_path):
        os.mkdir(image_path)
    if data_source == "csv":
        timeseries = read_timeseries(timeseries_path, timeseries_config, str(resample_frequency) + "min")
    elif data_source == "iotdb":
        end_time_str = timeseries_config["time_point"]
        end_time_unix_time = time.mktime(time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S"))
        start_time_unix_time = end_time_unix_time - timeseries_config["trend_range_day"] * 24 * 3600
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time_unix_time))
        timeseries_sql = "select re_sample(" + timeseries_name + ", 'every'='" + str(
            resample_frequency) + "m', 'interp'='linear')" + " from root.CNNP." + timeseries_name[
                                                                                  :2] + "." + timeseries_name[
                                                                                              3:5]
        timeseries_sql = timeseries_sql + " where time < " + end_time_str + " and time > " + \
                         start_time_str + ";"
        timeseries = read_timeseries_iotdb(timeseries_sql, resample_frequency, iotdb_config)

    Dplot = 'yes'
    s_tf = trend_features(timeseries, timeseries_name, trend_config, image_path, Dplot, "")
    assert  s_tf == [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    s_tf1 = threshold_features(timeseries, timeseries_name, threshold_config, image_path, Dplot)
    assert s_tf1 == [0, 0, 0, 0, 0, 1]

