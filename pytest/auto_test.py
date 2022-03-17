import sys
sys.path.append(r"E:\github\feature_judge_template")
sys.path.append(r"E:\github\feature_judge_template\code_for_test")
from code_for_test.feature_judge import *

def arch_main(_timeseries_name,
              _data_source,
              _trend_presgaes_status = [0 for i in range(12)],
              _threshold_presages_status = [0 for i in range(6)],
              check_trend = False,
              check_threshold = False):
    timeseries_name = _timeseries_name
    # option: iotdb, csv
    data_source = _data_source
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
    if check_trend:
        assert s_tf == _trend_presgaes_status
    s_tf1 = threshold_features(timeseries, timeseries_name, threshold_config, image_path, Dplot)
    print(s_tf1)
    if check_threshold:
        assert s_tf1 == _threshold_presages_status


def test_concave():
    timeseries_name = "concave"
    data_source = "csv"
    to_satisfy_trend_presage = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]

    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend = True)

# 凸函数测试
def test_convex():
    timeseries_name = "convex"
    data_source = "csv"
    to_satisfy_trend_presage = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend = True)


def test_rise1():
    timeseries_name = "rise_1"
    data_source = "csv"
    to_satisfy_trend_presage = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend=True)


def test_rise2():
    timeseries_name = "rise_2"
    data_source = "csv"
    to_satisfy_trend_presage = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend=True)


def test_rise3():
    timeseries_name = "rise_3"
    data_source = "csv"
    to_satisfy_trend_presage = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend=True)


def test_drop1():
    timeseries_name = "drop_1"
    data_source = "csv"
    to_satisfy_trend_presage = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend=True)


def test_drop2():
    timeseries_name = "drop_2"
    data_source = "csv"
    to_satisfy_trend_presage = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend=True)


def test_drop3():
    timeseries_name = "drop_3"
    data_source = "csv"
    to_satisfy_trend_presage = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend=True)


def test_stable():
    timeseries_name = "stable"
    data_source = "csv"
    to_satisfy_trend_presage = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend=True)


def test_stable_vibrate():
    timeseries_name = "stable_vibrate"
    data_source = "csv"
    to_satisfy_trend_presage = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    arch_main(timeseries_name, data_source, to_satisfy_trend_presage, check_trend=True)


def test_threshold_high_1():
    timeseries_name = "stable"
    data_source = "csv"
    to_satisfy_threshold_presgae = [1, 0, 0, 0, 0, 0]
    arch_main(timeseries_name, data_source, _threshold_presages_status=to_satisfy_threshold_presgae, check_threshold=True)


def test_threshold_high_2():
    timeseries_name = "high_2"
    data_source = "csv"
    to_satisfy_threshold_presgae = [0, 1, 0, 0, 0, 0]
    arch_main(timeseries_name, data_source, _threshold_presages_status=to_satisfy_threshold_presgae, check_threshold=True)


def test_threshold_high_3():
    timeseries_name = "high_3"
    data_source = "csv"
    to_satisfy_threshold_presgae = [0, 0, 1, 0, 0, 0]
    arch_main(timeseries_name, data_source, _threshold_presages_status=to_satisfy_threshold_presgae, check_threshold=True)


def test_threshold_low_1():
    timeseries_name = "low_1"
    data_source = "csv"
    to_satisfy_threshold_presgae = [0, 0, 0, 1, 0, 0]
    arch_main(timeseries_name, data_source, _threshold_presages_status=to_satisfy_threshold_presgae, check_threshold=True)


def test_threshold_low_2():
    timeseries_name = "low_2"
    data_source = "csv"
    to_satisfy_threshold_presgae = [0, 0, 0, 0, 1, 0]
    arch_main(timeseries_name, data_source, _threshold_presages_status=to_satisfy_threshold_presgae, check_threshold=True)


def test_threshold_low_3():
    timeseries_name = "low_3"
    data_source = "csv"
    to_satisfy_threshold_presgae = [0, 0, 0, 0, 0, 1]
    arch_main(timeseries_name, data_source, _threshold_presages_status=to_satisfy_threshold_presgae, check_threshold=True)

def test_connnection_iotdb():
    timeseries_name = "QF_01_1RCP604MP_AVALUE"
    data_source = "iotdb"

    arch_main(timeseries_name, data_source)

if __name__ == "__main__":
    test_threshold_high_2()