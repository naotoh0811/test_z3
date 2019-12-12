import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import yaml
import os.path

home_dir = os.path.expanduser('~')
# ref https://qiita.com/skotaro/items/5c9893d186ccd31f459d
color_list = [
    '#1f77b4', \
    '#ff7f0e', \
    '#2ca02c', \
    '#d62728', \
    '#9467bd', \
    '#8c564b', \
    '#e377c2', \
    '#7f7f7f', \
    '#bcbd22', \
    '#17becf' \
]

def read_yaml(filename):
    f = open(filename, "+r")
    data = yaml.load(f, yaml.SafeLoader)
    return data

def plot_window(ax, i_gate, open_time, close_time, window_hight, color, flow_name):
    ax.broken_barh( \
        [(open_time, close_time - open_time)], \
        (window_hight*(i_gate*2+1), window_hight), \
        facecolors=color, \
        label=flow_name \
    )

def gen_graph_for_each_sw(each_sw):
    name = each_sw["name"]
    cycle = each_sw["cycle"]
    control = each_sw["control"]

    # set font
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 15

    fig, ax = plt.subplots()
    y_size = 100
    window_hight = y_size / (4 * 2 + 1)

    # set lim
    ax.set_xlim(0, cycle)
    ax.set_ylim(0, y_size)

    # set axis
    plt.tick_params(labelleft=False, left=False)
    plt.grid(axis="x")

    # set label
    ax.set_xlabel(u'Time [\u03bcs]')

    # set margin
    mpl.rcParams['axes.xmargin'] = 0
    mpl.rcParams['axes.ymargin'] = 0

    # plot for each gate
    for i_gate, each_control in enumerate(control):
        nextNode = each_control["nextNode"]
        open_close = each_control["open_close"]

        # add text on left-outside
        ax.text(-0.1, (1/9)*(1.5+2*i_gate), 'to {}'.format(nextNode), transform=ax.transAxes)

        for each_time in open_close:
            open_time = each_time[0]
            close_time = each_time[1]
            flow_id = each_time[2]
            color = color_list[flow_id]
            flow_name = 'flow{}'.format(flow_id)
            plot_window(ax, i_gate, open_time, close_time, window_hight, color, flow_name)

    # set legend
    handler_list, label_list = ax.get_legend_handles_labels()
    ## remove duplicate
    handler_list_forLegend = []
    label_list_forLegend = []
    for (each_handler, each_label) in zip(handler_list, label_list):
        if not each_label in label_list_forLegend:
            handler_list_forLegend.append(each_handler)
            label_list_forLegend.append(each_label)
    ax.legend(handler_list_forLegend, label_list_forLegend)

    plt.tight_layout()
    pdf_filename = 'window_sw{}.pdf'.format(name)
    make_pdf(pdf_filename)

def make_pdf(pdf_filename):
    pp = PdfPages(pdf_filename)
    pp.savefig()
    pp.close()
    # plt.clf()
    plt.close()

def main():
    gcl_yaml_filename = home_dir + '/workspace/test_z3/multiSw_sch/gcl_sw.yml'
    gcl_sw = read_yaml(gcl_yaml_filename)

    for each_sw in gcl_sw:
        gen_graph_for_each_sw(each_sw)