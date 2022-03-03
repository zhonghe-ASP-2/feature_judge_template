import os

import matplotlib.pyplot as plt

from feature_judge import *
from util import *

alarm_time = 0
def show(ori_func, ft, images, sampling_period = 1):
    global alarm_time
    n = len(ori_func)
    interval = sampling_period / n
    plt.subplot(2, 1, 1)

    len1 = len(np.arange(0, sampling_period, interval))
    len1 = min(len1, n)
    plt.plot(np.arange(0, sampling_period, interval)[0:len1], ori_func[0:len1], 'black')
    plt.xlabel('Time'), plt.ylabel('Amplitude')
    plt.subplot(2,1,2)
    frequency = np.arange(int(n / 2)) / (n * interval)
    nfft = abs(ft[range(int(n / 2))] / n )
    plt.plot(frequency[1:], nfft[1:], 'red')
    if(nfft[1] >= 0.026):
        alarm_time += 1
        print(images)
    plt.xlabel('Freq (Hz)'), plt.ylabel('Amp. Spectrum')
    plt.savefig(images)
    plt.close()

if __name__ == "__main__":
    timeseries_name = "QF_01_1RCP604MP_AVALUE"
    # option: iotdb, csv
    # 推荐使用iotdb, csv是全量读入非常的慢
    data_source = "iotdb"
    iotdb_config = {
        "ip": "10.101.66.13",
        "port": "6667",
        "username": 'root',
        "passwd": 'root'
    }

    config_path = "../config/" + timeseries_name
    image_path = "../images/" + timeseries_name+"/"
    # 创建的图片保存目录
    if not os.path.exists(image_path):
        os.mkdir(image_path)
    timeseries_path = "../data/" + timeseries_name + ".csv"

    trend_config, threshold_config, timeseries_config, resample_frequency = read_config(config_path)

    # 遍历整个时间段，从而获取时间序列的误报率
    one_day = 60*60*24
    slide_step = 1
    tot = 0
    drop = 0
    right = 0
    expect_right_time = 0
    if data_source == "csv":
        history_start_time, history_end_time = get_start_end_time(timeseries_path, data_source, {})
    elif data_source == "iotdb":
        history_start_time, history_end_time = get_start_end_time(timeseries_name, data_source, iotdb_config)
    history_start_time = history_start_time + one_day*timeseries_config["trend_range_day"]*1000

    # 故障时间段
    failure_segments = [['2019-04-20 00:00:00', '2019-06-20 00:00:00'],

                        ]

    # 大修时间段
    fix_segments = [
        ["2014-11-14 00:00:00", "2014-11-18 00:00:00"],
        ["2015-10-15 20:00:45", "2015-12-06 13:28:06"],
        ["2016-06-24 00:00:00", "2016-07-02 00:00:00"],
        ["2016-09-15 00:00:00", "2016-10-15 00:00:00"],
        ["2017-09-10 00:00:00", "2017-10-14 00:00:00"],
        ["2019-03-15 00:00:00", "2019-04-15 00:00:00"],
        ["2020-10-10 00:00:00", "2020-11-14 00:00:00"],
    ]
    # 遍历窗口的终止时间

    # 第一步先做参数估计
    for end_time in range(int(history_start_time), int(history_end_time), one_day*slide_step*1000):
        end_time /= 1000
        timeseries_config["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
        timeseries_config["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time-one_day*timeseries_config["trend_range_day"]))

        has_fix_time = False
        for fix_segment in fix_segments:
            if (timeseries_config["start_time"] > fix_segment[0] and timeseries_config["start_time"] <
                fix_segment[1]) or (
                    timeseries_config["end_time"] > fix_segment[0] and timeseries_config["end_time"] <
                    fix_segment[1]) or (timeseries_config["start_time"] < fix_segment[0] and timeseries_config["end_time"] >
                    fix_segment[1]):
                has_fix_time = True
        if has_fix_time:
            continue
        for failure_segment in failure_segments:
            if (timeseries_config["start_time"] > failure_segment[0] and timeseries_config["start_time"] <
                failure_segment[1]) or (
                    timeseries_config["end_time"] > failure_segment[0] and timeseries_config["end_time"] <
                    failure_segment[1]) or (
                    timeseries_config["start_time"] < failure_segment[0] and timeseries_config["end_time"] >
                    failure_segment[1]):
                expect_right_time += 1

        print("回测的时间段：{} {}".format(timeseries_config["start_time"], timeseries_config["end_time"]))
        if data_source == "csv":
            timeseries = read_timeseries(timeseries_path, timeseries_config, str(resample_frequency) + "min")
        elif data_source == "iotdb":
            timeseries_sql = "select re_sample(" + timeseries_name + ", 'every'='"+str(resample_frequency)+"m', 'interp'='linear')" + " from root.CNNP." + timeseries_name[
                                                                                                                                :2] + "." + timeseries_name[3:5]
            timeseries_sql = timeseries_sql + " where time < " + timeseries_config["end_time"] + " and time > " + \
                             timeseries_config["start_time"] + ";"
            timeseries = read_timeseries_iotdb(timeseries_sql, resample_frequency, iotdb_config)
        Dplot = 'yes'
        # Dplot = 'no'

        timeseries = pd.to_numeric(timeseries)
        if(len(timeseries) < 10):
            continue
        transformed = np.fft.fft(timeseries)
        show(timeseries, transformed, image_path+timeseries_config["start_time"].split(' ')[0]+" "+timeseries_name+'_fft'+".png")
        tot += 1
    print("总测试窗口个数：{}".format(tot))
    print("满足单调缓慢下降次数：{}".format(alarm_time))


    # 做假设检验，回测
    

