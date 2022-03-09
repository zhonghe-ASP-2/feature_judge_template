import os

import matplotlib.pyplot as plt
import numpy as np

from feature_judge import *
from util import *
from scipy import stats
import pickle
from functools import reduce


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
    timeseries_name = "FQ_01_1RCP604MP_AVALUE"
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

    hz = 10

    if data_source == "csv":
        history_start_time, history_end_time = get_start_end_time(timeseries_path, data_source, {})
    elif data_source == "iotdb":
        history_start_time, history_end_time = get_start_end_time(timeseries_name, data_source, iotdb_config)
    history_start_time = history_start_time + one_day*timeseries_config["trend_range_day"]*1000

    # 故障时间段
    failure_segments = [
                        ]

    # 大修时间段
    fix_segments = [
        ["2015-09-17 22:26:40", "2015-12-20 16:26:40"],
        ["2017-01-10 06:13:20", "2017-02-23 05:46:40"],
        ["2018-01-27 04:53:20", "2018-03-20 06:53:20"],
        ["2019-09-28 00:00:00", "2019-11-05 04:40:00"],
        ["2021-03-20 08:26:40", "2021-04-19 10:40:00"]
    ]
    # 遍历窗口的终止时间

    # 第一步先做参数估计
    samples = []
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
        has_failure_time = False
        for failure_segment in failure_segments:
            if (timeseries_config["start_time"] > failure_segment[0] and timeseries_config["start_time"] <
                failure_segment[1]) or (
                    timeseries_config["end_time"] > failure_segment[0] and timeseries_config["end_time"] <
                    failure_segment[1]) or (
                    timeseries_config["start_time"] < failure_segment[0] and timeseries_config["end_time"] >
                    failure_segment[1]):
                expect_right_time += 1
                has_failure_time = True
        if has_failure_time:
            continue

        print("回测的时间段：{} {}".format(timeseries_config["start_time"], timeseries_config["end_time"]))
        if data_source == "csv":
            timeseries = read_timeseries(timeseries_path, timeseries_config, str(resample_frequency) + "min")
        elif data_source == "iotdb":
            timeseries_sql = "select re_sample(" + timeseries_name + ", 'every'='"+str(resample_frequency)+"m', 'interp'='linear')" + " from root.CNNP." + timeseries_name[
                                                                                                                                :2] + "." + timeseries_name[3:5]
            print(timeseries_sql)
            # timeseries_sql = "select " + timeseries_name + " from root.CNNP." + timeseries_name[
            #                                                                           :2] + "." + timeseries_name[3:5]
            timeseries_sql = timeseries_sql + " where time < " + timeseries_config["end_time"] + " and time > " + \
                             timeseries_config["start_time"] + " and "+timeseries_name+" > 0 ;"
            timeseries = read_timeseries_iotdb(timeseries_sql, resample_frequency, iotdb_config)
        Dplot = 'yes'
        # Dplot = 'no'

        timeseries = pd.to_numeric(timeseries)
        print(len(timeseries))
        if(len(timeseries) < 10):
            continue
        transformed = np.fft.fft(timeseries)
        n = len(timeseries)
        nfft = abs(transformed[range(int(n / 2))] / n)
        hz = min(hz, int(n/2)-1)
        samples.append(abs(nfft[:hz+1]))
        tot += 1
    print("总测试窗口个数：{}".format(tot))
    print("满足单调缓慢下降次数：{}".format(alarm_time))
    if hz < 10:
        print("有时候采样率不够，之后的推理没有到10HZ")
    mean = [-1, ]
    std = [-1, ]

    for i in range(1, hz+1, 1):
        temp = np.array([samples[j-1][i] for j in range(len(samples))])
        mean.append(temp.mean())
        std.append(temp.std(ddof=1))


    print(mean)
    print(std)


    # 回测，将失效时间段加回来
    samples = []
    time_segment = []
    results = []

    independent_events = []
    independent_events_a_possibility = []
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
            # timeseries_sql = "select " + timeseries_name + " from root.CNNP." + timeseries_name[
            #                                                                           :2] + "." + timeseries_name[3:5]
            timeseries_sql = timeseries_sql + " where time < " + timeseries_config["end_time"] + " and time > " + \
                             timeseries_config["start_time"] + " and "+timeseries_name+" > 0 ;"
            timeseries = read_timeseries_iotdb(timeseries_sql, resample_frequency, iotdb_config)

        timeseries = pd.to_numeric(timeseries)
        if(len(timeseries) < 10):
            continue
        transformed = np.fft.fft(timeseries)

        # 进行采样的窗口大小
        if len(samples) > 3:
            del samples[0]

        n = len(timeseries)
        nfft = abs(transformed[range(int(n / 2))] / n)
        samples.append(abs(nfft[:hz + 1]))

        show(timeseries, transformed, image_path+timeseries_config["start_time"].split(' ')[0]+" "+timeseries_name+'_fft'+".png")
        result_single = []
        independent_result = []
        # 先对列
        for i in range(1, len(samples[0])):
            mean_single = np.array([samples[j][i] for j in range(len(samples))])
            mean_single = mean_single.mean()
            std_single = np.array([samples[j][i] for j in range(len(samples))])
            std_single = std_single.std(ddof=1)

            # 需要二分进行优化
            confidence_answer = 1
            for confidence in np.arange(0.01, 1.01, 0.01):
                conf_interval = stats.norm.interval(confidence, loc=mean[i], scale=std[i])
                if conf_interval[0] < mean_single and conf_interval[1] > mean_single:
                    confidence_answer = confidence
                    break
            result_single.append(confidence_answer)

            confidence_answer = 1
            for confidence in np.arange(0.01, 1.01, 0.01):
                conf_interval = stats.norm.interval(confidence, loc=mean[i], scale=std[i])
                if conf_interval[0] < samples[-1][i] and conf_interval[1] > samples[-1][i]:
                    confidence_answer = confidence
                    break
            independent_result.append(confidence_answer)

        # 1、2、3hz连乘
        independent_events_a_possibility.append(reduce(lambda x, y: x*y, independent_result[0:3]))
        # 保存结果
        results.append(result_single)
        independent_events.append(independent_result)

        time_segment.append(timeseries_config["start_time"])

    print(time_segment)
    print(independent_events_a_possibility)
    print(results)
    print(independent_events)

    file = open('results_FQ_01_604.pickle', 'wb')
    pickle.dump(time_segment, file)
    pickle.dump(independent_events_a_possibility, file)
    pickle.dump(results, file)
    pickle.dump(independent_events, file)
    file.close()

