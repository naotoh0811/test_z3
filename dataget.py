import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def plot(flow_num, open_time, close_time, hight):
    plt.broken_barh([(open_time, close_time - open_time)], (hight*(flow_num*2+1), hight))

def read_and_plot(filename):
    data = open(filename, "r")
    flag = False
    i = -1 # flow index
    num_flow = 3 # the number of flow
    hight = 100 / (num_flow * 2 + 1)
    schedule_time = 120

    for line in data:
        if line[:1] == "#":
            cycle_time = line.split(":")[1].rstrip('\n')
            print(cycle_time)
            flag = True
            i += 1
            continue
        if flag:
            if line != "\n":
                open_time = line.split(",")[0]
                close_time = line.split(",")[1].rstrip('\n')
                plot(i, int(open_time), int(close_time), hight)
                print(open_time)
            else:
                print("end")
                break

    plt.axis([0, schedule_time, 0, 100])
    plt.grid(axis="x")
    plt.xlabel("Time", fontsize=18)
    plt.tick_params(labelleft=False, left=False, labelsize=18)
    plt.tight_layout()
    pp = PdfPages("test.pdf")
    pp.savefig()
    pp.close()
    plt.clf()

read_and_plot("result.txt")
