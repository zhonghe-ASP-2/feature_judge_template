import pickle
import matplotlib.pyplot as plt
from functools import reduce

if __name__ == "__main__":
    with open('./results_QF_02_804.pickle', 'rb') as file:  # 用with的优点是可以不用写关闭文件操作
        time_segment = pickle.load(file)
        independent_events_a_possibility = pickle.load(file)
        results = pickle.load(file)
        independent_events = pickle.load(file)

    temp = [reduce(lambda x, y: x*y, results[i][0:1]) for i in range(len(results))]
    # temp = [(results[i][0]) for i in range(len(results))]
    # temp = [independent_events_a_possibility[i] for i in range(len(results))]
    # plt.plot(time_segment, indepen)
    # plt.plot(time_segment, [results[i][1] for i in range(len(results))])
    print(len(temp))
    print([temp[i] for i in range(len(temp)) if temp[i]>0.9])
    print([i for i in range(len(temp)) if temp[i] > 0.9])
    print(len([temp[i] for i in range(len(temp)) if temp[i] > 0.9]))
    plt.plot(time_segment, temp)
    plt.show()