import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def plot(flow_num, open_time, close_time):
    plt.broken_barh([(open_time, close_time - open_time)], (high*(flow_num*2+1), high))

data = open("result.txt", "r")
flag = False
i = -1 # flow index
high = 14

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
            plot(i, int(open_time), int(close_time))
            print(open_time)
        else:
            print("end")
            break

#high = 100 / ((i+1) * 2 + 1)
plt.axis([0, 120, 0, 100])
plt.grid(True)
pp = PdfPages("test.pdf")
pp.savefig()
pp.close()