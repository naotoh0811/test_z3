import sys
import os.path
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rcParams
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import network.network.gen_linear_network as gen_linear_network
import network.flow.gen_flow_using_network_csv as gen_flow_using_network_csv
import network.dijkstra.gen_flowData as gen_flowData
import multiSw_sch.sch as sch

NOT_DEFINE = 1000
UNSAT = 1
SAT = 0

def from_gen_network_to_sch(num_sw, num_flow):
    gen_linear_network.main(num_sw)
    gen_flow_using_network_csv.main(num_flow)
    gen_flowData.main()
    sat_or_unsat = sch.main()

    return sat_or_unsat

def get_check_result_dic():
    check_result_dic_list = []
    for num_sw in range(2, 6):
        check_result_dic = {}
        check_result_dic["num_sw"] = num_sw
        check_result_dic["count"] = []
        max_num_flow = num_sw
        for num_flow in range(1, max_num_flow + 1):
            count_dic = {}
            cnt_sat = 0
            cnt_unsat = 0
            for i in range(10):
                sat_or_unsat = from_gen_network_to_sch(num_sw, num_flow)
                if sat_or_unsat == SAT:
                    cnt_sat += 1
                else:
                    cnt_unsat += 1

            count_dic["num_flow"] = num_flow
            count_dic["success_rate"] = float(cnt_sat / (cnt_sat + cnt_unsat))
            check_result_dic["count"].append(count_dic)

        check_result_dic_list.append(check_result_dic)

    print(check_result_dic_list)
    return check_result_dic_list

def plot_result(check_result_dic_list):
    for check_result_dic in check_result_dic_list:
        # ax.rcParams['font.family'] = 'Times New Roman'
        fig = plt.figure()
        ax = fig.add_subplot(111, xmargin=0.2)
        ax.set_xlabel('Number of flows')
        ax.set_ylabel('Success rate [%]')

        num_sw = check_result_dic["num_sw"]

        numFlow_list = []
        rate_list = []
        for each_count in check_result_dic["count"]:
            num_flow = each_count["num_flow"]
            rate = each_count["success_rate"]
            numFlow_list.append(num_flow)
            rate_list.append(rate)

        ax.bar(numFlow_list, rate_list, align='center', width=0.3, tick_label=numFlow_list)

        pdf_filename = 'rate_result_{}.pdf'.format(num_sw)
        gen_pdf(pdf_filename)


def gen_pdf(filename):
    pp = PdfPages(filename)
    pp.savefig()
    pp.close()
    plt.clf()

def main():
    # check_result_dic_list = get_check_result_dic()
    check_result_dic_list = [{'num_sw': 2, 'count': [{'num_flow': 1, 'success_rate': 1.0}, {'num_flow': 2, 'success_rate': 1.0}]}, {'num_sw': 3, 'count': [{'num_flow': 1, 'success_rate': 1.0}, {'num_flow': 2, 'success_rate': 1.0}, {'num_flow': 3, 'success_rate': 0.5}]}, {'num_sw': 4, 'count': [{'num_flow': 1, 'success_rate': 1.0}, {'num_flow': 2, 'success_rate': 0.8}, {'num_flow': 3, 'success_rate': 0.8}, {'num_flow': 4, 'success_rate': 0.9}]}, {'num_sw': 5, 'count': [{'num_flow': 1, 'success_rate': 1.0}, {'num_flow': 2, 'success_rate': 1.0}, {'num_flow': 3, 'success_rate': 0.8}, {'num_flow': 4, 'success_rate': 0.6}, {'num_flow': 5, 'success_rate': 0.7}]}]
    plot_result(check_result_dic_list)

if __name__ == "__main__":
    main()