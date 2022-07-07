import numpy as np
import matplotlib.pyplot as plt


def test_plot():
    # Create some mock data
    labels = ['a', 'b', 'c']
    cor1 = [0.01, 0.0, 0.01]
    cor2 = [0.11, 0.12, 0.02]
    a = [1.03, 1.5, 1.01]
    b = [3.07, 3.5, 3.01]
    x = np.arange(len(labels))  # the label locations
    data1 = np.exp(cor1)
    data2 = np.exp(cor2)
    data3 = np.exp(a)
    data4 = np.exp(b)
    width = 0.3

    fig, ax1 = plt.subplots()
    ax1.bar(labels, data3, width, label='cov1')
    ax1.bar(labels, data4, width, label='cov2', bottom=data3)
    color = 'tab:red'
    ax1.set_xlabel('bars')
    # ax1.set_xtick(x, labels)
    ax1.set_ylabel('exp1', color=color)
    # ax1.plot(t1, data1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.legend()
    # ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    #
    # color = 'tab:blue'
    # ax2.set_ylabel('exp2', color=color)  # we already handled the x-label with ax1
    # # ax2.plot(t2, data2, color=color)
    # ax2.tick_params(axis='y', labelcolor=color)
    #
    # fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()


def read_results(in_file):
    pass


def sort_form_pro():
    pass


def sort_form_silver():
    pass


def draw_chart1(out_file):
    pass


if __name__ == "__main__":
    test_plot()