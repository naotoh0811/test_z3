import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import yaml

def plot(flow_num, open_time, close_time, hight):
    plt.broken_barh([(open_time, close_time - open_time)], (hight*(flow_num*2+1), hight))

def read_and_plot(filename):
    f = open(filename, "r+")
    num_flow = 3 # the number of flow
    hight = 100 / (num_flow * 2 + 1)
    schedule_time = 120

    data = yaml.load(f, yaml.SafeLoader)
    for num, flow in enumerate(data.values()):
        plt.text(0.2, hight*num, flow.keys(), size = 10, color = "blue")
        for i_time in flow['time']:
            plot(num, i_time[0], i_time[1], hight)

    plt.axis([0, schedule_time, 0, 100])
    plt.grid(axis="x")
    plt.xlabel("Time", fontsize=18)
    plt.tick_params(labelleft=False, left=False, labelsize=18)
    plt.tight_layout()
    pp = PdfPages("test.pdf")
    pp.savefig()
    pp.close()
    plt.clf()

read_and_plot("schedule.yml")