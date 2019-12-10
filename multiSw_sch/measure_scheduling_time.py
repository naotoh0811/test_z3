import os.path
import sys
import pprint
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import multiSw_sch.gen_netwrok_and_flow as gen_netwrok_and_flow
import multiSw_sch.sch_with_soft as sch_with_soft

NOT_DEFINE = 1000
UNSAT = -2
SAT = -1

REPEAT = 30


def gen_result_list():
    result_list = []
    # for num_sw in range(2, 11): # 2 -- 10
    # for num_sw in range(2, 21):
    for num_sw in range(10, 11):
        print("now num_sw = {}".format(num_sw))
        num_flow = num_sw
        for num_flow_soft in range(num_flow + 1): # 0 -- num_flow
        # for num_flow_soft in range(math.ceil(num_flow/2), math.ceil(num_flow/2) + 1):
            sat_cnt = 0
            elapsed_time_list = []
            for i in range(REPEAT):
                gen_netwrok_and_flow.main(num_sw, num_flow, num_flow_soft)
                i_last_flow, elapsed_time = sch_with_soft.main()
                sat_cnt = sat_cnt + 1 if i_last_flow >= SAT else sat_cnt
                elapsed_time_list.append(elapsed_time)

            sat_rate = (sat_cnt / REPEAT) * 100

            result_list.append({
                "num_sw": num_sw, \
                "num_flow": num_flow, \
                "num_flow_hard": num_flow - num_flow_soft, \
                "num_flow_soft": num_flow_soft, \
                "sat_rate": sat_rate, \
                "elapsed_time": elapsed_time_list
            })

    pprint.pprint(result_list)
    return result_list

def gen_result_pdf(result_list):
    elapsed_time_list_list = []
    sat_rate_list = []
    label_list = []
    for result in result_list:
        elapsed_time_list_list.append(result["elapsed_time"])
        sat_rate_list.append(result["sat_rate"])
        # label_list.append(result["num_sw"])
        label_list.append(result["num_flow_soft"])

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # plot
    bp = ax1.boxplot(elapsed_time_list_list, labels=label_list, patch_artist=True, \
        boxprops={'facecolor': 'lightblue'})
    p = ax2.plot(range(1, len(label_list)+1), sat_rate_list, marker=".", color='indianred')

    # set legend
    # cf. http://oregengo.hatenablog.com/entry/2016/09/17/193909
    ax1.legend([bp['boxes'][0], [p][0][0]], ['Calculation time', 'Success rate'], loc='upper right')
    pprint.pprint(bp)

    # set label
    # ax1.set_xlabel('Number of switches')
    ax1.set_xlabel('Number of soft real-time flows')
    ax1.set_ylabel('Calculation time [s]')
    ax2.set_ylabel('Success rate [%]')

    # shape layout
    plt.tight_layout()
    # make pdf
    make_pdf('time_and_rate_for_numSw.pdf')

def make_pdf(pdf_filename):
    pp = PdfPages(pdf_filename)
    pp.savefig()
    pp.close()
    plt.clf()

def main():
    result_list = \
        [{'elapsed_time': [0.27921271324157715,
                        0.2017974853515625,
                        0.021190643310546875,
                        0.07768511772155762,
                        0.1728525161743164,
                        0.22516489028930664,
                        0.41533327102661133,
                        0.03780078887939453,
                        0.18122339248657227,
                        0.19135832786560059],
        'num_flow': 5,
        'num_flow_hard': 2,
        'num_flow_soft': 3,
        'num_sw': 5,
        'sat_rate': 90.0},
        {'elapsed_time': [0.2687036991119385,
                        0.26427793502807617,
                        0.044158935546875,
                        0.6348710060119629,
                        0.36142635345458984,
                        0.04407072067260742,
                        0.16357994079589844,
                        0.6791188716888428,
                        0.12261819839477539,
                        0.04690432548522949],
        'num_flow': 6,
        'num_flow_hard': 3,
        'num_flow_soft': 3,
        'num_sw': 6,
        'sat_rate': 80.0}]
    result_list = gen_result_list()
    gen_result_pdf(result_list)


if __name__ == "__main__":
    main()
