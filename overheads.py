"""
Created on Mon January 03 18:42:00 2022

@author: Kawsar
"""

"""
The calc_overhead function returns the number of suspend_resume and moving_between_clouds mechanisms and total delay overhead with SR&MBC. 
"""

import pandas as pd
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt

def calc_overhead(opt_emiss_data, delay_of_SR, delay_of_MBC, average_time_per_epoch_sec):

    
    number_of_SR = calc_number_of_SR(opt_emiss_data, average_time_per_epoch_sec)
    
    number_of_MBC = calc_number_of_MBC(opt_emiss_data)
    
    total_delay_overhead = number_of_SR*delay_of_SR + number_of_MBC*delay_of_MBC
 
    return(number_of_SR, number_of_MBC, total_delay_overhead)


def calc_number_of_SR(opt_emiss_data, average_time_per_epoch_sec):
    
    n_sr = 0 
    
    opt_emiss_data.dt = pd.to_datetime(opt_emiss_data.dt, utc=True)
    
    df = opt_emiss_data.copy()
    df.sort_values(by=['dt'], inplace=True)

    epo_time = datetime.timedelta(seconds=average_time_per_epoch_sec)
    
    for i in range(opt_emiss_data.shape[0]-1):
        if(((opt_emiss_data.dt.iloc[i] + epo_time) != opt_emiss_data.dt.iloc[i+1]) and (opt_emiss_data.location.iloc[i] == opt_emiss_data.location.iloc[i+1])):
            n_sr = n_sr + 1
        else:
            n_sr = n_sr

    
    
    return (n_sr)

def calc_number_of_MBC(opt_emiss_data):
    
    n_mbc = 0
    for i in range(opt_emiss_data.shape[0]-1):
        if(opt_emiss_data.location.iloc[i] == opt_emiss_data.location.iloc[i+1]):
            n_mbc = n_mbc
        else:
            n_mbc = n_mbc + 1
            
    
    return (n_mbc)
