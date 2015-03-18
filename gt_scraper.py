# -*- coding: utf-8 -*-
"""
gt_scraper.py
Created on Sun Nov 23 20:38:55 2014

@author: cboys
"""

import webbrowser
import time
import os
import shutil
import copy
import pandas as pd
import re
import csv
import numpy as np
from pandas import DataFrame
import sys

# We first need to download all the bimonthly data.
# Google usually returns daily data within a two month period, 
# but if there is not a lot of data for a quarter it will
# return weekly data. 

#keyword = "bread"

month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def ScrapeTwoMonths(keyword, year, startmonth):
    print 'Scraping '+month_list[startmonth-1]+' and '+month_list[startmonth]+' in '+str(year)
    URL_start = "http://www.google.com/trends/trendsReport?&q="
    URL_end = "&cmpt=q&content=1&export=1"
  
    queries = keyword[0]
    if len(keyword) > 1:
        queries_list = []
        for i in range(0,len(keyword)):
            queries_list.append(keyword[i])
        queries = '%20'.join(queries_list)
        
    date = '&date='+str(startmonth)+'%2F'+str(year)+'%202m'
    
    URL = URL_start+queries+date+URL_end

    webbrowser.open(URL)    
    
# ScrapeRange will download all files for the relevant months.
#
# WARNING: Before you run ScrapeRange, ensure your /Downloads folder
# does not contain any .csv files. 

def ScrapeRange(keyword, startmonth, startyear, endmonth, endyear):
            
    for i in range(startmonth,13,2):
        ScrapeTwoMonths(keyword,startyear,i)
        time.sleep(7)
    for y in range(startyear + 1, endyear):
        for i in range(1,11,2):
            ScrapeTwoMonths(keyword,y,i)
            time.sleep(7)
    for i in range(1,endmonth,2):
        ScrapeTwoMonths(keyword,endyear,i)
        time.sleep(7)
    
    files = copy.deepcopy(os.listdir(path))    
    
    for i in range(0,len(files)):
        if files[i].lower().endswith('.csv'):
            try:
                if files[i][-5] == ")":
                    oldname = path+'/'+files[i]
                    newname = path+'/report'+files[i][-6]+'.csv'
                    os.rename(oldname,newname)
            except OSError:
                pass

    quarterly_files = [fn for fn in os.listdir(path) if fn.lower().startswith('report')]
                                    
    for file in quarterly_files:
        shutil.move(path+"/"+file,path+'/'+scrapings_dir)

    full_path = path+'/'+scrapings_dir    
    newfiles = copy.deepcopy(os.listdir(full_path))

    for i in range(0,len(newfiles)):
        oldname = full_path+'/'+newfiles[i]
        if os.path.getsize(oldname) < 800:
            print 'File '+oldname+' is unusually small...'
        newname = full_path+'/'+str(os.path.getmtime(full_path+'/'+newfiles[i]))[:-2]+".csv"
        os.rename(oldname, newname)       



### move files from Downloads folder to /gt_keywords
### rename files (they can be distinguished by date modified)

### if a quarter only returns weekly data, pad out the weeks by steps:

    ## check weekly or not by filesize
    ## for weekly files:
        ## replce week ranges by week start dates
        ## insert six rows between each row, pad with intervening dates and copy values down
        ## overwrite files

### copy all these into a single daily list for the full date range

# download weekly data for full period

def ScrapeRangeWeekly(keyword, startmonth, startyear, endmonth, endyear):
    months = 11-startmonth + (endyear - startyear - 1)*12 + endmonth
    print 'Scraping weekly data from '+month_list[startmonth-1]+' '+str(startyear)+' to '+month_list[endmonth-1]+' '+str(endyear)
    
    URL_start = "http://www.google.com/trends/trendsReport?&q="
    URL_end = "&cmpt=q&content=1&export=1"
    
    queries = keyword[0]
    if len(keyword) > 1:
        queries_list = []
        for i in range(0,len(keyword)):
            queries_list.append(keyword[i])
        queries = '%20'.join(queries_list)

    date = '&date='+str(startmonth)+'%2F'+str(startyear)+'%20'+str(months)+'m'
    
    URL = URL_start+queries+date+URL_end
    
    webbrowser.open(URL)

    time.sleep(7)
    
    oldname = path+'/'+'report.csv'
    newname = path+'/'+'weekly_data.csv'
    os.rename(oldname,newname)

    shutil.move(newname,path+'/'+scrapings_dir)

def CreateDailyFrame():

    files = copy.deepcopy(os.listdir(path+'/'+scrapings_dir))[:-1]

    date_pattern = re.compile('\d\d\d\d-\d\d-\d\d')
    for i in range(0,len(files)):
        if files[i].lower().endswith('.csv'):
            oldname = path+'/'+scrapings_dir+'/'+files[i]
            newname = path+'/'+scrapings_dir+'/'+'bimonthly'+str(i)+'.csv'
            temp_file = csv.reader(open(oldname,'ru'))
            with open(newname,'wb') as write_to:
                write_data = csv.writer(write_to, delimiter=',')
                for row in temp_file:
                    if len(row)==2:
                        if re.search(date_pattern,row[0]) is not None:
                            write_data.writerows([row])
            os.remove(oldname)

    files = [fn for fn in copy.deepcopy(os.listdir(path+'/'+scrapings_dir))[:-1] if fn.lower().startswith('bimonthly')]

    frames_list = []

    for file in files:
        df = pd.read_csv(path+'/'+scrapings_dir+'/'+file,index_col=None,header=None)
        frames_list.append(df)

    frame = pd.concat(frames_list,ignore_index=True)
    return frame

def CreateWeeklyFrame():

    date_pattern = re.compile('\d\d\d\d-\d\d-\d\d\s-\s\d\d\d\d-\d\d-\d\d')

    oldname = path+'/'+scrapings_dir+'/'+'weekly_data.csv'
    newname = path+'/'+scrapings_dir+'/'+'weekly.csv'
    temp_file = csv.reader(open(oldname,'ru'))
    with open(newname,'wb') as write_to:
        write_data = csv.writer(write_to, delimiter=',')
        for row in temp_file:
            if len(row) == 2:
                if re.search(date_pattern,row[0]) is not None:
                    write_data.writerows([row])
    os.remove(oldname)

    frame = pd.read_csv(newname,index_col=None,header=None)
    return frame

def StitchFrames():

    daily_frame = CreateDailyFrame()
    interim_weekly_frame = CreateWeeklyFrame()

    daily_frame.columns = ['Date', 'Daily_Volume']
    pd.to_datetime(daily_frame['Date'])
    
    interim_weekly_frame.columns = ['Date_Range', 'Weekly_Volume']
    date_pattern = re.compile('\d\d\d\d-\d\d-\d\d')

    startdates = []
    enddates = []

    for i in range(0,len(interim_weekly_frame['Date_Range'])):
        startdates.append(re.findall(date_pattern,interim_weekly_frame['Date_Range'][i])[0])
        enddates.append(re.findall(date_pattern,interim_weekly_frame['Date_Range'][i])[1])

    weekly_frame = pd.DataFrame(data=[startdates,enddates,interim_weekly_frame['Weekly_Volume'].tolist()]).transpose()
    weekly_frame.columns = ['Start_Date', 'End_Date', 'Weekly_Volume']
    pd.to_datetime(weekly_frame['Start_Date'])
    pd.to_datetime(weekly_frame['End_Date'])

    bins = []

    for i in range(0,len(weekly_frame)):
        bins.append(pd.date_range(weekly_frame['Start_Date'][i],periods=7,freq='d'))

    weekly_frame = weekly_frame.set_index('Start_Date')

    daily_frame = daily_frame.set_index('Date')

    final_data = {}

    for i in range(0,len(bins)):
        for j in range(0,len(bins[i])):
            final_data[bins[i][j]] = weekly_frame['Weekly_Volume'][str(bins[i][0].date())]*daily_frame['Daily_Volume'][str(bins[i][j].date())]/daily_frame['Daily_Volume'][str(bins[i][0].date())]

    final_data_frame = DataFrame.from_dict(final_data,orient='index').sort()
    final_data_frame[0] = np.round(final_data_frame[0]/final_data_frame[0].max()*100)

    final_data_frame.columns=['Volume']
    final_data_frame.index.names = ['Date']

    final_name = path+'/'+scrapings_dir+'/'+'final_output.csv'

    final_data_frame.to_csv(final_name, sep=',')

## run as python gt_scraper.py startmonth startyear endmonth endyear keyword_list

if __name__ == '__main__':

    print sys.argv[0]

    startmonth = sys.argv[1]
    startyear = sys.argv[2]
    endmonth = sys.argv[3]
    endyear = sys.argv[4]
    keywords = sys.argv[5:]

    path = '/Users/clintonboys/Downloads'

    scrapings_dir = 'gt_{0}'.format(keywords[0])
    if not os.path.exists(path+"/"+scrapings_dir):
        os.makedirs(path+"/"+scrapings_dir)

    ScrapeRange(keywords, int(startmonth), int(startyear), int(endmonth), int(endyear))
    ScrapeRangeWeekly(keywords, int(startmonth), int(startyear), int(endmonth), int(endyear))

    StitchFrames()


