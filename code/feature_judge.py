# python 3.9 (>=3.7)
# encoding=UTF-8
# author: xyb
#---------------------------------------------------------------
# 功能：进行趋势离散分析
#

import sys
import os
import json
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller as ADF
from util import *
from changepy import pelt
from changepy.costs import normal_mean
import jenkspy

# 认为一分钟内被分割的点都是在同一段变化的区间
window_size = 60

def sign(value, pre):
    if value > 0:
        return 1
    elif value == 0:
        return pre
    else:
        return 0

def sign1(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0

def timeseries_represent(timeseries):
    diff1 = []
    diff2 = []
    for _, timeseries_value_ in enumerate(timeseries):
        if _ == 0:
            continue
        diff2.append(sign1(timeseries[_] - timeseries[_ - 1]))
        pre = sum(diff2[max(0, _-window_size): _-1])
        if pre > 0:
            pre = 1
        else:
            pre = 0
        diff1.append(sign(timeseries[_]-timeseries[_-1], pre))

    return diff1

def z_judge(timeseries):
    timeseries = timeseries_represent(timeseries)
    flag = 0
    for i in range(len(timeseries)):
        if flag == 0 and timeseries[i] == 0:
            flag = 2
        if flag == 2 and timeseries[i] == 1:
            return False
    if flag == 2:
        return True
    else:
        return False

def inverse_z_judge(timeseries):
    timeseries = timeseries_represent(timeseries)
    flag = 0
    for i in range(len(timeseries)):
        if flag == 0 and timeseries[i] == 1:
            flag = 1
        if flag == 1 and timeseries[i] == 0:
            return False
    if flag == 1:
        return True
    else:
        return False

def judge_monotonicity(timeseries):
    monotonicity_rise = True
    monotonicity_drop = True
    for i in range(1, len(timeseries)):
        if timeseries[i]+0.001 < timeseries[i-1]:
            monotonicity_rise = False
        if timeseries[i] > timeseries[i-1]+0.001:
            monotonicity_drop = False

    if monotonicity_drop:
        return 1
    if monotonicity_rise:
        return 0
    return -1




def trend_features(df_analyze, valuename, trend_features_inputdata, DPlot_dir, Dplot, start_time):
    # 判断准则 ： trend_features_inputdata
    # 时序序列 ： df_analyze
    # 时序序列在iotdb中的路径名：valuename
    # 调试输出路径：DPlot_dir
    # 调试输出判断：Dplot
    print('==>>>数据测点：%s' % (valuename))

    resample_method = trend_features_inputdata["resample_method"]
    trend_range_day = trend_features_inputdata["trend_range_day"]
    resample_fre = trend_features_inputdata["resample_fre"]
    vibrate_window = trend_features_inputdata["vibrate_window"]
    monotonicity_window = trend_features_inputdata["monotonicity_window"]
    z_window = trend_features_inputdata["z_window"]
    slope_method = trend_features_inputdata["slope_method"]
    segment_method = trend_features_inputdata["segment_method"]
    classification_number = trend_features_inputdata["classification_number"]

    threshold_range_day = trend_features_inputdata["threshold_range_day"]
    ADF_pvalue = trend_features_inputdata["ADF_pvalue"]

    S04_std = trend_features_inputdata['S04_std'] # type：float; 判断是否稳定不变时用到得方差上限

    S12_std = trend_features_inputdata['S12_std'] # type：float;

    S01_rise_range = trend_features_inputdata['S01_rise_range']
    S02_rise_range = trend_features_inputdata['S02_rise_range']
    S03_rise_range = trend_features_inputdata['S03_rise_range']

    S05_drop_range = trend_features_inputdata['S05_drop_range']
    S06_drop_range = trend_features_inputdata['S06_drop_range']
    S07_drop_range = trend_features_inputdata['S07_drop_range']

    S10_window_size = trend_features_inputdata['S10_window_size']
    S11_window_size = trend_features_inputdata['S11_window_size']

    ts_numeric = pd.to_numeric(df_analyze)
    print('==>>>用于趋势判断的时序数据：')
    if Dplot == 'yes':
        timeseries_plot(ts_numeric, 'g', start_time.split(' ')[0]+" "+valuename+'_oir'+"", pathsave=DPlot_dir)
    Dplot = 'no'
    trend_feature_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    ADF_pvalue_tf = 'unknown'
    print('序列的平稳性检验(ADF检验结)果为：')
    if len(ts_numeric) > 2:
        test_result = ADF(ts_numeric.dropna(inplace = False))
        p_value = test_result[1]
        print('p-value:', p_value)
        if p_value >= ADF_pvalue:
            print('--原始序列是非平稳序列')
            ADF_pvalue_tf = 'unstationary'
        else:
            print('--原始序列是平稳序列')
            ADF_pvalue_tf = 'stationary'
    if ADF_pvalue_tf == 'stationary':
        print('标准差判断：')
        # std_value = np.std(ts_numeric, ddof=1)
        ts_numeric_frame = pd.DataFrame(ts_numeric)
        mad_value = ts_numeric_frame.mad().get(0)
        if mad_value >= S04_std:
            # print('--标准差：s,大于下限：{:.8%}'.format(S04_S04_std_lower))
            print('--标准差：%f,大于下限：%f' % (mad_value, S04_std))
        if mad_value < S04_std:
            print('--标准差：%f,小于下限：%f' % (mad_value, S04_std))
            print('--原始序列是平稳不变序列')
            trend_feature_vector[4 - 1] = 1  # 失效特征趋势：平稳不变 ,s_04=1
        if sum(trend_feature_vector) == 0 and mad_value < S12_std:
            print('--标准差：%f,小于下限：%f' % (mad_value, S12_std))
            print('--原始序列是平稳不变序列')
            trend_feature_vector[12 - 1] = 1  # 失效特征趋势：平稳震荡的 ,s_04=1

    print("aotu judge: ", sum(trend_feature_vector))
    if sum(trend_feature_vector)  == 0:
        ts_numeric_z = ts_numeric.rolling(window=int(z_window)).median()
        ts_numeric_z = ts_numeric_z.dropna(inplace=False)

        timeseries_plot(ts_numeric_z, 'g', valuename + '_aotu',
                                           pathsave=DPlot_dir)
        if z_judge(ts_numeric_z):
            trend_feature_vector[9 - 1] = 1
            print("该时间序列为凸形，先增后降")
        elif inverse_z_judge(ts_numeric_z):
            trend_feature_vector[8 - 1] = 1
            print("该时间序列为凹形，先降后增")

    if True or sum(trend_feature_vector) == 0:
        ts_numeric_vibrate = ts_numeric.rolling(window=int(vibrate_window)).median()
        ts_numeric_vibrate = ts_numeric_vibrate.dropna(inplace=False)
        if Dplot == 'yes': timeseries_plot(ts_numeric_vibrate, 'g', valuename + '_vibrate', pathsave=DPlot_dir)
        vibrate_flag = judge_monotonicity(ts_numeric_vibrate)
        if vibrate_flag == 1:
            trend_feature_vector[11-1] = 1
        elif vibrate_flag == 0:
            trend_feature_vector[10-1] = 1

    if True or sum(trend_feature_vector) == 0:
        ts_numeric_monotonicity = ts_numeric
        ts_numeric_monotonicity = ts_numeric.rolling(window=int(monotonicity_window)).median()
        ts_numeric_monotonicity = ts_numeric_monotonicity.dropna(inplace=False)
        if Dplot == 'yes': timeseries_plot(ts_numeric_monotonicity, 'g', valuename + '_monotonicity', pathsave=DPlot_dir)
        monotonicity_flag = judge_monotonicity(ts_numeric_monotonicity)
        change_ratio = 0
        drop_slope = [-1]
        rise_slope = [-1]
        if slope_method == "ratio_count":
            change_ratio = abs(ts_numeric_monotonicity[0]-ts_numeric_monotonicity[-1])/ts_numeric_monotonicity[0]
        elif slope_method == "slope":
            if segment_method == "jenkspy":
                y = np.array(list(ts_numeric_monotonicity.values))
                # 返回的是分段的具体的值
                print("分段段数：{}".format(min(classification_number, len(y)-1)))
                if len(y) > 2:

                    breaks = jenkspy.jenks_breaks(y, nb_class = min(classification_number, 2))
                    print(breaks)
                    # if abs(breaks[0] -ts_numeric_monotonicity[0]) > 0.1 and :
                    #     breaks.append(ts_numeric_monotonicity.values[0])
                    # if abs(breaks[-1] -ts_numeric_monotonicity[-1]) > 0.1:
                    #     breaks.append(ts_numeric_monotonicity.values[-1])
                    breaks_jkp = []
                    print(breaks)
                    for v in breaks:
                        idx = ts_numeric_monotonicity.index[ts_numeric_monotonicity == v][-1]
                        breaks_jkp.append(idx)
                    Dplot = 'yes'
                    if Dplot == 'yes':
                        timeseries_segment_plot(ts_numeric_monotonicity, breaks_jkp, start_time.split(' ')[0]+" "+valuename + '_segment', pathsave=DPlot_dir)
                    Dplot = 'no'

                    temp = breaks_jkp.copy()
                    break_index = [-1 for i in range(len(breaks_jkp))]
                    breaks_jkp.sort()
                    for i in range(len(breaks_jkp)):
                        break_index[temp.index(breaks_jkp[i])] = i
                    breaks_copy = breaks
                    breaks = []
                    for i in range(len(breaks_copy)):
                        if i in break_index:
                            breaks.append(breaks_copy[break_index.index(i)])

                    print(breaks)
                    print(breaks_jkp)
                    for i in range(1, len(breaks)):
                        if breaks[i] > breaks[i-1]:
                            # 目前的时间单位为小时，不知道以后是否需要变成可配置项
                            slope = abs((breaks[i]-breaks[i-1])/((breaks_jkp[i]-breaks_jkp[i-1]).days*24+(breaks_jkp[i]-breaks_jkp[i-1]).seconds/60/60))
                            rise_slope.append(slope)
                        elif breaks[i-1] > breaks[i]:
                            slope = abs((breaks[i-1] - breaks[i]) / ((breaks_jkp[i] - breaks_jkp[i-1]).days * 24 + (
                                        breaks_jkp[i] - breaks_jkp[i-1]).seconds / 60 / 60))
                            drop_slope.append(slope)

        rise_slope_max = max(rise_slope)

        drop_slope_max = max(drop_slope)
        print("上升斜率队列：", rise_slope)
        print("下降斜率队列：", drop_slope)
        if drop_slope_max >= S07_drop_range:
            trend_feature_vector[7-1] = 1
        elif drop_slope_max >= S06_drop_range:
            trend_feature_vector[6-1] = 1
        elif drop_slope_max >= S05_drop_range:
            trend_feature_vector[5-1] = 1
        # 单调上升，进一步进行细分
        if rise_slope_max >= S01_rise_range:
            trend_feature_vector[1-1] = 1
        elif rise_slope_max >= S02_rise_range:
            trend_feature_vector[2-1] = 1
        elif rise_slope_max >= S03_rise_range:
            trend_feature_vector[3-1] = 1



    print(trend_feature_vector)
    if trend_feature_vector[0] == 1:
        print("满足单调急剧上升")
    if trend_feature_vector[1] == 1:
        print("满足单调上升")
    if trend_feature_vector[2] == 1:
        print("满足单调缓慢上升")
    if trend_feature_vector[3] == 1:
        print("满足平稳不变")
    if trend_feature_vector[4] == 1:
        print("满足单调缓慢下降")
    if trend_feature_vector[5] == 1:
        print("满足单调下降")
    if trend_feature_vector[6] == 1:
        print("满足单调急剧下降")
    if trend_feature_vector[7] == 1:
        print("满足下降后上升")
    if trend_feature_vector[8] == 1:
        print("满足上升后下降")
    if trend_feature_vector[9] == 1:
        print("满足波动上升")
    if trend_feature_vector[10] == 1:
        print("满足波动下降")
    if trend_feature_vector[11] == 1:
        print("满足平稳震荡")
    return trend_feature_vector


def threshold_features(df_analyze,valuename,threshold_features_inputdata,DPlot_dir,Dplot):
    # 判断准则 ： threshold_features_inputdata
    # 时序序列 ： df_analyze
    # 时序序列在iotdb中的路径名：valuename
    # 调试输出路径：DPlot_dir
    # 调试输出判断：Dplot

    print('==>>>数据测点：%s'%(valuename))
    T03_range = threshold_features_inputdata['T03_range']   #高高高
    T02_range = threshold_features_inputdata['T02_range']   # 高高
    T01_range = threshold_features_inputdata['T01_range']   # 高
    T04_range = threshold_features_inputdata['T04_range']   #低
    T05_range = threshold_features_inputdata['T05_range']   #低低
    T06_range = threshold_features_inputdata['T06_range']   #低低低

    # 若不落在以上区域中，均为正常
    T_used    = threshold_features_inputdata['T_used']

    t_tf = [0, 0, 0, 0, 0, 0]

    ts_numeric = pd.to_numeric(df_analyze)
    print('==>>>用于阈值判断的时序数据：')
    tsinfo = ts_info(ts_numeric)
    # 阈值判断区间是否合理
    ranking=[]
    if not T_used[3-1] == 0:
        ranking.append(T03_range[1])
        ranking.append(T03_range[0])
    if not T_used[2-1] == 0:
        ranking.append(T02_range[1])
        ranking.append(T02_range[0])
    if not T_used[1-1] == 0:
        ranking.append(T01_range[1])
        ranking.append(T01_range[0])
    if not T_used[4-1] == 0:
        ranking.append(T04_range[1])
        ranking.append(T04_range[0])
    if not T_used[5-1] == 0:
        ranking.append(T05_range[1])
        ranking.append(T05_range[0])
    if not T_used[6-1] == 0:
        ranking.append(T06_range[1])
        ranking.append(T06_range[0])

    for i in range(np.size(ranking)-1):
        if ranking[i] < ranking[i+1]:
            print('Error：检查各失效阈值的判定区间是否满足规律要求！（T3>T2>T1>T4>T5>T6）')
            os._exit()
    mean_value = np.mean(df_analyze)

    if not T_used[3-1] == 0:
        if mean_value >= T03_range[0] and mean_value <= T03_range[1]:
            t_tf[3-1]=1
    if not T_used[2-1] == 0:
        if mean_value >= T02_range[0] and mean_value <= T02_range[1]:
            t_tf[2-1]=1
    if not T_used[1-1] == 0:
        if mean_value >= T01_range[0] and mean_value <= T01_range[1]:
            t_tf[1-1]=1
    if not T_used[4-1] == 0:
        if mean_value >= T04_range[0] and mean_value <= T04_range[1]:
            t_tf[4-1]=1
    if not T_used[5-1] == 0:
        if mean_value >= T05_range[0] and mean_value <= T05_range[1]:
            t_tf[5-1]=1
    if not T_used[6-1] == 0:
        if mean_value >= T06_range[0] and mean_value <= T06_range[1]:
            t_tf[6-1]=1
    print('阈值征兆向量:', t_tf)
    return t_tf


def threshold_features(df_analyze,valuename,threshold_features_inputdata,DPlot_dir,Dplot):
    # 判断准则 ： threshold_features_inputdata
    # 时序序列 ： df_analyze
    # 时序序列在iotdb中的路径名：valuename
    # 调试输出路径：DPlot_dir
    # 调试输出判断：Dplot

    print('==>>>数据测点：%s'%(valuename))
    T03_range = threshold_features_inputdata['T03_range']   #高高高
    T02_range = threshold_features_inputdata['T02_range']   # 高高
    T01_range = threshold_features_inputdata['T01_range']   # 高
    T04_range = threshold_features_inputdata['T04_range']   #低
    T05_range = threshold_features_inputdata['T05_range']   #低低
    T06_range = threshold_features_inputdata['T06_range']   #低低低

    # 若不落在以上区域中，均为正常
    T_used    = threshold_features_inputdata['T_used']

    t_tf = [0, 0, 0, 0, 0, 0]

    ts_numeric = pd.to_numeric(df_analyze)
    print('==>>>用于阈值判断的时序数据：')
    tsinfo = ts_info(ts_numeric)
    # 阈值判断区间是否合理
    ranking=[]
    if not T_used[3-1] == 0:
        ranking.append(T03_range[1])
        ranking.append(T03_range[0])
    if not T_used[2-1] == 0:
        ranking.append(T02_range[1])
        ranking.append(T02_range[0])
    if not T_used[1-1] == 0:
        ranking.append(T01_range[1])
        ranking.append(T01_range[0])
    if not T_used[4-1] == 0:
        ranking.append(T04_range[1])
        ranking.append(T04_range[0])
    if not T_used[5-1] == 0:
        ranking.append(T05_range[1])
        ranking.append(T05_range[0])
    if not T_used[6-1] == 0:
        ranking.append(T06_range[1])
        ranking.append(T06_range[0])

    for i in range(np.size(ranking)-1):
        if ranking[i] < ranking[i+1]:
            print('Error：检查各失效阈值的判定区间是否满足规律要求！（T3>T2>T1>T4>T5>T6）')
            os._exit()
    mean_value = np.mean(df_analyze)
    print(mean_value)
    if not T_used[3-1] == 0:
        if mean_value >= T03_range[0] and mean_value <= T03_range[1]:
            t_tf[3-1]=1
    if not T_used[2-1] == 0:
        if mean_value >= T02_range[0] and mean_value <= T02_range[1]:
            t_tf[2-1]=1
    if not T_used[1-1] == 0:
        if mean_value >= T01_range[0] and mean_value <= T01_range[1]:
            t_tf[1-1]=1
    if not T_used[4-1] == 0:
        if mean_value >= T04_range[0] and mean_value <= T04_range[1]:
            t_tf[4-1]=1
    if not T_used[5-1] == 0:
        if mean_value >= T05_range[0] and mean_value <= T05_range[1]:
            t_tf[5-1]=1
    if not T_used[6-1] == 0:
        if mean_value >= T06_range[0] and mean_value <= T06_range[1]:
            t_tf[6-1]=1
    print('阈值征兆向量:', t_tf)
    return t_tf


if __name__ == '__main__':
    jsonfile ={
        'rolmean_window4vibrate': 20,   # type：int; 降噪平均的滑窗窗口长度,不能超过数据个数，用于判断震动，建议给的小一些
        'rolmean_window4monotonicity':50,  # type：int; 降噪平均的滑窗窗口长度,不能超过数据个数，用于判断单调性，可适当稍大
        'monotonicity_peakvalleys':20,  # type：int; 单调性加窗滤波后，单调性序列允许的最大波峰波谷数（该值取1，表示严格单调）
        'ADF_pvalue':0.05,          # type：float;ADF 检验时的p-value

        'S04': {'std_lower':0.10},    # type：float; 判断是否稳定不变时用到得方差上限
        'S12': {'vibrate_range': 0.05,'vibrate_rate': 0.05},  # type：float; 判定为震荡时用到得四分位距下限（四分位距相对于均值的百分比）
                                                              # type：float; 振荡条件时，波峰波谷数目占总数据点数的比例（滤去小波后）

        'S11': {'drop_range': 0.01, 'vibrate_rate': 0.09},   # type：float; 波动下降时，下降幅度（起点减终点绝对值）占起点绝对值的比例应大于这个数
                                                             # type：float; 波动下降时，波峰波谷数目占总数据点数的比例（滤去小波后）
        'S10': {'rise_range': 0.01, 'vibrate_rate': 0.05},   # type：float; 波动上升时，下降幅度（起点减终点绝对值）占起点绝对值的比例应大于这个数
                                                             # type：float; 波动上升时，波峰波谷数目占总数据点数的比例（滤去小波后）
        'S01': {'rise_range': 0.05},   # type：float; 单调快速上升时，上升幅度（起点减终点绝对值）占起点绝对值的比例应大于这个数
        'S02': {},
        'S03': {'rise_range': 0.01},   # type：float; 单调缓慢上升时，上升幅度（起点减终点绝对值）占起点绝对值的比例应小于这个数

        'S05': {'drop_range': 0.04},   # type：float; 单调快速下降时，下降幅度（起点减终点绝对值）占起点绝对值的比例应大于这个
        'S06': {},
        'S07': {'drop_range': 0.05},   # type：float; 单调缓慢下降时，下降幅度（起点减终点绝对值）占起点绝对值的比例应小于这个

        'S08': {'range': [0.01, 0.99]},  # type:floatlist; 单凸峰值所处的相对位置
        'S09': {'range': [0.01, 0.99]},  # type:floatlist; 单凹峰值所处的相对位置
    }

    with open("trend.json", "w") as f:
        json.dump(jsonfile, f)
        print("加载入文件完成...")

    # jsonfile = { # for FQ1RCP604MP
    #     'T03': {'lower': 10000001, 'upper': 10000002, },  # type：float; 高高高，上限建议给默认的极大值
    #     'T02': {'lower': 10000000, 'upper': 10000001, },       # type：float; 高高
    #     'T01': {'lower': 100, 'upper': 10000000, },       # type：float; 高
    #     'T04': {'lower': -1000001, 'upper':-1000000, },       # type：float; 低
    #     'T05': {'lower': -1000003, 'upper': -1000002, },       # type：float; 低低
    #     'T06': {'lower': -1000005, 'upper': -1000004, }, # type：float; 低低低，下限建议给默认的极小值
    #     'T_used':[1,1,1,1,1,1]   # type：int; 使用到的征兆通道给非零值
    # }

    jsonfile = {  # for 1APA136MT_1
        'T03': {'lower': 1000003, 'upper': 1000004, },  # type：float; 高高高，上限建议给默认的极大值
        'T02': {'lower': 1000001, 'upper': 1000002, },  # type：float; 高高
        'T01': {'lower': 100, 'upper': 1000000, },  # type：float; 高
        'T04': {'lower': 4.7, 'upper': 5, },  # type：float; 低
        'T05': {'lower': 4.5, 'upper': 4.7, },  # type：float; 低低
        'T06': {'lower': -1000005, 'upper': 4.5, },  # type：float; 低低低，下限建议给默认的极小值
        'T_used': [1, 0, 0, 0, 0, 0]  # type：int; 使用到的征兆通道给非零值
    }

    with open("threshold.json", "w") as f:
        json.dump(jsonfile, f)
        print("加载入文件完成...")