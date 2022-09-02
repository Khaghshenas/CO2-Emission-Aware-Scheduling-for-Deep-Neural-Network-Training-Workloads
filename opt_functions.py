"""
Created on Sun July 04 15:25:00 2021

@author: Kawsar
"""

"""
The SusRes_MBC function returns the optimal emission using suspend_resume and moving_between_clouds mechansims. 
suspend happens only after epoches.
"""

import pandas as pd
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt

def SusRes_MBC(average_power, average_time_per_epoch_sec, num_epochs, start_y, start_m, start_d):


    PUE = 1.58
    #  I decided to not use 1.58 but the code for CPU has it.
    
    #-------------------calculating runtime
    runtime = average_time_per_epoch_sec*num_epochs
    runtime = datetime.timedelta(seconds=runtime)
    
    #-------------------reading emission data 2018&2019
    emission_data_france_edited, emission_data_centralbrazil_edited, emission_data_germany_edited, emission_data_netherlands_edited, emission_data_m_germany_edited, emission_data_m_france_edited = read_emiss_data()
    
    #-------------------calculating base emissions
    france_emiss, centralbrazil_emiss, germany_emiss, netherlands_emiss, m_germany_emiss, m_france_emiss = calc_base_emiss(average_power, start_y, start_m, start_d, runtime, emission_data_france_edited, emission_data_centralbrazil_edited, emission_data_germany_edited, emission_data_netherlands_edited, emission_data_m_germany_edited, emission_data_m_france_edited)
 
    #-------------------creating emission data with freq = average_time_per_epoch_sec    
    emission_data_france_edited_epoch, emission_data_centralbrazil_edited_epoch = read_emiss_data_epoch(average_time_per_epoch_sec, start_y, start_m, start_d, runtime, 
                          emission_data_france_edited, emission_data_centralbrazil_edited)
    
    opt_emiss, real_job_completion_time, opt_emiss_data = calc_opt_emiss(average_time_per_epoch_sec, average_power, start_y, start_m, start_d, runtime,
                   num_epochs,
                   emission_data_france_edited, 
                   emission_data_centralbrazil_edited,
                   emission_data_france_edited_epoch,
                   emission_data_centralbrazil_edited_epoch)
 
 
    return(opt_emiss, france_emiss, centralbrazil_emiss, germany_emiss, netherlands_emiss, m_germany_emiss, m_france_emiss, real_job_completion_time, opt_emiss_data)


def calc_opt_emiss(average_time_per_epoch_sec, average_power, start_y, start_m, start_d, runtime,
                   num_epochs,
                   emission_data_france_edited, 
                   emission_data_centralbrazil_edited,
                   emission_data_france_edited_epoch,
                   emission_data_centralbrazil_edited_epoch):
    
    start_date = datetime.datetime(year=start_y, month=start_m, day=start_d, hour=0, minute=0, second=0)
    end_date = start_date + runtime*2
    #based on SLA for NAS model (jobs with runtime> one week)
    #end_date = start_date + runtime
    
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    #------------depend on the SLA. here = 2*min_runtime
    opt_emiss_data = emission_data_france_edited_epoch.loc[start_date_str:end_date_str].copy()
    opt_emiss_data['location'] = "-"
    
    
    
    for i in range(num_epochs*2+1):
    #based on SLA for NAS model (jobs with runtime> one week)
    #for i in range(num_epochs):          
        if (emission_data_france_edited_epoch.carbon_intensity_avg.iloc[i]<=emission_data_centralbrazil_edited_epoch.carbon_intensity_avg.iloc[i]):
            opt_emiss_data.carbon_intensity_avg.iloc[i] = emission_data_france_edited_epoch.carbon_intensity_avg.iloc[i]
            opt_emiss_data.location.iloc[i] = "france"
            
        else:
            opt_emiss_data.carbon_intensity_avg.iloc[i] = emission_data_centralbrazil_edited_epoch.carbon_intensity_avg.iloc[i]
            opt_emiss_data.location.iloc[i] = "centralbrazil"
    
    opt_emiss_data = opt_emiss_data.nsmallest(num_epochs, 'carbon_intensity_avg', keep='first')
    opt_emiss_data = opt_emiss_data.sort_index()
    

    opt_emiss = 0
    start = 0
    end=0
  
    for i in range(num_epochs):
        
        x = datetime.timedelta(seconds=average_time_per_epoch_sec)
        start_date_epoch = opt_emiss_data.index[i]
        end_date_epoch = start_date_epoch + x
    
        start_date_epoch_str = start_date_epoch.strftime("%Y-%m-%d %H:%M:%S")
        end_date_epoch_str = end_date_epoch.strftime("%Y-%m-%d %H:%M:%S")
        
        if(i==0):
            start = start_date_epoch
        elif(i==num_epochs-1):
            end = end_date_epoch
            
        
        if (opt_emiss_data.iloc[i].location=="france"):
            df = emission_data_france_edited.loc[start_date_epoch_str:end_date_epoch_str].copy()
            df['power'] = average_power
            df['emission'] = df.carbon_intensity_avg*df['power']
    
            em_i = df.emission[0:-1].sum()
            em_i = em_i/(1000*1000*60)  #kgCO2 eq/kwh. freqency is 1min, thats why we have to divide to 60
            #For jobs with epoch time=30 seconds
            #em_i = em_i/(1000*1000*120)  #kgCO2 eq/kwh.
            em_i = em_i * 2.20462 #lbs
            
            opt_emiss = opt_emiss + em_i
            
        else:
            df = emission_data_centralbrazil_edited.loc[start_date_epoch_str:end_date_epoch_str].copy()
            df['power'] = average_power
            df['emission'] = df.carbon_intensity_avg*df['power']
    
            em_i = df.emission[0:-1].sum()
            em_i = em_i/(1000*1000*60)  #kgCO2 eq/kwh. freqency is 1min, thats why we have to divide to 60
            #For jobs with epoch time=30 seconds
            #em_i = em_i/(1000*1000*120)  #kgCO2 eq/kwh.
            em_i = em_i * 2.20462 #lbs
            
            opt_emiss = opt_emiss + em_i

        #if(i==num_epochs-1):
         #   opt_emiss = opt_emiss + (df.emission[-1]*2.20462)/(1000*1000*60) # the last value must be calculated once at the end. Not required

    real_job_completion_time = end-start
        
    return(opt_emiss, real_job_completion_time, opt_emiss_data)

    
def read_emiss_data():
    
    emission_data_centralbrazil_edited = pd.read_csv("data/centralbrazil2018 - edited1.csv")
    #For NAS model
    #emission_data_centralbrazil_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/ten_years/centralbrazil2018 - edited1-tenyears.csv")
    emission_data_centralbrazil_edited.drop(emission_data_centralbrazil_edited.columns.difference(['datetime','carbon_intensity_avg']), 1, inplace=True)
    emission_data_centralbrazil_edited.rename(columns = {"datetime":"dt"}, inplace = True)
    emission_data_centralbrazil_edited.dt = pd.to_datetime(emission_data_centralbrazil_edited.dt, utc=True)
    emission_data_centralbrazil_edited = emission_data_centralbrazil_edited.set_index('dt').asfreq(freq='1min', method='ffill')
    #For jobs with epoch time=30 seconds
    #emission_data_centralbrazil_edited = emission_data_centralbrazil_edited.set_index('dt').asfreq(freq='30S', method='ffill')
    emission_data_centralbrazil_edited['dt'] = emission_data_centralbrazil_edited.index
    emission_data_centralbrazil_edited.dt = emission_data_centralbrazil_edited.dt.apply(lambda x: datetime.datetime.strftime(x, "%Y-%m-%d %H:%M:%S"))
    emission_data_centralbrazil_edited = emission_data_centralbrazil_edited.set_index('dt')
    emission_data_centralbrazil_edited.interpolate(inplace=True)
    
    
    emission_data_france_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/UniGroningen_FR_2018 - edited.csv")
    #For NAS model
    #emission_data_france_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/ten_years/UniGroningen_FR_2018 - edited-tenyears.csv")
    emission_data_france_edited.drop(emission_data_france_edited.columns.difference(['datetime','carbon_intensity_avg']), 1, inplace=True)
    emission_data_france_edited.rename(columns = {"datetime":"dt"}, inplace = True)
    emission_data_france_edited.dt = pd.to_datetime(emission_data_france_edited.dt, utc=True)
    emission_data_france_edited = emission_data_france_edited.set_index('dt').asfreq(freq='1min', method='ffill')
    #For jobs with epoch time=30 seconds
    #emission_data_france_edited = emission_data_france_edited.set_index('dt').asfreq(freq='30S', method='ffill')
    emission_data_france_edited['dt'] = emission_data_france_edited.index
    emission_data_france_edited.dt = emission_data_france_edited.dt.apply(lambda x: datetime.datetime.strftime(x, "%Y-%m-%d %H:%M:%S"))
    emission_data_france_edited = emission_data_france_edited.set_index('dt')
    emission_data_france_edited.interpolate(inplace=True)
    
    emission_data_germany_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/UniGroningen_DE_2018 - edited.csv")
    #For NAS model
    #emission_data_germany_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/ten_years/UniGroningen_DE_2018 - edited-tenyears.csv")
    emission_data_germany_edited.drop(emission_data_germany_edited.columns.difference(['datetime','carbon_intensity_avg']), 1, inplace=True)
    emission_data_germany_edited.rename(columns = {"datetime":"dt"}, inplace = True)
    emission_data_germany_edited.dt = pd.to_datetime(emission_data_germany_edited.dt, utc=True)
    emission_data_germany_edited = emission_data_germany_edited.set_index('dt').asfreq(freq='1min', method='ffill')
    #For jobs with epoch time=30 seconds
    #emission_data_germany_edited = emission_data_germany_edited.set_index('dt').asfreq(freq='30S', method='ffill')   
    emission_data_germany_edited['dt'] = emission_data_germany_edited.index
    emission_data_germany_edited.dt = emission_data_germany_edited.dt.apply(lambda x: datetime.datetime.strftime(x, "%Y-%m-%d %H:%M:%S"))
    emission_data_germany_edited = emission_data_germany_edited.set_index('dt')
    emission_data_germany_edited.interpolate(inplace=True)
    
    emission_data_netherlands_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/UniGroningen_NL_2018 - edited.csv")
    #For NAS model
    #emission_data_netherlands_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/ten_years/UniGroningen_NL_2018 - edited-tenyears.csv")
    emission_data_netherlands_edited.drop(emission_data_netherlands_edited.columns.difference(['datetime','carbon_intensity_avg']), 1, inplace=True)
    emission_data_netherlands_edited.rename(columns = {"datetime":"dt"}, inplace = True)
    emission_data_netherlands_edited.dt = pd.to_datetime(emission_data_netherlands_edited.dt, utc=True)
    emission_data_netherlands_edited = emission_data_netherlands_edited.set_index('dt').asfreq(freq='1min', method='ffill')
    #For jobs with epoch time=30 seconds
    #emission_data_netherlands_edited = emission_data_netherlands_edited.set_index('dt').asfreq(freq='30S', method='ffill')
    emission_data_netherlands_edited['dt'] = emission_data_netherlands_edited.index
    emission_data_netherlands_edited.dt = emission_data_netherlands_edited.dt.apply(lambda x: datetime.datetime.strftime(x, "%Y-%m-%d %H:%M:%S"))
    emission_data_netherlands_edited = emission_data_netherlands_edited.set_index('dt')
    emission_data_netherlands_edited.interpolate(inplace=True)
    
    emission_data_m_germany_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/UniGroningen_2018_DE_marginal_avg - edited.csv")
    #For NAS model
    #emission_data_m_germany_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/ten_years/UniGroningen_2018_DE_marginal_avg - edited-tenyears.csv")
    emission_data_m_germany_edited.rename(columns = {"marginal_carbon_intensity_avg":"carbon_intensity_avg"}, inplace = True)
    emission_data_m_germany_edited.rename(columns = {"datetime":"dt"}, inplace = True)
    emission_data_m_germany_edited.dt = pd.to_datetime(emission_data_m_germany_edited.dt, utc=True)
    emission_data_m_germany_edited = emission_data_m_germany_edited.set_index('dt').asfreq(freq='1min', method='ffill')
    #For jobs with epoch time=30 seconds
    #emission_data_m_germany_edited = emission_data_m_germany_edited.set_index('dt').asfreq(freq='30S', method='ffill')
    emission_data_m_germany_edited['dt'] = emission_data_m_germany_edited.index
    emission_data_m_germany_edited.dt = emission_data_m_germany_edited.dt.apply(lambda x: datetime.datetime.strftime(x, "%Y-%m-%d %H:%M:%S"))
    emission_data_m_germany_edited = emission_data_m_germany_edited.set_index('dt')
    emission_data_m_germany_edited.interpolate(inplace=True)
    
    emission_data_m_france_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/UniGroningen_2018_FR_marginal_avg - edited.csv")
    #For NAS model
    #emission_data_m_france_edited = pd.read_csv("data/Laura_drive-download-20210907T065325Z-001/ten_years/UniGroningen_2018_FR_marginal_avg - edited-tenyears.csv")
    emission_data_m_france_edited.rename(columns = {"marginal_carbon_intensity_avg":"carbon_intensity_avg"}, inplace = True)
    emission_data_m_france_edited.rename(columns = {"datetime":"dt"}, inplace = True)
    emission_data_m_france_edited.dt = pd.to_datetime(emission_data_m_france_edited.dt, utc=True)
    emission_data_m_france_edited = emission_data_m_france_edited.set_index('dt').asfreq(freq='1min', method='ffill')
    #For jobs with epoch time=30 seconds
    #emission_data_m_france_edited = emission_data_m_france_edited.set_index('dt').asfreq(freq='30S', method='ffill')
    emission_data_m_france_edited['dt'] = emission_data_m_france_edited.index
    emission_data_m_france_edited.dt = emission_data_m_france_edited.dt.apply(lambda x: datetime.datetime.strftime(x, "%Y-%m-%d %H:%M:%S"))
    emission_data_m_france_edited = emission_data_m_france_edited.set_index('dt')
    emission_data_m_france_edited.interpolate(inplace=True)
    
    
    return(emission_data_france_edited, emission_data_centralbrazil_edited, emission_data_germany_edited, emission_data_netherlands_edited, emission_data_m_germany_edited, emission_data_m_france_edited)
    
    
def read_emiss_data_epoch(average_time_per_epoch_sec, start_y, start_m, start_d, runtime, 
                          emission_data_france_edited, emission_data_centralbrazil_edited):
    
    ep_time = datetime.timedelta(seconds=average_time_per_epoch_sec)
    start_date = datetime.datetime(year=start_y, month=start_m, day=start_d, hour=0, minute=0, second=0)
    end_date = datetime.datetime(year=2019, month=12, day=30, hour=0, minute=0, second=0)
    #For NAS
    #end_date = datetime.datetime(year=2028, month=12, day=30, hour=0, minute=0, second=0)
    
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    emission_data_france_edited_epoch = emission_data_france_edited.loc[start_date_str:end_date_str].copy()
    emission_data_centralbrazil_edited_epoch = emission_data_centralbrazil_edited.loc[start_date_str:end_date_str].copy()
    
    emission_data_france_edited_epoch['dt'] = emission_data_france_edited_epoch.index
    emission_data_france_edited_epoch['dt'] = pd.to_datetime(emission_data_france_edited_epoch.dt, utc=True)
    emission_data_france_edited_epoch = emission_data_france_edited_epoch.set_index('dt')
    emission_data_france_edited_epoch = emission_data_france_edited_epoch.resample(ep_time).mean()
    
    emission_data_centralbrazil_edited_epoch['dt'] = emission_data_centralbrazil_edited_epoch.index
    emission_data_centralbrazil_edited_epoch['dt'] = pd.to_datetime(emission_data_centralbrazil_edited_epoch.dt, utc=True)
    emission_data_centralbrazil_edited_epoch = emission_data_centralbrazil_edited_epoch.set_index('dt')
    emission_data_centralbrazil_edited_epoch = emission_data_centralbrazil_edited_epoch.resample(ep_time).mean()
    
    
    
    return(emission_data_france_edited_epoch, emission_data_centralbrazil_edited_epoch)
    

def calc_base_emiss(average_power, start_y, start_m, start_d, runtime, em_data_france, em_data_centralbrazil, em_data_germany, em_data_netherlands, em_data_m_germany, em_data_m_france):
    
    start_date = datetime.datetime(year=start_y, month=start_m, day=start_d, hour=0, minute=0, second=0)
    end_date = start_date + runtime
    
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    
    df = em_data_france.loc[start_date_str:end_date_str].copy()
    df['power'] = average_power
    df['emission'] = df.carbon_intensity_avg*df['power']
    
    france_emiss = df.emission[0:-1].sum()
    france_emiss = france_emiss/(1000*1000*60)  #kgCO2 eq/kwh. freqency is 1min, thats why we have to divide to 60
    #For jobs with epoch time=30 seconds   
    #france_emiss = france_emiss/(1000*1000*120)  #kgCO2 eq/kwh. freqency is 30 seconds, thats why we have to divide to 120
    france_emiss = france_emiss * 2.20462 #lbs
    
    df1 = em_data_centralbrazil.loc[start_date_str:end_date_str].copy()
    df1['power'] = average_power
    df1['emission'] = df1.carbon_intensity_avg*df1['power']
    
    centralbrazil_emiss = df1.emission[0:-1].sum()
    centralbrazil_emiss = centralbrazil_emiss/(1000*1000*60)  #kgCO2 eq/kwh
    #For jobs with epoch time=30 seconds 
    #centralbrazil_emiss = centralbrazil_emiss/(1000*1000*120)  #kgCO2 eq/kwh
    centralbrazil_emiss = centralbrazil_emiss * 2.20462 #lbs
    
    
    df2 = em_data_germany.loc[start_date_str:end_date_str].copy()
    df2['power'] = average_power
    df2['emission'] = df2.carbon_intensity_avg*df2['power']
    
    germany_emiss = df2.emission[0:-1].sum()
    germany_emiss = germany_emiss/(1000*1000*60)  #kgCO2 eq/kwh
    #For jobs with epoch time=30 seconds 
    #germany_emiss = germany_emiss/(1000*1000*120)  #kgCO2 eq/kwh
    germany_emiss = germany_emiss * 2.20462 #lbs
    
    df3 = em_data_netherlands.loc[start_date_str:end_date_str].copy()
    df3['power'] = average_power
    df3['emission'] = df3.carbon_intensity_avg*df3['power']
    
    netherlands_emiss = df3.emission[0:-1].sum()
    netherlands_emiss = netherlands_emiss/(1000*1000*60)  #kgCO2 eq/kwh
    #For jobs with epoch time=30 seconds 
    #netherlands_emiss = netherlands_emiss/(1000*1000*120)  #kgCO2 eq/kwh
    netherlands_emiss = netherlands_emiss * 2.20462 #lbs
    
    df4 = em_data_m_germany.loc[start_date_str:end_date_str].copy()
    df4['power'] = average_power
    df4['emission'] = df4.carbon_intensity_avg*df4['power']
    
    m_germany_emiss = df4.emission[0:-1].sum()
    m_germany_emiss = m_germany_emiss/(1000*1000*60)  #kgCO2 eq/kwh
    #For jobs with epoch time=30 seconds 
    #m_germany_emiss = m_germany_emiss/(1000*1000*120)  #kgCO2 eq/kwh
    m_germany_emiss = m_germany_emiss * 2.20462 #lbs
    
    df5 = em_data_m_france.loc[start_date_str:end_date_str].copy()
    df5['power'] = average_power
    df5['emission'] = df5.carbon_intensity_avg*df5['power']
    
    m_france_emiss = df5.emission[0:-1].sum()
    m_france_emiss = m_france_emiss/(1000*1000*60)  #kgCO2 eq/kwh
    #For jobs with epoch time=30 seconds 
    #m_france_emiss = m_france_emiss/(1000*1000*120)  #kgCO2 eq/kwh
    m_france_emiss = m_france_emiss * 2.20462 #lbs
    
    return(france_emiss, centralbrazil_emiss, germany_emiss, netherlands_emiss, m_germany_emiss, m_france_emiss)
    

