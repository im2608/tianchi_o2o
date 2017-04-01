from global_var import *
import numpy as np
import datetime
from common import *
import logging
from nltk.tbl import feature
from lxml.html.builder import SAMP
from tkinter.constants import ON
from utils import *

# 该优惠券在商家领取与使用的次数, date diff 之和, 最大最小天数, discount rate, min charge
def feature_coupon_cnt(c_id, m_id, coupon_cnt_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    c_id = opt_tuple[1]
    discount_rate = opt_tuple[2]
    min_charge = opt_tuple[3]
    date_received = opt_tuple[4]
    date = opt_tuple[5]
    date_diff = opt_tuple[6]
    
    c_m_tuple = (c_id, m_id)
    if (c_m_tuple not in coupon_cnt_dict):
        coupon_cnt_dict[c_m_tuple] = dict()
        coupon_cnt_dict[c_m_tuple][ONLINE] = [0, 0, 0, 0, 0] # 领取/使用的次数, date diff 之和, 最大最小天数 
        coupon_cnt_dict[c_m_tuple][OFFLINE] = [0, 0, 0, 0, 0]
    
    if (date is None and date_received is not None and\
        date_received >= expected_date_tup[0] and date_received < expected_date_tup[1]):
        coupon_cnt_dict[c_m_tuple][on_off][0] += tuple_cnt # 领取

    if (date is not None and date_received is not None and \
        date >= expected_date_tup[0] and date < expected_date_tup[1]):
        coupon_cnt_dict[c_m_tuple][on_off][0] += tuple_cnt # 使用隐含了领取
        coupon_cnt_dict[c_m_tuple][on_off][1] += tuple_cnt # 使用
        
        coupon_cnt_dict[c_m_tuple][on_off][2] += date_diff * tuple_cnt
        if (coupon_cnt_dict[c_m_tuple][on_off][3] > date_diff):
            coupon_cnt_dict[c_m_tuple][on_off][3] = date_diff
        
        if (coupon_cnt_dict[c_m_tuple][on_off][4] < date_diff):
            coupon_cnt_dict[c_m_tuple][on_off][4] = date_diff

    return

def create_coupon_feature_values(expected_date_tup, samples):
    calculated_c_m_set = set()
    
    coupon_cnt_dict = dict()
    
    sample_cnt = len(samples)
    
    for index in range(sample_cnt):
        m_id = samples[index][1]
        c_id = samples[index][2]
        c_m_tuple = (c_id, m_id)
        
        if (c_m_tuple not in g_coupon_merchant_dict):
            continue

        if (c_m_tuple in calculated_c_m_set):
            continue
    
        for on_off, on_off_data in g_coupon_merchant_dict[c_m_tuple].items():
            for opt_tuple, tuple_cnt in on_off_data.items():
                feature_coupon_cnt(c_id, m_id, coupon_cnt_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off)
                
            calculated_c_m_set.add(c_m_tuple)
    
    return coupon_cnt_dict

def create_coupon_on_off_features(samples, on_off):   
    
    coupon_cnt_dict = g_feature_values["coupon_cnt_dict"]

    sample_cnt = len(samples)
    coupon_feature_mat = np.zeros((sample_cnt, 100))
    feature_index = 0
    for index in range(sample_cnt):
        m_id = samples[index][1]
        c_id = samples[index][2]
        c_m_tuple = (c_id, m_id)

        if (c_m_tuple not in g_coupon_merchant_dict):
            continue

        feature_index = 0
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][on_off][0]; feature_index += 1 # 领取次数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][on_off][1]; feature_index += 1 # 使用次数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][on_off][1]/ \
                                                  (coupon_cnt_dict[c_m_tuple][on_off][0] + 1); feature_index += 1 # 比例
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][on_off][2]/ \
                                                  (coupon_cnt_dict[c_m_tuple][on_off][1] + 1); feature_index += 1 # 领取到使用之间的平均天数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][on_off][3]; feature_index += 1 # 领取到使用之间的最大天数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][on_off][4]; feature_index += 1 # 领取到使用之间的最小天数      

        if (len(g_coupon_merchant_dict[c_m_tuple][on_off]) > 0):
            opt_tuple = list(g_coupon_merchant_dict[c_m_tuple][on_off].keys())[0]

            coupon_feature_mat[index, feature_index] = opt_tuple[2]; feature_index += 1   # discount_rate     
            coupon_feature_mat[index, feature_index] = opt_tuple[3]; feature_index += 1 # min_charge
  
    return coupon_feature_mat[:, 0 : feature_index]

# (action,   c_id, discount_rate, min_charge, date_received, date, date_diff)
# (distance, c_id, discount_rate, min_charge, date_received, date, date_diff)
def create_coupon_feature_matrix_ex(samples, on_off):
    
    if (on_off == BOTH):
        coupon_feature_mat = create_coupon_on_off_features(samples, ONLINE)
        coupon_feature_mat = create_coupon_on_off_features(samples, OFFLINE)
    else:
        coupon_feature_mat = create_coupon_on_off_features(samples, on_off)
    return coupon_feature_mat



# (action,   c_id, discount_rate, min_charge, date_received, date, date_diff)
# (distance, c_id, discount_rate, min_charge, date_received, date, date_diff)
def create_coupon_feature_matrix(samples, expected_date_tup):
    
    coupon_cnt_dict = create_coupon_feature_values(expected_date_tup, samples)

    sample_cnt = len(samples)
    coupon_feature_mat = np.zeros((sample_cnt, 100))
    feature_index = 0
    for index in range(sample_cnt):
        m_id = samples[index][1]
        c_id = samples[index][2]
        c_m_tuple = (c_id, m_id)
        
        if (c_m_tuple not in g_coupon_merchant_dict):
            continue

        feature_index = 0
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][ONLINE][0]; feature_index += 1 # 领取次数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][ONLINE][1]; feature_index += 1 # 使用次数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][ONLINE][1]/ \
                                                  (coupon_cnt_dict[c_m_tuple][ONLINE][0] + 1); feature_index += 1 # 比例
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][ONLINE][2]/ \
                                                  (coupon_cnt_dict[c_m_tuple][ONLINE][1] + 1); feature_index += 1 # 领取到使用之间的平均天数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][ONLINE][3]; feature_index += 1 # 领取到使用之间的最大天数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][ONLINE][4]; feature_index += 1 # 领取到使用之间的最小天数

        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][OFFLINE][0]; feature_index += 1 # 领取次数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][OFFLINE][1]; feature_index += 1 # 使用次数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][OFFLINE][1]/ \
                                                  (coupon_cnt_dict[c_m_tuple][OFFLINE][0] + 1); feature_index += 1 # 比例
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][OFFLINE][2]/ \
                                                  (coupon_cnt_dict[c_m_tuple][OFFLINE][1] + 1); feature_index += 1 # 领取到使用之间的平均天数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][OFFLINE][3]; feature_index += 1 # 领取到使用之间的最大天数
        coupon_feature_mat[index, feature_index] = coupon_cnt_dict[c_m_tuple][OFFLINE][4]; feature_index += 1 # 领取到使用之间的最小天数  
        
        if (len(g_coupon_merchant_dict[c_m_tuple][ONLINE]) > 0):
            opt_tuple = list(g_coupon_merchant_dict[c_m_tuple][ONLINE].keys())[0]
        else:
            opt_tuple = list(g_coupon_merchant_dict[c_m_tuple][OFFLINE].keys())[0]

        coupon_feature_mat[index, feature_index] = opt_tuple[2]; feature_index += 1   # discount_rate     
        coupon_feature_mat[index, feature_index] = opt_tuple[3]; feature_index += 1 # min_charge

        if (index % 10000 == 0):
            print("creating Coupon feature matrix, %d / %d handled\r"  % (index, sample_cnt), end="")

    print("%s coupon feature size is %d" % (getCurrentTime(), feature_index))
    return coupon_feature_mat[:, 0 : feature_index]