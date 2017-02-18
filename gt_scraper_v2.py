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
import json
import urllib
from datetime import datetime, timedelta
import requests


def get_buckets(start_date, end_date):
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    bucket_limits = [start_date_dt]
    left_limit = start_date_dt
    while left_limit <= end_date_dt:
        new_limit = left_limit + timedelta(days=181)
        if new_limit < end_date_dt:
            bucket_limits.append(new_limit)
        left_limit = new_limit
    bucket_limits.append(end_date_dt)
    return bucket_limits

def get_data(bucket_start_date,bucket_end_date, keyword):
    bucket_start_date_printed = datetime.strftime(bucket_start_date, '%Y-%m-%d')
    bucket_end_date_printed = datetime.strftime(bucket_end_date, '%Y-%m-%d')
    time_formatted = bucket_start_date_printed + '+' + bucket_end_date_printed

    req = {"comparisonItem":[{"keyword":keyword, "geo":geo, "time": time_formatted}], "category":category,"property":""}
    hl = "en-GB"
    tz = "-120"

    explore_URL = 'https://trends.google.com/trends/api/explore?hl={0}&tz={1}&req={2}'.format(hl,tz,json.dumps(req).replace(' ','').replace('+',' '))
    return requests.get(explore_URL).text

def get_token(response_text):
    try:
        return response_text.split('token":"')[1].split('","')[0]
    except:
        return None

def get_csv_request(response_text):
    try:
        return response_text.split('"widgets":')[1].split(',"lineAnno')[0].split('"request":')[1]       
    except:
        return None

def get_csv(response_text):
    request = get_csv_request(response_text)
    token = get_token(response_text)

    csv = requests.get('https://www.google.com/trends/api/widgetdata/multiline/csv?req={0}&token={1}&tz=-120'.format(request,token))
    return csv.text.encode('utf8')

def parse_csv(csv_contents):
    lines = csv_contents.split('\n')
    df = pd.DataFrame(columns = ['date','value'])
    dates = []
    values = []
    # Delete top 3 lines
    for line in lines[3:-1]:
        try:
            dates.append(line.split(',')[0].replace(' ',''))
            values.append(line.split(',')[1].replace(' ',''))
        except:
            pass
    df['date'] = dates
    df['value'] = values
    return df   

def get_daily_frames(start_date, end_date, keyword):

    bucket_list = get_buckets(start_date, end_date)
    frames = []
    for i in range(0,len(bucket_list) - 1):
        resp_text = get_data(bucket_list[i], bucket_list[i+1], keyword)
        frames.append(parse_csv(get_csv(resp_text)))

    return frames

def get_weekly_frame(start_date, end_date, keyword):

    if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=180):
        print 'No need to stitch; your time interval is short enough. '
        return None
    else:
        resp_text = get_data(datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d'), keyword)
        return parse_csv(get_csv(resp_text))

def stitch_frames(daily_frames, weekly_frame):

    daily_frame = pd.concat(daily_frames, ignore_index = True)

    daily_frame.columns = ['Date', 'Daily_Volume']
    pd.to_datetime(daily_frame['Date'])
    
    weekly_frame.columns = ['Week_Start_Date', 'Weekly_Volume']
    daily_frame.index = daily_frame['Date']
    weekly_frame.index = weekly_frame['Week_Start_Date']

    bins = []

    for i in range(0,len(weekly_frame)):
        bins.append(pd.date_range(weekly_frame['Week_Start_Date'][i],periods=7,freq='d'))

    final_data = {}

    for i in range(0,len(bins)):
        week_start_date = datetime.strftime(bins[i][0],'%Y-%m-%d')
        for j in range(0,len(bins[i])):
            this_date = datetime.strftime(bins[i][j],'%Y-%m-%d')
            try:
                this_val = int(float(weekly_frame['Weekly_Volume'][week_start_date])*float(daily_frame['Daily_Volume'][this_date])/float(daily_frame['Daily_Volume'][week_start_date]))
                final_data[this_date] = this_val
            except:
                pass
    final_data_frame = DataFrame.from_dict(final_data,orient='index').sort()
    final_data_frame[0] = np.round(final_data_frame[0]/final_data_frame[0].max()*100,2)

    final_data_frame.columns=['Volume']
    final_data_frame.index.names = ['Date']

    final_data_frame.to_csv('{0}.csv'.format(keywords.replace('+','')), sep=',')


if __name__ == '__main__':

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    geo = ''
    category = 22
    keywords = '+'.join(sys.argv[3:])

    daily_frames = get_daily_frames(start_date, end_date, keywords)
    weekly_frame = get_weekly_frame(start_date, end_date, keywords)

    stitch_frames(daily_frames, weekly_frame)
