# coding: utf-8

__author__ = 'youngsterxyf'

import re
import subprocess
import time
import json
import argparse
import os
import hashlib

from matplotlib import pyplot as plt
from numpy import arange


class HttpLoad(object):
    
    def __init__(self, request_num=1000, url='', debug=False, other_configs=None):
        if url == '':
            raise Exception(u'请提供完整的目标URL！')
        
        self.url = url
        url_parts = url.split('/')
        if len(url_parts) < 4:
            raise Exception(u'URL: %s 不正确！' % (self.url,))
        self.path = '/' + '/'. join(url_parts[3:])
        self.url_md5 = hashlib.md5(self.url).hexdigest()
        
        # 一次ab命令的请求数
        self.request_num = request_num
        self.debug = debug
        
        self.other_configs = other_configs
        
        # 最小并发数
        self.currency_min = self.other_configs.get('currency_min', 50)
        # 并发数步进大小
        self.currency_interval = self.other_configs.get('currency_interval', 50)
        # 实际上是达不到这个上限的
        # 最大并发数
        self.currency_max = self.request_num
        
        # 两次执行ab命令的时间间隔，单位为秒
        self.task_interval = self.other_configs.get('task_interval', 20)
        
        self.load_results = []
    
    def __shoot(self):
        ab_currency_list = []
        for currency_item in xrange(self.currency_min, self.currency_max, self.currency_interval):
            ab_currency_list.append(currency_item)
        
        ab_command_pattern = 'ab -n %d -c %d %s'
        
        regex_pattern = re.compile(r'Requests per second:\s+(?P<req_ps>[\d.]+) \[#/sec\] \(mean\)')
        
        load_results = []
        
        for currency in ab_currency_list:
            ab_command = ab_command_pattern % (self.request_num, currency, self.url)
            print ab_command
            
            try:
                output = subprocess.check_output(ab_command, shell=True)
            except subprocess.CalledProcessError as err:
                print err
                output = ''
            
            match = regex_pattern.search(output)
            if not match:
                req_ps = 0
            else:
                print match.groupdict()
                req_ps = float(match.groupdict().get('req_ps', '0'))
            
            self.load_results.append({
                'currency': currency,
                'result': req_ps
            })
            time.sleep(self.task_interval)
    
    def __plot(self):
        if self.debug:
            data_file_name = 'data_%s_%d.json' % (self.url_md5, self.request_num)
            with open(data_file_name, 'w') as fh:
                json.dump(self.load_results, fh)
            print self.load_results
        xaxis = [one_result['currency'] for one_result in self.load_results]
        yaxis = [one_result['result'] for one_result in self.load_results]
        
        figure_opts = self.other_configs.get('figure', {})
        fig_title = figure_opts.get('title', 'HTTP Load')
        fig_size = tuple(figure_opts.get('size', [20, 10]))
        
        fig = plt.figure(figsize=fig_size)
        plt.title('%s (URL: %s, %d Requests)' % (fig_title, self.path, self.request_num))
        plt.ylabel('requests / s')
        plt.xlabel('concurrency')
        # 显示网格，颜色为红色
        plt.grid(color='r')
        # 设置横坐标的最小值和最大值
        plt.xlim(xaxis[0], xaxis[-1])
        # 设置横坐标的刻度
        plt.xticks(arange(self.currency_min, self.currency_max, self.currency_interval), tuple(xaxis))
        # 设置纵坐标的最小值最大值
        plt.ylim(0, max(yaxis) + 100)
        plt.plot(xaxis, yaxis, 'b*-', linewidth=2)
        # 绘制线上每个数据点所在纵坐标的值
        for index, y in enumerate(yaxis):
            plt.text(xaxis[index], y, str(int(y)))
        # 保存绘图结果
        fig.savefig('http_load_%s_%d.png' % (self.url_md5, self.request_num), dpi=fig.dpi)
    
    def run(self):
        self.__shoot()
        self.__plot()


def parse_arguments():
    parser = argparse.ArgumentParser(description='parse arguments')
    parser.add_argument('-c', action='store', dest='config', default='./config.json')
    parser.add_argument('-v', action='store_true', dest='debug', default=False)
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    target_config_file = arguments.config
    is_debug = arguments.debug
    
    if not os.path.isfile(target_config_file):
        raise Exception(u'找不到配置文件：%s' % (target_config_file,))
    
    with open(target_config_file) as fh:
        configs = json.load(fh)
    # request_num_list 请求数列表
    # target_url_list 待压测的URL列表
    # 组合任务数 = len(request_num_list) x len(target_url_list)
    request_num_list = configs.pop('request_num_list', None)
    target_url_list = configs.pop('target_url_list', None)
    if request_num_list is None or target_url_list is None:
        raise Exception(u'请添加必要的配置项：request_num_list、target_url_list')
    
    task_opts = [(tul, rnl) for tul in target_url_list for rnl in request_num_list]
    for url, request_num in task_opts:
        hl = HttpLoad(request_num = request_num, url=url, debug=is_debug, other_configs=configs)
        hl.run()


if __name__ == '__main__':
    main()
