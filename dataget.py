import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import yaml

def plot(flow_num, open_time, close_time, hight):
    plt.broken_barh([(open_time, close_time - open_time)], (hight*(flow_num*2+1), hight))

def read_and_plot(filename):
    # read yaml
    f = open(filename, "r+")
    data = yaml.load(f, yaml.SafeLoader)

    # variables set
    num_flow = data['num_flow']
    y_size = 100
    hight = y_size / (num_flow * 2 + 1)
    schedule_cycle = data['schedule_cycle']

    # plot
    for num, flow in enumerate(data['flow']):
        plt.text(-15, hight*(1.5+num*2), flow['name'], size = 16)
        for i_time in flow['time']:
            plot(num, i_time[0], i_time[1], hight)

    plt.axis([0, schedule_cycle, 0, y_size])
    plt.grid(axis="x")
    plt.xlabel("Time", fontsize=18)
    plt.tick_params(labelleft=False, left=False, labelsize=18)
    plt.tight_layout()
    pp = PdfPages("window.pdf")
    pp.savefig()
    pp.close()
    plt.clf()

read_and_plot("schedule.yml")