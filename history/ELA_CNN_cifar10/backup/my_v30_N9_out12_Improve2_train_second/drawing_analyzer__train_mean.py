# -*- encoding: utf-8 -*-
# author: mo weilong
import re
import matplotlib.pyplot as plt
from collections import OrderedDict

# str2float方法堆
from functools import reduce
def str2float(s):
  return reduce(lambda x,y:x+int2dec(y),map(str2int,s.split('.')))
def char2num(s):
  return{'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9}[s]
def str2int(s):
  return reduce(lambda x,y:x*10+y,map(char2num,s))
def intLen(i):
    return len('%d' % i)
def int2dec(i):
  return i/(10** intLen(i))
def str2float(s):
    return reduce(lambda x,y: x+int2dec(y),map(str2int,s.split('.')))

def get_parameters_list(path,re_dict={}):
	data_dict =OrderedDict()
	for key in re_dict.keys():
		with open(path, 'r') as fo:
			number_list= []
			for line in fo:
				pattern = re.compile(re_dict[key])
				res = pattern.findall(line)
				if res:
					number_list.append(str2float(res[0]))
		data_dict[key] =number_list
	return data_dict

def curve_smooth(data_list, batch_size=100):
	new_data_list, idx_list = [], []
	for i in range(int(len(data_list) / batch_size)):
		batch = data_list[i*batch_size: (i+1)*batch_size]
		new_data_list.append(1.0 * sum(batch) / len(batch))
		idx_list.append(i*batch_size)

	return new_data_list, idx_list

def plot_curvev_v2(x,y_datas_dict,y_datas_legend_dict = None,setting_dict={}):
    colors=['b','r','y','k','c','m','g','tan','tomato']
    line_styles= ['^--','+--','x--',':','o--','*--','s--','D--','.--']
    # plt.switch_backend('agg')
    plt.title(setting_dict['title'])
    plt.xlabel(setting_dict['xlabel'])
    plt.ylabel(setting_dict['ylabel'])
    p_legend = []
    p_legend_name = []
    y_datas_keys = y_datas_dict.keys()
    for idx,y_datas_key in enumerate(y_datas_keys):
        y_data_dict = y_datas_dict[y_datas_key]
        p, =plt.plot(x, y_data_dict, line_styles[idx], color=colors[idx])
        p_legend.append(p)
        if y_datas_legend_dict is not None:
            p_legend_name.append(y_datas_legend_dict[y_datas_key])

    if p_legend_name is not None:
        plt.legend(p_legend, p_legend_name,loc='lower right')

    plt.grid()
    plt.savefig(setting_dict['save_name'], dpi=100, format='png')
    plt.show()

import numpy as np
def add_two_list(list_1,list_2):
    array_1 = np.array(list_1)
    array_2 = np.array(list_2)
    array_3 = array_1 + array_2
    return array_3
if __name__ =='__main__':
    file_path = 'train_log.txt'
    # file_path_1 = 'train_N1_log.txt'

    # 从文件中正则re获取全部y轴的值
    #file_path_1    acc_decision_batch_hv12
    y_re_dict_1 = OrderedDict()
    y_re_dict_1['net1']=r'net1: ([\d\.]+)'
    y_re_dict_1['net2']=r'net2: ([\d\.]+)'
    y_re_dict_1['net3']=r'net3: ([\d\.]+)'
    y_re_dict_1['net1_1']=r'net1_1: ([\d\.]+)'
    y_re_dict_1['net1_2']=r'net1_2: ([\d\.]+)'
    y_re_dict_1['net1_3']=r'net1_3: ([\d\.]+)'
    y_re_dict_1['net2_1']=r'net2_1: ([\d\.]+)'
    y_re_dict_1['net2_2']=r'net2_2: ([\d\.]+)'
    y_re_dict_1['net2_3']=r'net2_3: ([\d\.]+)'
    y_re_dict_1['net3_1']=r'net3_1: ([\d\.]+)'
    y_re_dict_1['net3_2']=r'net3_2: ([\d\.]+)'
    y_re_dict_1['net3_3']=r'net3_3: ([\d\.]+)'
    # y_re_dict_1['acc_decision_batch_hv2_list']=r'acc_decision_batch_hv2: ([\d\.]+)'
    y_re_dict_1['acc_decision_batch_hv4_list']=r'acc_decision_batch_hv4: ([\d\.]+)'
    y_re_dict_1['acc_decision_batch_hv6_list']=r'acc_decision_batch_hv6: ([\d\.]+)'
    y_re_dict_1['acc_decision_batch_hv8_list']=r'acc_decision_batch_hv8: ([\d\.]+)'
    y_re_dict_1['acc_decision_batch_hv10_list']=r'acc_decision_batch_hv10: ([\d\.]+)'
    y_re_dict_1['acc_decision_batch_hv12_list']=r'acc_decision_batch_hv12: ([\d\.]+)'
    # y_re_dict_1['decision_prediction_list']=r'decision_prediction: ([\d\.]+)'
    y_datas_dict_1 = get_parameters_list(path = file_path ,re_dict= y_re_dict_1)

    # from collections import namedtuple
    # namedtuple('get_mean_object',)
    # numeobject()
    list_names = ('net1','net2','net3','net1_1','net1_2','net1_3','net2_1','net2_2','net2_3',
     'net3_1','net3_2','net3_3')
    sum = 0
    for list_name in list_names:
        sum= add_two_list(sum,y_datas_dict_1[list_name])
        y_datas_dict_1.pop(list_name)   #删除没用的键和值

    mean_value = sum / 12.0
    mean_value_list = mean_value.tolist()
    y_datas_dict_1['mean_value_list'] = mean_value_list
    #file_path_2
    # y_re_dict_2 = OrderedDict()
    # y_re_dict_2['net_N1_list'] = r'net1: ([\d\.]+)'
    # y_datas_dict_2 = get_parameters_list(path = file_path_1 ,re_dict= y_re_dict_2)

    #两个顺序字典合并
    y_datas_dict = OrderedDict()
    y_datas_dict.update(y_datas_dict_1)
    # y_datas_dict.update(y_datas_dict_2)

    #从文件中正则re获取全部x轴的值
    x_re_dict = OrderedDict()
    x_re_dict['epoch_list']=r'epoch: ([\d]+)'
    x_re_dict['global_step_list']=r'global_step: ([\d]+)'
    x_datas_dict = get_parameters_list(path = file_path ,re_dict= x_re_dict)

    #画图显示legend的名字
    y_datas_legend_dict =OrderedDict()
    # y_datas_legend_dict['net1_list']="N3_net1"
    # y_datas_legend_dict['net2_list']="N3_net2"
    # y_datas_legend_dict['net3_list']="N3_net3"
    # y_datas_legend_dict['acc_decision_batch_hv2_list']="acc_decision_batch_hv2"
    y_datas_legend_dict['mean_value_list']="avg_12_predict"
    y_datas_legend_dict['acc_decision_batch_hv4_list']="acc_hv4"
    y_datas_legend_dict['acc_decision_batch_hv6_list']="acc_hv6"
    y_datas_legend_dict['acc_decision_batch_hv8_list']="acc_hv8"
    y_datas_legend_dict['acc_decision_batch_hv10_list']="acc_hv10"
    y_datas_legend_dict['acc_decision_batch_hv12_list']="acc_hv12"
    # y_datas_legend_dict['decision_prediction_list']="N3_final_predict"
    # y_datas_legend_dict['net_N1_list']="N1"

    #标题、x轴、y轴显示信息
    setting_dict = OrderedDict()
    setting_dict['title'] = 'ELA-DCNN classification precision'
    setting_dict['xlabel'] = 'epoch'
    setting_dict['ylabel'] = 'accuracy'
    setting_dict['save_name'] ='cifar10_compare5.png'

    #传入字典参数并画图
    plot_curvev_v2(x_datas_dict['epoch_list'],y_datas_dict,y_datas_legend_dict,setting_dict)




