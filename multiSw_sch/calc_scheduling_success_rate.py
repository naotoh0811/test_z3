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
    for num_sw in range(2, 11):
        check_result_dic = {}
        check_result_dic["num_sw"] = num_sw
        check_result_dic["count"] = []
        max_num_flow = num_sw
        for num_flow in range(1, max_num_flow + 1):
            count_dic = {}
            cnt_sat = 0
            cnt_unsat = 0
            for i in range(100):
                sat_or_unsat = from_gen_network_to_sch(num_sw, num_flow)
                if sat_or_unsat == SAT:
                    cnt_sat += 1
                else:
                    cnt_unsat += 1

            count_dic["num_flow"] = num_flow
            count_dic["success_rate"] = float(cnt_sat / (cnt_sat + cnt_unsat)) * 100
            check_result_dic["count"].append(count_dic)

        check_result_dic_list.append(check_result_dic)

    print(check_result_dic_list)
    return check_result_dic_list

def plot_result(check_result_dic_list):
    for check_result_dic in check_result_dic_list:
        # rcParams['font.family'] = 'Times New Roman'
        rcParams['font.size'] = 20
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
        plt.tight_layout()

        pdf_filename = 'rate_result_{}.pdf'.format(num_sw)
        gen_pdf(pdf_filename)


def gen_pdf(filename):
    pp = PdfPages(filename)
    pp.savefig()
    pp.close()
    plt.clf()

def main():
    # check_result_dic_list = get_check_result_dic()
    check_result_dic_list = [{'count': [{'num_flow': 1, 'success_rate': 100.0}, {'num_flow': 2, 'success_rate': 100.0}], 'num_sw': 2}, {'count': [{'num_flow': 1, 'success_rate': 100.0}, {'num_flow': 2, 'success_rate': 93.0}, {'num_flow': 3, 'success_rate': 82.0}], 'num_sw': 3}, {'count': [{'num_flow': 1, 'success_rate': 100.0}, {'num_flow': 2, 'success_rate': 93.0}, {'num_flow': 3, 'success_rate': 76.0}, {'num_flow': 4, 'success_rate': 80.0}], 'num_sw': 4}, {'count': [{'num_flow': 1, 'success_rate': 100.0}, {'num_flow': 2, 'success_rate': 93.0}, {'num_flow': 3, 'success_rate': 77.0}, {'num_flow': 4, 'success_rate': 68.0}, {'num_flow': 5, 'success_rate': 59.0}], 'num_sw': 5}, {'count': [{'num_flow': 1, 'success_rate': 100.0}, {'num_flow': 2, 'success_rate': 96.0}, {'num_flow': 3, 'success_rate': 81.0}, {'num_flow': 4, 'success_rate': 65.0}, {'num_flow': 5, 'success_rate': 72.0}, {'num_flow': 6, 'success_rate': 59.0}], 'num_sw': 6}, {'count': [{'num_flow': 1, 'success_rate': 100.0}, {'num_flow': 2, 'success_rate': 91.0}, {'num_flow': 3, 'success_rate': 84.0}, {'num_flow': 4, 'success_rate': 67.0}, {'num_flow': 5, 'success_rate': 62.0}, {'num_flow': 6, 'success_rate': 55.00000000000001}, {'num_flow': 7, 'success_rate': 62.0}], 'num_sw': 7}, {'count': [{'num_flow': 1, 'success_rate': 100.0}, {'num_flow': 2, 'success_rate': 90.0}, {'num_flow': 3, 'success_rate': 79.0}, {'num_flow': 4, 'success_rate': 70.0}, {'num_flow': 5, 'success_rate': 61.0}, {'num_flow': 6, 'success_rate': 62.0}, {'num_flow': 7, 'success_rate': 52.0}, {'num_flow': 8, 'success_rate': 53.0}], 'num_sw': 8}, {'count': [{'num_flow': 1, 'success_rate': 100.0}, {'num_flow': 2, 'success_rate': 90.0}, {'num_flow': 3, 'success_rate': 87.0}, {'num_flow': 4, 'success_rate': 68.0}, {'num_flow': 5, 'success_rate': 56.00000000000001}, {'num_flow': 6, 'success_rate': 54.0}, {'num_flow': 7, 'success_rate': 46.0}, {'num_flow': 8, 'success_rate': 55.00000000000001}, {'num_flow': 9, 'success_rate': 49.0}], 'num_sw': 9}, {'count': [{'num_flow': 1, 'success_rate': 100.0}, {'num_flow': 2, 'success_rate': 91.0}, {'num_flow': 3, 'success_rate': 85.0}, {'num_flow': 4, 'success_rate': 77.0}, {'num_flow': 5, 'success_rate': 56.00000000000001}, {'num_flow': 6, 'success_rate': 49.0}, {'num_flow': 7, 'success_rate': 43.0}, {'num_flow': 8, 'success_rate': 48.0}, {'num_flow': 9, 'success_rate': 50.0}, {'num_flow': 10, 'success_rate': 40.0}], 'num_sw': 10}]
    plot_result(check_result_dic_list)

if __name__ == "__main__":
    main()