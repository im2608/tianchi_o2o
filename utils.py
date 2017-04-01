'''
Created on Mar 21, 2017

@author: Heng.Zhang
'''

import csv
from global_var import *
from common import *
from dateutil.relativedelta import relativedelta


ISOTIMEFORMAT="%Y-%m-%d %X"
def getCurrentTime():
    return time.strftime(ISOTIMEFORMAT, time.localtime())

def datetime2Str(date):
    return "%d%02d%02d" % (date.year, date.month, date.day)
 
# 滑动窗口, 每个窗口为6周， 用1，2，3，4周数据预测5，6周的行为
# 每次向后滑动 2 周, 每周以周日开始，周六结束
def create_slide_window():

    slide_windows = []

    # 源数据从20160101开始，不是一周对齐的，所以第一个窗口多加了几天
    train_win_start = datetime.datetime.strptime("20160101", "%Y%m%d")
    train_win_end = datetime.datetime.strptime("20160131", "%Y%m%d")

    fcst_win_start = datetime.datetime.strptime("20160131", "%Y%m%d") 
    fcst_win_end = fcst_win_start + relativedelta(weeks=2)

    slide_windows.append((train_win_start, train_win_end, fcst_win_start, fcst_win_end))
    
    train_win_start = datetime.datetime.strptime("20160117", "%Y%m%d")
    train_win_end = train_win_start + relativedelta(weeks=4)
    
    fcst_win_start = fcst_win_start+ relativedelta(weeks=2)        
    fcst_win_end = fcst_win_start + relativedelta(weeks=2)
    
    # 源数据中date_received只给到6-15号    
    last_std_win_end = datetime.datetime.strptime("20160522", "%Y%m%d")
    
    while train_win_end <= last_std_win_end:
        slide_windows.append((train_win_start, train_win_end, fcst_win_start, fcst_win_end))

        train_win_start = train_win_start + relativedelta(weeks=2)
        train_win_end = train_win_start + relativedelta(weeks=4)

        fcst_win_start = fcst_win_start+ relativedelta(weeks=2)        
        fcst_win_end = fcst_win_start + relativedelta(weeks=2)

    # 源数据中date_received只给到6-15号，所以最后一个窗口从 [5-22, 6-15), 预测为[6-15, 7-01)
    train_win_end = datetime.datetime.strptime("20160601", "%Y%m%d")
    fcst_win_start = datetime.datetime.strptime("20160601", "%Y%m%d")
    fcst_win_end = datetime.datetime.strptime("20160616", "%Y%m%d")
    slide_windows.append((train_win_start, train_win_end, fcst_win_start, fcst_win_end))

    return [slide_windows[0]]

if __name__ == '__main__':
    print("utils")