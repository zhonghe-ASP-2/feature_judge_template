import os

import matplotlib.pyplot as plt

from feature_judge import *
from util import *

if __name__ == "__main__":
    timeseries_name = "QF_01_1RCP604MP_AVALUE"
    # option: iotdb, csv
    # 推荐使用iotdb, csv是全量读入非常的慢
    data_source = "iotdb"
    iotdb_config = {
        "ip": "127.0.0.1",
        "port": "6667",
        "username": 'root',
        "passwd": 'root'
    }

    config_path = "../config/" + timeseries_name
    image_path = "../images/" + timeseries_name + "/"
    # 创建的图片保存目录
    if not os.path.exists(image_path):
        os.mkdir(image_path)
    timeseries_path = "../data/" + timeseries_name + ".csv"

    trend_config, threshold_config, timeseries_config, resample_frequency = read_config(config_path)

    # 遍历整个时间段，从而获取时间序列的误报率
    one_day = 60 * 60 * 24
    slide_step = 10

    if data_source == "csv":
        history_start_time, history_end_time = get_start_end_time(timeseries_path, data_source, {})
    elif data_source == "iotdb":
        history_start_time, history_end_time = get_start_end_time(timeseries_name, data_source, iotdb_config)


    # 失效时间段
    failure_segments = [['2019-04-20 00:00:00', '2019-06-20 00:00:00'],

                       ]

    # 大修时间段
    fix_segments = [
        ["2015-10-15 20:00:45", "2015-12-06 13:28:06"],
        ["2016-06-24 00:00:00", "2016-07-02 00:00:00"],
        ["2016-09-15 00:00:00", "2016-10-15 00:00:00"],
        ["2017-09-10 00:00:00", "2017-10-14 00:00:00"],
        ["2019-03-15 00:00:00", "2019-04-15 00:00:00"],
        ["2020-10-10 00:00:00", "2020-11-14 00:00:00"],
    ]
    failure_metric_x = []
    failure_metric_y = []

    # 遍历窗口的终止时间
    for watch_day in range(6, 61, 6):
        timeseries_config["trend_range_day"] = watch_day
        history_start_time_ = history_start_time + one_day * timeseries_config["trend_range_day"] * 1000
        tot = 0
        drop = 0
        right = 0
        for end_time in range(int(history_start_time_), int(history_end_time), one_day * slide_step * 1000):
            end_time /= 1000
            timeseries_config["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
            timeseries_config["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                end_time - one_day * timeseries_config["trend_range_day"]))
            has_fix_time = False
            for fix_segment in fix_segments:
                if (timeseries_config["start_time"] > fix_segment[0] and timeseries_config["start_time"] <
                    fix_segment[1]) or (
                        timeseries_config["end_time"] > fix_segment[0] and timeseries_config["end_time"] <
                        fix_segment[1]):
                    has_fix_time = True
            if has_fix_time:
                continue
            print("回测的时间段：{} {}".format(timeseries_config["start_time"], timeseries_config["end_time"]))
            if data_source == "csv":
                timeseries = read_timeseries(timeseries_path, timeseries_config, str(resample_frequency) + "min")
            elif data_source == "iotdb":
                timeseries_sql = "select re_sample(" + timeseries_name + ", 'every'='60.0m', 'interp'='linear')" + " from root.CNNP." + timeseries_name[
                                                                                                                                         :2] + "." + timeseries_name[
                                                                                                                                                     3:5]
                timeseries_sql = timeseries_sql + " where time < " + timeseries_config["end_time"] + " and time > " + \
                                 timeseries_config["start_time"] + ";"
                timeseries = read_timeseries_iotdb(timeseries_sql, resample_frequency, iotdb_config)
            Dplot = 'yes'
            # Dplot = 'no'
            if timeseries_config["start_time"] == "2015-11-03 07:01:23":
                print(timeseries)
            s_tf = trend_features(timeseries, timeseries_name, trend_config, image_path, Dplot,
                                  timeseries_config["start_time"])
            # print(s_tf)
            # 满足某个特定的征兆，进行特殊的显示
            if (s_tf[4]):
                drop += 1
                for failure_segment in failure_segments:
                    if (timeseries_config["start_time"] > failure_segment[0] and timeseries_config["start_time"] < failure_segment[1]) or (timeseries_config["end_time"] > failure_segment[0] and timeseries_config["end_time"] < failure_segment[1]):
                        right += 1


                print('\033[0;35;46m {}, {} \033[0m'.format(timeseries_config["start_time"], timeseries_config["end_time"]))

            tot += 1

        print("总测试窗口的大小：{}".format(tot))
        print("满足单调缓慢下降次数：{}".format(drop))
        print("正确次数：{}".format(right))
        failure_metric_x.append(watch_day)
        failure_metric_y.append(right/tot)
    print(failure_metric_x)
    print(failure_metric_y)
    plt.plot(failure_metric_x, failure_metric_y)
    plt.show()
    plt.savefig(image_path+"stability.png")

