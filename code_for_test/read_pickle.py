import pickle
import matplotlib.pyplot as plt

if __name__ == "__main__":
    with open('results.pickle', 'rb') as file:  # 用with的优点是可以不用写关闭文件操作
        time_segment = pickle.load(file)
        independent_events_a_possibility = pickle.load(file)
        results = pickle.load(file)
        independent_events = pickle.load(file)
    plt.plot(time_segment, independent_events_a_possibility)
    plt.show()