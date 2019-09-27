import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import yaml
import numpy as np
import math

def read_yaml(filename):
    f = open(filename, "r+")
    data = yaml.load(f, yaml.SafeLoader)
    return data

def make_pdf(index):
    pdf_name = 'tuf' + str(index) + '.pdf'
    pp = PdfPages(pdf_name)
    pp.savefig()
    pp.close()
    plt.clf()

def plot_liner(ax, start_x, end_x, start_y, end_y):
    ax.plot([start_x, end_x], [start_y, end_y], 'k')
    ax.set_ylim(0,)

def plot_step(ax, time, val_ini):
    ax.plot([0, time], [val_ini, val_ini], 'k')
    ax.plot([time, time], [val_ini, -1], 'k')
    ax.set_ylim(0,)

def plot_exp(ax, val_ini, coef):
    x = np.arange(0, 10, 0.1)
    y = val_ini * math.e ** (coef * x)
    ax.plot(x, y, 'k')
    ax.set_ylim(0,val_ini+2)

def data_plot(data):
    for i, flow in enumerate(data):
        fig = plt.figure()
        ax = fig.add_subplot(111, xmargin=0)

        val_ini = flow['val_ini']
        start_x = 0
        start_y = val_ini
        end_x = 0
        end_y = val_ini

        for tuf in flow['tuf']:
            time = tuf[0]
            shape = tuf[1]
            coef = tuf[2]
            if shape == 'liner':
                end_x = time
                end_y = end_y + coef * (time - start_x)
                plot_liner(ax, start_x, end_x, start_y, end_y)
                start_x = end_x
                start_y = end_y
            elif shape == 'step':
                plot_step(ax, time, val_ini)
            elif shape == 'exp':
                plot_exp(ax, val_ini, coef)
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')

        make_pdf(i)

if __name__ == '__main__':
    data = read_yaml('flow.yml')
    data_plot(data)
